from celery import Celery
from app.core.config import REDIS_URL

celery_app = Celery(
    "application_tracker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.reminder_tasks"]
)