from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password
from app.core.auth import create_access_token


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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
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

        return current_user

    def delete_user(
        self,
        current_user: User
    ):
        self.db.delete(current_user)
        self.db.commit()

        return {
            "message": "User deleted successfully"
        }