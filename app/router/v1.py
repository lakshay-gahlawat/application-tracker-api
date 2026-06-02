from fastapi import APIRouter

from app.router import (
    auth,
    admin,
    application,
    dashboards,
    reminders,
    notification
)

v1_router = APIRouter(
    prefix="/api/v1"
)

v1_router.include_router(auth.router)
v1_router.include_router(admin.router)
v1_router.include_router(application.router)
v1_router.include_router(dashboards.router)
v1_router.include_router(reminders.router)
v1_router.include_router(notification.router)