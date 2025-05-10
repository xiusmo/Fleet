import asyncio
import json
from enum import Enum
from types import TracebackType
from typing import Any, Callable, Dict, List, Optional, Type, Union, TypeVar, cast

import httpx
from fastapi import Depends
import orjson
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.session import get_db
from shared.models.log import LogCategory, LogLevel
from shared.utils.logger import DBLogger, get_logger


# 类型定义
T = TypeVar("T")
RequestHook = Callable[[httpx.Request], httpx.Request]
ResponseHook = Callable[[httpx.Response], httpx.Response]
RetryPredicate = Callable[[httpx.Response], bool]


class HttpMethod(str, Enum):
    """HTTP方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HttpLogLevel(str, Enum):
    """HTTP日志级别选项"""
    NONE = "none"  # 不记录日志
    BASIC = "basic"  # 仅记录基本信息（URL、状态码、耗时）
    HEADERS = "headers"  # 记录基本信息和请求/响应头
    BODY = "body"  # 记录所有信息，包括请求/响应体


class AsyncHttpClient:
    """异步HTTP客户端封装"""
    
    def __init__(
        self,
        base_url: str = "",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 0.5,
        retry_backoff: float = 1.5,
        logger: Optional[DBLogger] = None,
        db: Optional[AsyncSession] = None,
        log_level: HttpLogLevel = HttpLogLevel.BASIC,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
        http2: bool = False,
    ):
        """
        初始化HTTP客户端
        
        Args:
            base_url: 基础URL，所有请求都会基于此URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 初始重试延迟（秒）
            retry_backoff: 重试延迟的指数增长因子
            logger: 日志工具实例
            db: 数据库会话（如果没有提供logger）
            log_level: HTTP日志详细程度
            headers: 默认请求头
            cookies: 默认Cookie
            follow_redirects: 是否自动跟随重定向
            http2: 是否启用HTTP/2
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.logger = logger
        self.db = db
        self.log_level = log_level
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.follow_redirects = follow_redirects
        self.http2 = http2
        
        # 拦截器集合
        self.request_hooks: List[RequestHook] = []
        self.response_hooks: List[ResponseHook] = []
        
        # 重试条件
        self.retry_on_status_codes = [500, 502, 503, 504]
        self.retry_predicates: List[RetryPredicate] = []
        
        # 客户端实例
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "AsyncHttpClient":
        """异步上下文管理器入口"""
        if not self.client:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.headers,
                cookies=self.cookies,
                follow_redirects=self.follow_redirects,
                http2=self.http2
            )
        return self
    
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """异步上下文管理器退出"""
        if self.client:
            await self.client.aclose()
            self.client = None
    
    def add_request_hook(self, hook: RequestHook) -> None:
        """添加请求拦截器"""
        self.request_hooks.append(hook)
    
    def add_response_hook(self, hook: ResponseHook) -> None:
        """添加响应拦截器"""
        self.response_hooks.append(hook)
    
    def add_retry_predicate(self, predicate: RetryPredicate) -> None:
        """添加自定义重试条件"""
        self.retry_predicates.append(predicate)
    
    def _apply_request_hooks(self, request: httpx.Request) -> httpx.Request:
        """应用所有请求拦截器"""
        for hook in self.request_hooks:
            request = hook(request)
        return request
    
    def _apply_response_hooks(self, response: httpx.Response) -> httpx.Response:
        """应用所有响应拦截器"""
        for hook in self.response_hooks:
            response = hook(response)
        return response
    
    def _should_retry(self, response: httpx.Response, attempt: int) -> bool:
        """判断是否应该重试请求"""
        # 如果已经达到最大重试次数，不再重试
        if attempt >= self.max_retries:
            return False
        
        # 检查状态码
        if response.status_code in self.retry_on_status_codes:
            return True
        
        # 执行自定义重试条件
        for predicate in self.retry_predicates:
            if predicate(response):
                return True
        
        return False
    
    async def _log_request(
        self, 
        method: str, 
        url: str, 
        headers: Dict[str, str], 
        data: Any = None
    ) -> None:
        """记录请求日志"""
        if self.log_level == HttpLogLevel.NONE or not self.logger:
            return
        
        log_message = f"HTTP请求: {method} {url}"
        details: Dict[str, Any] = {}
        
        if self.log_level in [HttpLogLevel.HEADERS, HttpLogLevel.BODY]:
            details["headers"] = dict(headers)
        
        if self.log_level == HttpLogLevel.BODY and data:
            try:
                # 尝试将请求体作为JSON或字符串记录
                if isinstance(data, bytes):
                    details["body"] = data.decode("utf-8")
                elif isinstance(data, dict):
                    details["body"] = data
                else:
                    details["body"] = str(data)
            except Exception:
                details["body"] = "<无法序列化的请求体>"
        
        await self.logger.debug(
            message=log_message,
            category=LogCategory.API,
            details=details
        )
    
    async def _log_response(
        self, 
        method: str, 
        url: str, 
        status_code: int, 
        elapsed: float, 
        headers: Dict[str, str], 
        body: Any = None
    ) -> None:
        """记录响应日志"""
        if self.log_level == HttpLogLevel.NONE or not self.logger:
            return
        
        # 根据状态码选择日志级别
        log_level = LogLevel.INFO
        if status_code >= 400:
            log_level = LogLevel.WARNING
        if status_code >= 500:
            log_level = LogLevel.ERROR
        
        log_message = f"HTTP响应: {method} {url} - 状态码: {status_code}, 耗时: {elapsed:.3f}s"
        details: Dict[str, Any] = {
            "status_code": status_code,
            "elapsed_seconds": elapsed
        }
        
        if self.log_level in [HttpLogLevel.HEADERS, HttpLogLevel.BODY]:
            details["headers"] = dict(headers)
        
        if self.log_level == HttpLogLevel.BODY and body is not None:
            try:
                # 尝试将响应体解析为JSON或保存为字符串
                if isinstance(body, bytes):
                    body_str = body.decode("utf-8")
                    try:
                        details["body"] = json.loads(body_str)
                    except json.JSONDecodeError:
                        details["body"] = body_str
                elif isinstance(body, dict):
                    details["body"] = body
                else:
                    details["body"] = str(body)
            except Exception:
                details["body"] = "<无法序列化的响应体>"
        
        await self.logger.log(
            message=log_message,
            level=log_level,
            category=LogCategory.API,
            details=details
        )
    
    async def request(
        self,
        method: Union[str, HttpMethod],
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Any = None,
        json: Any = None,
        headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        follow_redirects: Optional[bool] = None,
        ignore_retries: bool = False,
        raise_for_status: bool = True
    ) -> httpx.Response:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            params: URL查询参数
            data: 请求体数据
            json: JSON请求体
            headers: 请求头
            cookies: 请求Cookie
            timeout: 超时时间（秒）
            follow_redirects: 是否跟随重定向
            ignore_retries: 是否忽略重试配置
            raise_for_status: 是否在响应状态错误时抛出异常
            
        Returns:
            httpx.Response: HTTP响应对象
        """
        if isinstance(method, HttpMethod):
            method = method.value
        
        # 确保客户端已初始化
        if not self.client:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=timeout or self.timeout,
                headers=self.headers,
                cookies=self.cookies,
                follow_redirects=follow_redirects if follow_redirects is not None else self.follow_redirects,
                http2=self.http2
            )
        
        # 合并请求头和Cookie
        merged_headers = {**self.headers, **(headers or {})}
        merged_cookies = {**self.cookies, **(cookies or {})}
        
        merged_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

        # 记录请求日志
        if self.logger:
            await self._log_request(
                method=method,
                url=str(httpx.URL(url, params=params)),
                headers=merged_headers,
                data=json if json is not None else data
            )
        
        if isinstance(json, BaseModel):
            json = json.model_dump(by_alias=False)

        if json is not None:
            # 用 orjson 编码 json 字典为字节流
            data = orjson.dumps(json)
            json = None
            headers = headers or {}
            headers["Content-Type"] = "application/json"
        
        # 创建请求对象
        request = self.client.build_request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=merged_headers,
            cookies=merged_cookies,
            timeout=timeout
        )
        
        # 应用请求拦截器
        request = self._apply_request_hooks(request)
        
        response = None
        attempt = 0
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                response = await self.client.send(request)
                
                # 应用响应拦截器
                response = self._apply_response_hooks(response)
                
                # 特殊处理422错误
                if response.status_code == 422 and self.logger:
                    await self.logger.error(
                        f"422 Validation Error: {response.text}",
                        category=LogCategory.API,
                        details={
                            "status_code": response.status_code,
                            "method": method,
                            "url": url,
                            "response": response.json() if response.json() else response.text if response.text else response.content
                        }
                    )
                    # 如果不需要重试422错误，直接返回
                    if ignore_retries:
                        break
                
                # 判断是否需要重试
                if (
                    not ignore_retries
                    and response is not None
                    and self._should_retry(response, attempt)
                ):
                    attempt += 1
                    delay = self.retry_delay * (self.retry_backoff ** (attempt - 1))
                    
                    if self.logger:
                        await self.logger.warning(
                            f"HTTP请求失败，正在重试({attempt}/{self.max_retries}): {method} {url}",
                            category=LogCategory.API,
                            details={
                                "status_code": response.status_code,
                                "retry_attempt": attempt,
                                "retry_delay": delay
                            }
                        )
                    
                    await asyncio.sleep(delay)
                    continue
                
                break
            except httpx.RequestError as e:
                # 处理请求异常
                if not ignore_retries and attempt < self.max_retries:
                    attempt += 1
                    delay = self.retry_delay * (self.retry_backoff ** (attempt - 1))
                    
                    if self.logger:
                        await self.logger.error(
                            f"HTTP请求错误，正在重试({attempt}/{self.max_retries}): {method} {url}",
                            category=LogCategory.API,
                            details={
                                "error": str(e),
                                "retry_attempt": attempt,
                                "retry_delay": delay
                            }
                        )
                    
                    await asyncio.sleep(delay)
                    continue
                else:
                    # 已达到最大重试次数，记录错误并重新抛出异常
                    if self.logger:
                        await self.logger.exception(
                            exc=e,
                            message=f"HTTP请求失败: {method} {url}",
                            category=LogCategory.API
                        )
                    raise
        
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # 记录响应日志
        if self.logger and response:
            await self._log_response(
                method=method,
                url=str(response.url),
                status_code=response.status_code,
                elapsed=elapsed,
                headers=dict(response.headers),
                body=response.content
            )
        
        # 如果需要，检查响应状态
        if raise_for_status and response:
            response.raise_for_status()
        
        return response
    
    async def get(
        self, url: str, *, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> httpx.Response:
        """发送GET请求"""
        return await self.request(HttpMethod.GET, url, params=params, **kwargs)
    
    async def post(
        self, url: str, *, data: Any = None, json: Any = None, **kwargs: Any
    ) -> httpx.Response:
        """发送POST请求"""
        return await self.request(HttpMethod.POST, url, data=data, json=json, **kwargs)
    
    async def put(
        self, url: str, *, data: Any = None, json: Any = None, **kwargs: Any
    ) -> httpx.Response:
        """发送PUT请求"""
        return await self.request(HttpMethod.PUT, url, data=data, json=json, **kwargs)
    
    async def delete(
        self, url: str, *, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> httpx.Response:
        """发送DELETE请求"""
        return await self.request(HttpMethod.DELETE, url, params=params, **kwargs)
    
    async def patch(
        self, url: str, *, data: Any = None, json: Any = None, **kwargs: Any
    ) -> httpx.Response:
        """发送PATCH请求"""
        return await self.request(HttpMethod.PATCH, url, data=data, json=json, **kwargs)
    
    async def head(
        self, url: str, *, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> httpx.Response:
        """发送HEAD请求"""
        return await self.request(HttpMethod.HEAD, url, params=params, **kwargs)
    
    async def options(
        self, url: str, *, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> httpx.Response:
        """发送OPTIONS请求"""
        return await self.request(HttpMethod.OPTIONS, url, params=params, **kwargs)
    
    async def get_json(
        self, url: str, *, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Any:
        """发送GET请求并返回JSON响应"""
        response = await self.get(url, params=params, **kwargs)
        return response.json()
    
    async def post_json(
        self, url: str, *, data: Any = None, json: Any = None, **kwargs: Any
    ) -> Any:
        """发送POST请求并返回JSON响应"""
        response = await self.post(url, data=data, json=json, **kwargs)
        return response.json()


def get_http_client(
    db: AsyncSession = Depends(get_db),
    logger: DBLogger = Depends(get_logger),
    base_url: str = "",
    timeout: float = 30.0,
    log_level: HttpLogLevel = HttpLogLevel.BASIC
) -> AsyncHttpClient:
    """
    FastAPI依赖项，用于获取HTTP客户端实例
    
    用法示例:
    ```python
    @router.get("/external-data")
    async def get_external_data(http: AsyncHttpClient = Depends(get_http_client)):
        response = await http.get("https://api.example.com/data")
        return response.json()
    ```
    """
    return AsyncHttpClient(
        base_url=base_url,
        timeout=timeout,
        logger=logger,
        db=db,
        log_level=log_level
    ) 