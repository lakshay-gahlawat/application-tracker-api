"""
Tests for reminder_notification Celery task.
We call reminder_notification.run() to bypass Celery entirely.
The task opens its own SessionLocal internally, so we patch
SessionLocal at the tasks module level to inject our test session.
"""
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.models.user_model import User
from app.models.application_model import Application
from app.models.reminder_model import ApplicationReminder
from app.tasks.reminder_tasks import reminder_notification


def make_user(db, email="task_test@example.com"):
    user = User(email=email, hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_application(db, user):
    app = Application(
        company_name="Google",
        role="Backend Engineer",
        applied_date=datetime.utcnow(),
        user_id=user.id
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def make_reminder(db, application, is_done=False, is_processing=False):
    reminder = ApplicationReminder(
        application_id=application.id,
        reminder_date=datetime.utcnow(),
        message="Follow up",
        is_done=is_done,
        is_processing=is_processing,
        processing_started_at=datetime.utcnow() if is_processing else None
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


class TestReminderNotificationTask:
    def test_completed_reminder_not_processed_again(self, db_session):
        """Already-done reminder should be skipped."""
        user = make_user(db_session, "done_task@example.com")
        app = make_application(db_session, user)
        reminder = make_reminder(db_session, app, is_done=True)
        reminder_id = reminder.id

        # Patch SessionLocal so task uses our test session
        mock_session = MagicMock()
        mock_session.__enter__ = MagicMock(return_value=db_session)
        mock_session.__exit__ = MagicMock(return_value=False)

        with patch("app.tasks.reminder_tasks.SessionLocal", return_value=db_session):
            reminder_notification.run(reminder_id, "Follow up")

        result = db_session.get(ApplicationReminder, reminder_id)
        assert result.is_done is True

    def test_task_completes_processing_reminder(self, db_session):
        """Task should mark reminder as done and clear processing fields."""
        user = make_user(db_session, "worker_task@example.com")
        app = make_application(db_session, user)
        reminder = make_reminder(db_session, app, is_processing=True)
        reminder_id = reminder.id

        with patch(
            "app.tasks.reminder_tasks.SessionLocal",
            return_value=db_session
        ), patch(
            "app.tasks.reminder_tasks.EmailService.send_reminder_email",
            return_value=None
        ):
            reminder_notification.run(reminder_id, "Follow up")

        result = db_session.get(ApplicationReminder, reminder_id)
        assert result.is_done is True
        assert result.is_processing is False
        assert result.processing_started_at is None

    def test_task_handles_nonexistent_reminder(self, db_session):
        """Task should return safely if reminder doesn't exist."""
        with patch("app.tasks.reminder_tasks.SessionLocal", return_value=db_session):
            reminder_notification.run("nonexistent-id", "Follow up")
        # No exception = pass

    def test_task_completes_pending_reminder(self, db_session):
        """Normal flow — pending reminder gets completed."""
        user = make_user(db_session, "pending_task@example.com")
        app = make_application(db_session, user)
        reminder = make_reminder(db_session, app)
        reminder_id = reminder.id
        with patch(
            "app.tasks.reminder_tasks.SessionLocal",
            return_value=db_session
        ), patch(
            "app.tasks.reminder_tasks.EmailService.send_reminder_email",
            return_value=None
        ):
            reminder_notification.run(reminder_id, "Follow up")

        result = db_session.get(ApplicationReminder, reminder_id)
        assert result.is_done is True