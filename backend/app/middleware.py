"""中间件：全局异常处理、访问日志、基于 IP 的滑动窗口限流。"""
import logging
import threading
import time
import traceback
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings

logger = logging.getLogger(__name__)

# 限流排除路径（健康检查与文档）
EXEMPT_PATHS = {"/api/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """兜底异常处理：任何未捕获异常返回统一 500 JSON，堆栈写日志。"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception:
            logger.error(
                "未捕获异常 path=%s\n%s", request.url.path, traceback.format_exc()
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "服务器开小差了，请稍后再试"},
            )


class AccessLogMiddleware(BaseHTTPMiddleware):
    """访问日志：客户端、方法、路径、状态码、耗时。"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            cost_ms = (time.perf_counter() - start) * 1000
            client = request.client.host if request.client else "-"
            status = response.status_code if response is not None else 500
            logger.info("%s %s %s -> %s (%.1fms)", client, request.method, request.url.path, status, cost_ms)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """基于 IP 的滑动窗口限流（内存实现，单进程内生效）。

    默认 120 次/分钟，超限返回 429。/api/health 与文档路径排除。
    """

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self._lock = threading.Lock()
        # ip -> deque[timestamp(monotonic)]
        self._hits: dict[str, deque] = {}
        self._window_seconds = 60
        self._limit = settings.rate_limit_per_minute
        self._last_cleanup = time.monotonic()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        if path in EXEMPT_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        if self._is_limited(client_ip, now):
            logger.warning("限流触发 ip=%s path=%s", client_ip, path)
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"},
                headers={"Retry-After": "60"},
            )
        return await call_next(request)

    def _is_limited(self, ip: str, now: float) -> bool:
        window_start = now - self._window_seconds
        with self._lock:
            hits = self._hits.get(ip)
            if hits is None:
                hits = deque()
                self._hits[ip] = hits
            # 淘汰窗口外记录
            while hits and hits[0] <= window_start:
                hits.popleft()
            limited = len(hits) >= self._limit
            if not limited:
                hits.append(now)
            # 周期性清理空桶，防止内存无限增长
            if now - self._last_cleanup > 300:
                self._last_cleanup = now
                empty = [k for k, v in self._hits.items() if not v]
                for k in empty:
                    self._hits.pop(k, None)
        return limited


def register_middlewares(app: FastAPI) -> None:
    """注册中间件（Starlette 后注册的先执行，异常兜底最先执行）。"""
    app.add_middleware(GlobalExceptionMiddleware)
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RateLimitMiddleware)
