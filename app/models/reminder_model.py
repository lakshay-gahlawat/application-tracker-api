from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.session import Base


class ApplicationReminder(Base):
    __tablename__ = "application_reminders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    application_id = Column(
        String,
        ForeignKey("applications.id"),
        nullable=False
    )

    reminder_date = Column(DateTime, nullable=False)
    message = Column(String)

    is_done = Column(Boolean, nullable=False, default=False)
    is_processing = Column(Boolean, default=False)

    processing_started_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    retry_count = Column(Integer, default=0, nullable=False)
    last_retry_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)

    application = relationship(
        "Application",
        back_populates="reminders"
    )