from fastapi import APIRouter, Depends
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService
from app.dependencies.deps import get_db
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/notifications", tags=["Notification"])

@router.get("/", response_model=list[NotificationResponse])
def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return NotificationService(db).get_notifications(current_user)

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return NotificationService(db).mark_as_read(notification_id, current_user)