from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.enums import ApplicationStatus
from app.models.application_status_history import ApplicationStatusHistory
import uuid

from app.database.session import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    company_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    job_link = Column(String)

    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    applied_date = Column(DateTime, nullable=False)

    notes = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    status_history = relationship("ApplicationStatusHistory",
            back_populates="application",
            order_by=ApplicationStatusHistory.changed_at,
            cascade="all, delete-orphan"  
        )
    
    deleted_at = Column(DateTime, nullable=True)

    reminders = relationship("ApplicationReminder", back_populates="application")

    __table_args__ = (
        UniqueConstraint("user_id", "company_name", "role", name="unique_application_per_user"),
    )