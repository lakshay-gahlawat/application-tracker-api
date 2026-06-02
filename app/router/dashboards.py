from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.dashboard import DashboardStatsResponse, MonthlyApplicationTrend
from app.dependencies.auth import  get_current_user
from app.dependencies.deps import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_stats(
    current_user: User = Depends(get_current_user),
    db:  Session = Depends(get_db)
):
    return DashboardService(db).get_dashboard_stats(current_user)

@router.get("/monthly-trends", response_model=list[MonthlyApplicationTrend])
def get_monthly_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return DashboardService(db).get_monthly_application_trends(current_user)