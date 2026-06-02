from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.deps import get_db

from app.models.user_model import User

from app.schemas.reminder import (
    ReminderCreate,
    ReminderResponse
)

from app.services.reminder_service import ReminderService


router = APIRouter(
    prefix="/reminders",
    tags=["Reminders"]
)


@router.post(
    "/",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_reminder(
    reminder: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ReminderService(db).create_reminder(
        reminder,
        current_user
    )


@router.get(
    "/",
    response_model=list[ReminderResponse]
)
def get_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ReminderService(db).get_reminders(
        current_user
    )


@router.get(
    "/today",
    response_model=list[ReminderResponse]
)
def get_today_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ReminderService(db).get_today_reminders(
        current_user
    )


@router.patch(
    "/{reminder_id}/complete",
    response_model=ReminderResponse
)
def complete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ReminderService(db).complete_reminder(
        reminder_id,
        current_user
    )