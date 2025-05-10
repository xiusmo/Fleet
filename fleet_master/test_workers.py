#!/usr/bin/env python3
"""
测试多worker是否正常工作的脚本
"""
import asyncio
import json
import sys
from collections import Counter

import aiohttp

async def get_worker_id(session, url):
    """从根路由获取worker ID"""
    async with session.get(url) as response:
        if response.status != 200:
            return None
        data = await response.json()
        return data.get('worker_id')

async def main():
    """主函数"""
    url = "http://localhost:8000/"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    num_requests = 1000
    print(f"向 {url} 发送 {num_requests} 个请求...")
    
    async with aiohttp.ClientSession() as session:
        tasks = [get_worker_id(session, url) for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
    
    # 统计每个worker处理的请求数
    worker_counter = Counter(results)
    worker_ids = list(worker_counter.keys())
    
    print(f"\n发现 {len(worker_ids)} 个不同的worker进程:")
    for worker_id, count in worker_counter.items():
        print(f"Worker ID: {worker_id}, 处理了 {count} 个请求 ({count/num_requests:.1%})")
    
    if len(worker_ids) > 1:
        print("\n✅ 多worker模式正常工作！请求被分配到多个不同的worker进程。")
    else:
        print("\n❌ 似乎只有一个worker在工作。请检查gunicorn配置。")

if __name__ == "__main__":
    asyncio.run(main()) 