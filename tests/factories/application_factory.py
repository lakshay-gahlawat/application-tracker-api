from app.models.application_model import Application
from app.models.enums import ApplicationStatus
from tests.factories.user_factory import create_user
from app.models.application_status_history import ApplicationStatusHistory
from datetime import datetime
from sqlalchemy.orm import Session

def create_application(
        db:Session,
        user=None,
        company_name="Google",
        role="Backend Engineer",
        status=ApplicationStatus.APPLIED
):
    if user is None:
        user = create_user(db)

    application = Application(
        user_id=user.id,
        company_name=company_name,
        role=role,
        status=status,
        applied_date=datetime.utcnow()
    )

    db.add(application)
    db.flush()
    db.refresh(application)

    history = ApplicationStatusHistory(
        application_id = application.id,
        old_status = None,
        new_status = status
    )

    db.add(history)

    db.flush()

    return application