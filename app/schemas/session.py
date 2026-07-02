from pydantic import BaseModel
from datetime import datetime

class SessionResponse(BaseModel):
    id: str
    user_id: str
    token_hash: str
    expires_at: datetime
    revoked_at: datetime

    model_config = {
        "from_attributes": True
    }    