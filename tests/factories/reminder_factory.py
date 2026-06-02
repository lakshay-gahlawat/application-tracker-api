from app.models.reminder_model import ApplicationReminder
from tests.factories.application_factory import create_application
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

def create_reminder(
        db:Session,
        application=None,
        message="Follow up",
        minutes_from_now=30,
        reminder_date=None,
        is_done=False,
        is_processing=False
):
    if application is None:
        application = create_application(db)

    if reminder_date is None:
        reminder_date = datetime.utcnow() + timedelta(
            minutes=minutes_from_now
        )

    reminder = ApplicationReminder(
        application_id=application.id,
        message=message,
        reminder_date=reminder_date,
        is_done=is_done,
        is_processing=is_processing
    )

    db.add(reminder)

    db.flush()

    db.refresh(reminder)

    return reminder