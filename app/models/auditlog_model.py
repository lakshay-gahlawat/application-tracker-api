from sqlalchemy import Column, String, DateTime, ForeignKey
from app.database.session import Base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")