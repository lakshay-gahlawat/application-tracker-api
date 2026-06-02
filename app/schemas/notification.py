from pydantic import BaseModel
from datetime import datetime

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
