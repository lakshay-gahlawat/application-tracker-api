import logging
import time
import uuid

from fastapi import FastAPI, Request

from app.core.request_context import request_id_context

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def log_requests(
        request: Request,
        call_next,
    ):
        request_id = str(uuid.uuid4())

        token = request_id_context.set(request_id)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)

        finally:
            process_time = (
                time.perf_counter() - start_time
            ) * 1000

            status_code = (
                response.status_code
                if "response" in locals()
                else 500
            )

            logger.info(
                "HTTP_REQUEST | method=%s | path=%s | status_code=%s | duration_ms=%.2f",
                request.method,
                request.url.path,
                status_code,
                process_time,
            )

        request_id_context.reset(token)

        response.headers["X-Request-ID"] = request_id

        return response