from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security import verify_fleet_jwt

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_prefix="/api/v1/abracadabra", expected_audience="fleet"):
        super().__init__(app)
        self.protected_prefix = protected_prefix
        self.expected_audience = expected_audience

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # 跳过公钥注册和分发，用 Bootstrap Token 保护它们
        if path == f"{self.protected_prefix}/register-key" or path.startswith(f"{self.protected_prefix}/public-key"):
            return await call_next(request)

        # 其它 /api/v1/abracadabra/* 路由依然走 JWT 校验
        if path.startswith(self.protected_prefix):
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
            token_str = token[7:]  # Remove 'Bearer '

            try:
                payload = verify_fleet_jwt(token_str, expected_audience=self.expected_audience)
                request.state.jwt_payload = payload
                request.state.jwt_issuer = payload.get("iss")
                request.state.jwt_jti = payload.get("jti")
            except Exception as e:
                raise HTTPException(status_code=403, detail=str(e))

        # 放行请求
        response = await call_next(request)
        return response