from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from app.core.config import TESTING

def get_login_rate_key(request: Request) -> str:
    # email is attached to request.state by the route before limiting
    email = getattr(request.state, "login_email", "")
    ip = get_remote_address(request)
    return f"{ip}:{email}"

limiter = Limiter(
    key_func=get_remote_address,  # default for all routes
    enabled=not TESTING
)

login_limiter_key = get_login_rate_key