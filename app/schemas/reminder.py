from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReminderCreate(BaseModel):
    application_id: str
    message: Optional[str] = None
    reminder_date: datetime

class ReminderUpdate(BaseModel):
    reminder_date: Optional[datetime] = None
    message: Optional[str] = None
    is_done: Optional[bool] = None

class ReminderResponse(BaseModel):
    id: str
    application_id: str
    reminder_date: datetime
    message: Optional[str] = None
    is_done: bool
    created_at: datetime

    model_config = {
    "from_attributes": True
}