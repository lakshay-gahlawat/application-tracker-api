from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.core.rate_limiter import limiter
from app.router.v1 import v1_router
from app.core.config import TESTING
from app.core.logging import configure_logging
from app.core.exception_handler import register_exception_handlers
from app.core.middleware import register_middleware

configure_logging()

app = FastAPI()

register_exception_handlers(app)
register_middleware(app)

app.include_router(v1_router)

if not TESTING:
    app.state.limiter = limiter

    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler
    )

    app.add_middleware(SlowAPIMiddleware)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}

