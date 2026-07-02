from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    UserUpdate,
    TokenResponse,
    RefreshTokenRequest
)
from app.schemas.common import MessageResponse
from app.dependencies.deps import get_db
from app.dependencies.auth import get_current_user
from app.models.user_model import User
from app.services.auth_service import AuthService

from app.core.rate_limiter import limiter, login_limiter_key

router = APIRouter(tags=["Users"])

# ---------------- AUTH ---------------- #

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return AuthService(db).register_user(user)


@router.post("/auth/login", response_model=TokenResponse)
@limiter.limit("5/minute", key_func=login_limiter_key)
def login_user(
    request: Request,
    login: UserLogin,
    db: Session = Depends(get_db)
):
    request.state.login_email = login.email
    return AuthService(db).login_user(
        login.email,
        login.password
    )

# ---------------- USER ---------------- #

@router.get("/users/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.post("/refresh")
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    return AuthService(db).refresh_access_token(request.refresh_token)

@router.post("/logout")
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    return AuthService(db).logout(request.refresh_token)

@router.put("/users/me", response_model=UserResponse)
def update_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return AuthService(db).update_user(
        user_update,
        current_user
    )


@router.delete("/users/me", response_model=MessageResponse)
def delete_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return AuthService(db).delete_user(current_user)