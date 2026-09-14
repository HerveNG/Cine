"""Baseline security response headers, applied to every response.

Not a replacement for HTTPS/CSP tuning at the reverse-proxy layer in a
real deployment — see docs/known-issues.md — but a free, zero-dependency
floor that costs nothing to keep on for an API + SPA pairing like this
one.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        # HSTS only makes sense once the app is actually served over
        # HTTPS — forcing it in local dev (plain http://localhost) would
        # just break the browser's ability to reach it.
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response
