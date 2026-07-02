from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
import uuid

class RefreshSession(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    token_hash = Column(String, unique=True, nullable=False)

    expires_at = Column(DateTime, nullable=False)

    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")