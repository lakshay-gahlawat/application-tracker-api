from pydantic import BaseModel
from datetime import datetime

class AdminUserResponse(BaseModel):
    id: str
    email: str
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class AuditLogResponse(BaseModel):
    id: str
    user_id: str | None
    action: str
    entity_type: str
    entity_id: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }