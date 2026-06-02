"""
Tests for ReminderService internal methods directly — no HTTP needed.
"""
from datetime import datetime
from app.models.user_model import User
from app.models.application_model import Application
from app.models.reminder_model import ApplicationReminder
from app.models.application_status_history import ApplicationStatusHistory
from app.models.enums import ApplicationStatus
from app.services.reminder_service import ReminderService


def make_user(db, email="service_test@example.com"):
    user = User(email=email, hashed_password="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_application(db, user):
    app = Application(
        company_name="Google", role="Backend Engineer",
        applied_date=datetime.utcnow(), user_id=user.id
    )
    db.add(app)
    db.flush()
    history = ApplicationStatusHistory(
        application_id=app.id, old_status=None,
        new_status=ApplicationStatus.APPLIED
    )
    db.add(history)
    db.commit()
    db.refresh(app)
    return app


def make_reminder(db, application, message="Follow up"):
    reminder = ApplicationReminder(
        application_id=application.id,
        reminder_date=datetime.utcnow(),
        message=message
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


class TestMarkReminderProcessing:
    def test_sets_is_processing_true(self, db_session):
        user = make_user(db_session, "processing@example.com")
        app = make_application(db_session, user)
        reminder = make_reminder(db_session, app)
        now = datetime.utcnow()
        ReminderService(db_session).mark_reminder_processing(reminder, now)
        db_session.refresh(reminder)
        assert reminder.is_processing is True
        assert reminder.processing_started_at == now

    def test_does_not_mark_as_done(self, db_session):
        user = make_user(db_session, "processing2@example.com")
        app = make_application(db_session, user)
        reminder = make_reminder(db_session, app)
        ReminderService(db_session).mark_reminder_processing(reminder, datetime.utcnow())
        db_session.refresh(reminder)
        assert reminder.is_done is False


class TestMarkReminderCompleted:
    def test_marks_done_and_clears_processing(self, db_session):
        user = make_user(db_session, "completed@example.com")
        app = make_application(db_session, user)
        reminder = make_reminder(db_session, app)
        reminder.is_processing = True
        reminder.processing_started_at = datetime.utcnow()
        db_session.commit()
        ReminderService(db_session).mark_reminder_completed(reminder)
        db_session.refresh(reminder)
        assert reminder.is_done is True
        assert reminder.is_processing is False
        assert reminder.processing_started_at is None


class TestRecoverStaleReminder:
    def test_clears_processing_fields(self, db_session):
        user = make_user(db_session, "stale@example.com")
        app = make_application(db_session, user)
        reminder = make_reminder(db_session, app)
        reminder.is_processing = True
        reminder.processing_started_at = datetime.utcnow()
        db_session.commit()
        ReminderService(db_session).recover_stale_reminder(reminder)
        db_session.refresh(reminder)
        assert reminder.is_processing is False
        assert reminder.processing_started_at is None

    def test_does_not_mark_as_done(self, db_session):
        user = make_user(db_session, "stale2@example.com")
        app = make_application(db_session, user)
        reminder = make_reminder(db_session, app)
        reminder.is_processing = True
        reminder.processing_started_at = datetime.utcnow()
        db_session.commit()
        ReminderService(db_session).recover_stale_reminder(reminder)
        db_session.refresh(reminder)
        assert reminder.is_done is False