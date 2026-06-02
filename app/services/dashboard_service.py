import json
from app.models.application_model import Application
from app.models.enums import ApplicationStatus
from app.models.reminder_model import ApplicationReminder
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.core.redis_client import redis_client

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def _get_application_query(self, current_user: User):
        application = self.db.query(Application).filter(
            Application.user_id == current_user.id
        )
        
        return application

    def get_dashboard_stats(self, current_user: User):

        cache_key = (
            f"dashboard_stats:{current_user.id}"
        )

        cached_stats = redis_client.get(
            cache_key
        )

        if cached_stats:
            return json.loads(cached_stats)

        application_query = self._get_application_query(current_user)

        total = application_query.count()
    
        # applied = application_query.filter(
        #     Application.status == ApplicationStatus.APPLIED
        # ).count()

        status_counts = self.db.query(
            Application.status,
            func.count(Application.id)
        ).filter(
            Application.user_id == current_user.id
        ).group_by(Application.status).all()

        status_map = {
            status.value: count
            for status, count in status_counts
        }

        responses = (
            status_map.get("interviewing", 0) +
            status_map.get("offer", 0) +
            status_map.get("accepted", 0)
        )

        response_rate = 0
        offer_rate = 0
        acceptance_rate = 0

        offers = status_map.get("offer", 0)
        accepted = status_map.get("accepted", 0)

        if total > 0:
            response_rate = round((responses / total) * 100, 2)

        if total > 0:
            offer_rate = round((offers / total) * 100, 2)

        if offers > 0:
            acceptance_rate = round((accepted / offers) * 100, 2)

        response_durations = []

        applications = self._get_application_query(
            current_user
        ).all()

        for application in applications:
            applied_time = None
            response_time = None

            for history in application.status_history:
                if history.new_status == ApplicationStatus.APPLIED:
                    applied_time = history.changed_at

                if history.new_status in [
                    ApplicationStatus.INTERVIEWING,
                    ApplicationStatus.OFFER,
                    ApplicationStatus.ACCEPTED
                ]:
                    response_time = history.changed_at
                    break

            if applied_time and response_time:

                duration = (
                    response_time - applied_time
                ).days

                response_durations.append(duration)

        average_days_to_first_response = 0

        if response_durations:
            average_days_to_first_response = round(
                sum(response_durations) / len(response_durations), 2
            )

        pending_reminders = self.db.query(ApplicationReminder).join(Application).filter(
            Application.user_id == current_user.id,
            ApplicationReminder.is_done.is_(False)
        ).count()

        today = func.current_date()

        today_reminders = self.db.query(ApplicationReminder).join(Application).filter(
            Application.user_id == current_user.id,
            func.date(ApplicationReminder.reminder_date) == today,
            ApplicationReminder.is_done.is_(False)
        ).count()

        stats = {
        "total_applications": total,
        "applied": status_map.get("applied", 0),
        "interviewing": status_map.get("interviewing", 0),
        "offer": status_map.get("offer", 0),
        "accepted": status_map.get("accepted", 0),
        "rejected": status_map.get("rejected", 0),
        "ghosted": status_map.get("ghosted", 0),
        "response_rate": response_rate,
        "offer_rate": offer_rate,
        "acceptance_rate": acceptance_rate,
        "average_days_to_first_response": average_days_to_first_response,
        "pending_reminders": pending_reminders,
        "today_reminders": today_reminders
    }
        
        redis_client.setex(
            cache_key,
            300,
            json.dumps(stats)
        )

        return stats

    def get_monthly_application_trends(self, current_user: User):
        monthly_applications = (
            self.db.query(
                func.date_trunc(
                    "month",
                    Application.created_at
                ).label("month"),

                func.count(Application.id).label(
                    "count"
                )
            )
            .filter(Application.user_id == current_user.id)
            .group_by("month")
            .order_by("month")
            .all()
        )

        return [
            {
                "month": month.strftime("%Y-%m"),
                "applications": count
            }

            for month, count in monthly_applications
        ]