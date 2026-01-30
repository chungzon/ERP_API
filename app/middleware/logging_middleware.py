import time
from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from utils.log_manager import LogEntry, log_manager

# Max body size to capture (avoid huge payloads flooding the log)
MAX_BODY_LOG_SIZE = 4096


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that intercepts requests/responses and pushes log entries to LogManager."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Capture request body
        request_body = None
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    text = body_bytes.decode("utf-8", errors="replace")
                    request_body = text[:MAX_BODY_LOG_SIZE]
            except Exception:
                request_body = "<unable to read body>"

        # Call the actual endpoint
        response: Response = await call_next(request)

        # Capture response body
        response_body = None
        response_body_bytes = b""
        async for chunk in response.body_iterator:
            if isinstance(chunk, str):
                response_body_bytes += chunk.encode("utf-8")
            else:
                response_body_bytes += chunk

        if response_body_bytes:
            text = response_body_bytes.decode("utf-8", errors="replace")
            response_body = text[:MAX_BODY_LOG_SIZE]

        # Rebuild response with captured body
        from starlette.responses import Response as StarletteResponse
        new_response = StarletteResponse(
            content=response_body_bytes,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        duration_ms = (time.perf_counter() - start_time) * 1000

        # Push log entry
        entry = LogEntry(
            timestamp=timestamp,
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            request_body=request_body,
            response_body=response_body,
        )
        log_manager.push(entry)

        return new_response
