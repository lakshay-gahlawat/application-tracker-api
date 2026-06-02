from app.database.session import Base
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.models.enums import ApplicationStatus
from datetime import datetime
import uuid

class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id = Column(String, primary_key=True, index=True, default= lambda: str(uuid.uuid4()))
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    old_status = Column(Enum(ApplicationStatus))
    new_status = Column(Enum(ApplicationStatus), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="status_history")

