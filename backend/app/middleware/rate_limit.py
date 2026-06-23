from collections import defaultdict, deque
from time import monotonic

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/health", "/docs", "/openapi.json"}:
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = monotonic()
        bucket = self.requests[client]
        while bucket and now - bucket[0] > settings.RATE_LIMIT_WINDOW_SECONDS:
            bucket.popleft()

        if len(bucket) >= settings.RATE_LIMIT_REQUESTS:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please wait and try again."},
            )

        bucket.append(now)
        return await call_next(request)

