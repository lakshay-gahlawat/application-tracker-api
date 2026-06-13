from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.deps import get_db
from app.dependencies.auth import get_current_admin
from app.models.user_model import User
from app.schemas.admin_schema import AdminUserResponse, AuditLogResponse
from app.schemas.admin import AdminAnalyticsResponse

from app.services.auditlog_service import AuditLogService
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/me")
def admin_me(
    current_admin : User = Depends(get_current_admin)
):
    return {
        "message": "Admin access granted",
        "email": current_admin.email,
        "role": current_admin.role
    }

@router.get("/users", response_model=list[AdminUserResponse])
def get_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return [
        AdminUserResponse(
            id = user.id,
            email = user.email,
            created_at = user.created_at,
            role = user.role.value
        )
        for user in users
    ]

@router.get("/audit-logs", response_model=list[AuditLogResponse])
def get_audit_log(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return AuditLogService(db).get_logs()

@router.get("/analytics", response_model=AdminAnalyticsResponse)
def get_analytics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return AdminService(db).get_analytics()