from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    total_applications: int

    applied: int
    interviewing: int
    offer: int
    accepted: int
    rejected: int
    ghosted: int

    pending_reminders: int
    today_reminders: int

    response_rate: float
    offer_rate: float
    acceptance_rate: float
    average_days_to_first_response: float

class MonthlyApplicationTrend(BaseModel):
    month: str
    applications: int
    