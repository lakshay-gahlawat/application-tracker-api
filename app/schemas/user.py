from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    model_config = {
    "from_attributes": True
}

class UserLogin(BaseModel):
    email: str
    password: str
    