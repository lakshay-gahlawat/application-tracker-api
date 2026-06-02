from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.application_model import Application
from app.models.reminder_model import ApplicationReminder
from app.models.user_model import User
from app.schemas.reminder import ReminderCreate
from app.services.auditlog_service import AuditLogService

from datetime import datetime
from app.core.redis_client import redis_client

class ReminderService:

    def __init__(self, db: Session):
        self.db = db

    def _get_user_reminder(
        self,
        reminder_id: str,
        current_user: User
    ):
        reminder = (
            self.db.query(ApplicationReminder)
            .join(Application)
            .filter(
                ApplicationReminder.id == reminder_id,
                Application.user_id == current_user.id
            )
            .first()
        )

        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found"
            )

        return reminder

    def create_reminder(
        self,
        reminder_data: ReminderCreate,
        current_user: User
    ):
        application = self.db.query(Application).filter(
            Application.id == reminder_data.application_id,
            Application.user_id == current_user.id
        ).first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

        reminder_dict = reminder_data.model_dump()

        existing_reminder = self.db.query(ApplicationReminder).filter(
            ApplicationReminder.application_id == reminder_data.application_id,
            ApplicationReminder.reminder_date == reminder_data.reminder_date
        ).first()

        if existing_reminder:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Reminder already exists"
            )

        application_reminder = ApplicationReminder(
            **reminder_dict
        )

        self.db.add(application_reminder)
        self.db.flush()

        AuditLogService(self.db).create_log(
            user_id=current_user.id,
            action="REMINDER_CREATED",
            entity_type="application_reminder",
            entity_id=application_reminder.id
        )

        self.db.add(application_reminder)
        self.db.commit()
        self.db.refresh(application_reminder)

        redis_client.delete(
        f"dashboard_stats:{current_user.id}"
        )

        return application_reminder

    def get_reminders(
        self,
        current_user: User
    ):
        reminders = (
            self.db.query(ApplicationReminder)
            .join(Application)
            .filter(
                Application.user_id == current_user.id
            )
            .all()
        )

        return reminders

    def get_today_reminders(
        self,
        current_user: User
    ):
        today = func.current_date()

        reminders = (
            self.db.query(ApplicationReminder)
            .join(Application)
            .filter(
                Application.user_id == current_user.id,
                func.date(
                    ApplicationReminder.reminder_date
                ) == today,
                ApplicationReminder.is_done.is_(False)
            )
            .all()
        )

        return reminders

    def complete_reminder(
        self,
        reminder_id: str,
        current_user: User
    ):
        reminder = self._get_user_reminder(
            reminder_id,
            current_user
        )

        if reminder.is_done:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reminder already completed"
            )

        reminder.is_done = True

        AuditLogService(self.db).create_log(
            user_id=current_user.id,
            action="REMINDER_CREATED",
            entity_type="application_reminder",
            entity_id=reminder.id
        )

        self.db.commit()
        self.db.refresh(reminder)

        redis_client.delete(
        f"dashboard_stats:{current_user.id}"
        )

        return reminder
    
    def mark_reminder_processing(
            self,
            reminder: ApplicationReminder,
            now: datetime
    ):
        reminder.is_processing = True
        reminder.processing_started_at = now

        self.db.commit()

    def mark_reminder_completed(
            self,
            reminder: ApplicationReminder
    ):
        reminder.is_done = True
        reminder.is_processing = False
        reminder.processing_started_at = None

        self.db.commit()

    def recover_stale_reminder(
            self,
            reminder: ApplicationReminder
    ):
        reminder.is_processing = False
        reminder.processing_started_at = None

        AuditLogService(self.db).create_log(
            user_id=None,
            action="REMINDER_CREATED",
            entity_type="application_reminder",
            entity_id=reminder.id
        )

        self.db.commit()