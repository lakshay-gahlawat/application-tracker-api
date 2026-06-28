from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token
import logging

logger = logging.getLogger(__name__)


class AuthService:

    def __init__(self, db: Session):
        self.db = db

    def register_user(
        self,
        user_data: UserCreate
    ):
        existing_user = self.db.query(User).filter(
            User.email == user_data.email
        ).first()

        if existing_user:
            logger.warning(
                "USER_REGISTER_FAILED | email=%s | reason=duplicate_email",
                user_data.email,
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password)
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        logger.info(
            "USER_REGISTER_SUCCESS | user_id=%s | email=%s",
            user.id,
            user.email,
        )

        return user

    def login_user(
        self,
        email: str,
        password: str
    ):
        user = self.db.query(User).filter(
            User.email == email
        ).first()

        if not user or not verify_password(
            password,
            user.hashed_password
        ):
            logger.warning(
                "USER_LOGIN_FAILED | email=%s | reason=invalid_credentials",
                email,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        logger.info(
            "USER_LOGIN_SUCCESS | user_id=%s | email=%s",
            user.id,
            user.email,
        )

        token = create_access_token(user.id)

        return {
            "access_token": token,
            "token_type": "Bearer"
        }

    def update_user(
        self,
        user_update: UserUpdate,
        current_user: User
    ):
        update_data = user_update.model_dump(
            exclude_unset=True
        )

        if "email" in update_data:

            existing_user = self.db.query(User).filter(
                User.email == update_data["email"]
            ).first()

            if (
                existing_user
                and existing_user.id != current_user.id
            ):
                
                logger.warning(
                    "USER_UPDATE_FAILED | user_id=%s | reason=duplicate_email",
                    current_user.id,
                )
                                
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )

        if "password" in update_data:

            update_data["hashed_password"] = hash_password(
                update_data["password"]
            )

            del update_data["password"]

        for key, value in update_data.items():
            setattr(current_user, key, value)

        self.db.commit()
        self.db.refresh(current_user)

        logger.info(
            "USER_UPDATE_SUCCESS | user_id=%s | email=%s",
            current_user.id,
            current_user.email,
        )

        return current_user

    def delete_user(
        self,
        current_user: User
    ):
        self.db.delete(current_user)
        self.db.commit()

        logger.info(
            "USER_DELETE_SUCCESS | user_id=%s | email=%s",
            current_user.id,
            current_user.email,
        )

        return {
            "message": "User deleted successfully"
        }