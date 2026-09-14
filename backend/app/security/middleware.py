import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from backend.app.config import MAX_REQUEST_SIZE_BYTES, IS_PRODUCTION
from backend.app.security.rate_limit import check_rate_limit

logger = logging.getLogger("crimenet.security.middleware")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces essential HTTP security headers across all API responses."""
    async def dispatch(self, request: Request, call_next):
        # 1. Attach Correlation ID for end-to-end request tracing
        correlation_id = request.headers.get("X-Correlation-ID") or f"req-{uuid.uuid4().hex[:12]}"
        request.state.correlation_id = correlation_id

        # 2. Enforce Request Size Limit
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > MAX_REQUEST_SIZE_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={"error": "Payload Too Large", "detail": "Request body exceeds 10MB limit.", "correlation_id": correlation_id}
                    )
            except ValueError:
                pass

        # 3. Rate Limit Enforcement
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Real-IP") or (request.client.host if request.client else "127.0.0.1")
        if not check_rate_limit(client_ip, max_requests=180, window_seconds=60):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate Limit Exceeded", "detail": "Too many requests. Please slow down.", "correlation_id": correlation_id}
            )

        # 4. Safe Request Execution
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            logger.error(f"Unhandled server error [{correlation_id}]: {exc}", exc_info=not IS_PRODUCTION)
            if IS_PRODUCTION:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal Server Error",
                        "detail": "An unexpected error occurred. Please contact an intelligence administrator.",
                        "correlation_id": correlation_id
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal Server Error",
                        "detail": str(exc),
                        "correlation_id": correlation_id
                    }
                )

        # 5. Inject Security Headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws: wss:;"
        )
        if request.url.scheme == "https" or IS_PRODUCTION:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
