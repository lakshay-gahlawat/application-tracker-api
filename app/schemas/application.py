from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import ApplicationStatus

class ApplicationCreate(BaseModel):
    company_name: str
    role: str
    job_link: Optional[str] = None
    applied_date: Optional[datetime] = None
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = None
    role: Optional[str] = None
    job_link: Optional[str] = None
    applied_date: Optional[datetime] = None
    notes: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    company_name: str
    role: str
    job_link: Optional[str] = None
    status: str
    applied_date: datetime
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
    "from_attributes": True
}

class PaginatedApplicationResponse(BaseModel):
    data: list[ApplicationResponse]
    page: int
    total: int
    pages: int

    model_config = {
    "from_attributes": True
}

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus