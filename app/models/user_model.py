from sqlalchemy import Column, String, DateTime
from sqlalchemy import Enum as SQLEnum
from app.database.session import Base
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship
from app.models.enums import UserRole

class User(Base):
    
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)

    applications = relationship("Application", back_populates="user")

    notifications = relationship("Notification", back_populates="user")

    audit_logs = relationship("AuditLog", back_populates="user")

    sessions = relationship("RefreshSession", back_populates="user", cascade="all, delete-orphan")