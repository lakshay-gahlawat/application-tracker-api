from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    ApplicationResponse,
    ApplicationUpdate,
    PaginatedApplicationResponse
)

from app.schemas.common import MessageResponse
from app.dependencies.deps import get_db
from app.dependencies.auth import get_current_user
from app.services.application_service import ApplicationService
from app.models.user_model import User


router = APIRouter(
    prefix="/applications",
    tags=["Application"]
)


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    application: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ApplicationService(db).create_application(
        application,
        current_user
    )


@router.get("/", response_model=PaginatedApplicationResponse)
def get_applications(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    status: str | None = None,
    company: str | None = None,
    role: str | None = None,

    sort_by: str | None = None,
    order: str | None = None,

    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ApplicationService(db).get_applications(
        current_user,
        page,
        limit,
        status,
        company,
        role,
        sort_by,
        order
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application_by_id(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ApplicationService(db).get_application_by_id(
        application_id,
        current_user
    )


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: str,
    application: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ApplicationService(db).update_application(
        application_id,
        application,
        current_user
    )


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse
)
def update_application_status(
    application_id: str,
    update_status: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ApplicationService(db).update_application_status(
        application_id,
        update_status,
        current_user
    )


@router.delete("/{application_id}", response_model=MessageResponse)
def delete_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ApplicationService(db).delete_application(
        application_id,
        current_user
    )