from app.core.celery_app import celery_app
from app.models.reminder_model import ApplicationReminder
from app.database.session import SessionLocal
from datetime import datetime
import logging
from app.services.reminder_service import ReminderService
from app.services.notification_service import NotificationService
from app.services.auditlog_service import AuditLogService
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

@celery_app.task

def reminder_notification(
    reminder_id: str,
    message: str
):
    db = SessionLocal()

    try:
        reminder = db.get(
            ApplicationReminder,
            reminder_id
        )

        if not reminder:
            return
        
        if reminder.is_done:
            return

        logger.info(
        f"REMINDER_QUEUED | "
        f"reminder_id={reminder.id} | "
        f"application_id={reminder.application_id}"
        )

        reminder_service = ReminderService(db)
        email_service = EmailService()

        email_service.send_reminder_email(
            to_email=reminder.application.user.email,
            company_name=reminder.application.company_name,
            role=reminder.application.role
        )

        reminder_service.mark_reminder_completed(
            reminder
        )

        reminder.retry_count = 0
        reminder.last_retry_at = None

        notification_service = NotificationService(db)

        notification_service.create_notification(
            user_id=reminder.application.user_id,
            title="Reminder completed",
            message=f"Reminder sent for {reminder.application.company_name}"
        )

    except Exception as e:
        db.rollback()

        reminder = db.get(
        ApplicationReminder,
        reminder_id
        )
        
        reminder.retry_count += 1
        reminder.last_retry_at = datetime.utcnow()

        if reminder.retry_count >= 3:
            reminder.failed_at = datetime.utcnow()

        AuditLogService(db).create_log(
            user_id=None,
            action="REMINDER_FAILED",
            entity_type="application_reminder",
            entity_id=reminder.id
        )

        db.commit()

        logger.error(
        f"REMINDER_FAILED | "
        f"reminder_id={reminder.id} | "
        f"error={str(e)}"
        )

    finally:
        db.close()

    
