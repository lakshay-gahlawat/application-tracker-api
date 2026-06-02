
from apscheduler.schedulers.background import BackgroundScheduler
from app.database.session import SessionLocal
from app.models.reminder_model import ApplicationReminder
from datetime import datetime, timedelta
from app.tasks.reminder_tasks import reminder_notification
from app.core.config import REMINDER_CHECK_INTERVAL, REMINDER_PROCESSING_TIMEOUT_MINUTES
import logging
from app.services.reminder_service import ReminderService

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def check_due_reminders():
    db = SessionLocal()

    try:
        now = datetime.utcnow()
        reminder_service = ReminderService(db)

        stale_threshold = now - timedelta(
            minutes= REMINDER_PROCESSING_TIMEOUT_MINUTES
        )

        stale_reminders = db.query(ApplicationReminder).filter(
            ApplicationReminder.is_processing.is_(True),
            ApplicationReminder.is_done.is_(False),
            ApplicationReminder.processing_started_at < stale_threshold
        ).all()

        for reminder in stale_reminders:
            logger.warning(
                f"Recovering stale reminder: {reminder.id}"
            )

            reminder_service.recover_stale_reminder(
                reminder
            )

        reminders = db.query(ApplicationReminder).filter(
            ApplicationReminder.is_done.is_(False),
            ApplicationReminder.is_processing.is_(False),
            ApplicationReminder.reminder_date <= now,
            ApplicationReminder.failed_at.is_(None),
            ApplicationReminder.retry_count < 3
        ).all()

        for reminder in reminders:

            reminder_service.mark_reminder_processing(
                reminder,
                now
            )

            logger.info(
                f"Queuing reminder task: {reminder.id}"
            )
            
            reminder_notification.delay(
                reminder.id,
                reminder.message
            )

    finally:
        db.close()

scheduler.add_job(
    check_due_reminders,
    trigger = "interval",
    seconds = REMINDER_CHECK_INTERVAL
)