import logging
import time

from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def log_requests(
        request: Request,
        call_next,
    ):
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "HTTP_REQUEST | method=%s | path=%s | status_code=%s | duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response