from app.models.user_model import User
from app.core.security import hash_password
from sqlalchemy.orm import Session
import uuid

def create_user(
        db: Session,
        email: str | None = None,
        password: str ="test1234"
):
    if email is None:
        email = f"{uuid.uuid4()}@test.com"

    hashed_password = hash_password(password)

    user = User(
        email=email,
        hashed_password = hashed_password
    )

    db.add(user)
    db.flush()
    db.refresh(user)

    return user