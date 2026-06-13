from app.models.user_model import User
from app.models.application_model import Application
from app.models.reminder_model import ApplicationReminder
from sqlalchemy import func

class AdminService:

    def __init__(self, db):
        self.db = db

    def get_analytics(self):

        total_users = self.db.query(
            func.count(User.id)
        ).scalar()

        total_applications = self.db.query(
            func.count(Application.id)
        ).scalar()

        total_reminders = self.db.query(
            func.count(ApplicationReminder.id)
        ).scalar()

        completed_reminders = self.db.query(
            func.count(ApplicationReminder.id)
        ).filter(
            ApplicationReminder.is_done.is_(True)
        ).scalar()

        pending_reminders = self.db.query(
            func.count(ApplicationReminder.id)
        ).filter(
            ApplicationReminder.is_done.is_(False)
        ).scalar()

        failed_reminders = self.db.query(
            func.count(ApplicationReminder.id)
        ).filter(
            ApplicationReminder.failed_at.is_not(None)
        ).scalar()

        status_counts = (self.db.query(
            Application.status,
            func.count(Application.id)
        )
        .group_by(Application.status)
        .all()
        )

        applications_by_status = {
            status.value: count
            for status, count in status_counts
        }
        
        return {
        "total_users": total_users,
        "total_applications": total_applications,
        "total_reminders": total_reminders,
        "completed_reminders": completed_reminders,
        "pending_reminders": pending_reminders,
        "failed_reminders": failed_reminders,
        "applications_by_status": applications_by_status
    }