from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base
import uuid

class Notification(Base):

    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True, default= lambda : str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    message = Column(String, nullable=False)

    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime,  default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notifications")
