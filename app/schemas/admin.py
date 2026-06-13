from pydantic import BaseModel

class AdminAnalyticsResponse(BaseModel):
    total_users: int
    total_applications: int
    total_reminders: int
    completed_reminders: int
    pending_reminders: int
    failed_reminders: int
    applications_by_status: dict[str, int]