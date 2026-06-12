from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.models.application_model import Application
from app.models.enums import ApplicationStatus
from app.models.application_status_history import (
    ApplicationStatusHistory
)

from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationStatusUpdate
)

from app.services.auditlog_service import AuditLogService
from app.core.redis_client import redis_client


class ApplicationService:

    def __init__(self, db: Session):
        self.db = db

    def _get_user_application(
        self,
        application_id: str,
        current_user: User
    ):
        application = self.db.query(Application).filter(
            Application.id == application_id,
            Application.deleted_at.is_(None)
        ).first()

        if (
            not application
            or application.user_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

        return application

    def create_application(
        self,
        app_data: ApplicationCreate,
        current_user: User
    ):
        existing = self.db.query(Application).filter(
            Application.user_id == current_user.id,
            Application.company_name == app_data.company_name,
            Application.role == app_data.role,
            Application.deleted_at.is_(None)
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Application already exists"
            )

        app_dict = app_data.model_dump()

        app_dict["user_id"] = current_user.id

        if not app_dict.get("applied_date"):
            app_dict["applied_date"] = datetime.utcnow()

        application = Application(**app_dict)

        self.db.add(application)
        self.db.flush()

        AuditLogService(self.db).create_log(
            user_id=current_user.id,
            action="APPLICATION_CREATED",
            entity_type="application",
            entity_id=application.id
        )

        history = ApplicationStatusHistory(
        application_id=application.id,
        old_status=None,
        new_status=ApplicationStatus.APPLIED
    )

        self.db.add(history)
        self.db.commit()
        self.db.refresh(application)

        redis_client.delete(
            f"dashboard_stats:{current_user.id}"
        )

        return application

    def get_applications(
        self,
        current_user: User,
        page: int,
        limit: int,
        status_filter: str | None,
        company: str | None,
        role: str | None,
        sort_by: str | None,
        order: str | None
    ):
        query = self.db.query(Application).filter(
            Application.user_id == current_user.id,
            Application.deleted_at.is_(None)
        )

        if status_filter:
            try:
                status_enum = ApplicationStatus(status_filter)
                query = query.filter(Application.status == status_enum)
            except ValueError:
                pass  # ignore invalid status values

        if company:
            query = query.filter(
                Application.company_name.ilike(
                    f"%{company}%"
                )
            )

        if role:
            query = query.filter(
                Application.role == role
            )

        total = query.count()

        pages = (
            (total + limit - 1) // limit
            if total > 0 else 0
        )

        if page > pages and pages != 0:
            page = pages

        offset = (page - 1) * limit

        allowed_sort_fields = {
            "created_at": Application.created_at,
            "applied_date": Application.applied_date
        }

        order = (order or "desc").lower()

        if order not in ["asc", "desc"]:
            order = "desc"

        column = allowed_sort_fields.get(
            sort_by,
            Application.created_at
        )

        if order == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

        results = query.offset(offset).limit(limit).all()

        return {
            "data": results,
            "page": page,
            "total": total,
            "pages": pages
        }

    def get_application_by_id(
        self,
        application_id: str,
        current_user: User
    ):
        return self._get_user_application(
            application_id,
            current_user
        )

    def update_application(
        self,
        application_id: str,
        update_data: ApplicationUpdate,
        current_user: User
    ):
        application = self._get_user_application(
            application_id,
            current_user
        )

        update_fields = update_data.model_dump(
            exclude_unset=True
        )

        if (
            "company_name" in update_fields
            or "role" in update_fields
        ):

            company = update_fields.get(
                "company_name",
                application.company_name
            )

            role = update_fields.get(
                "role",
                application.role
            )

            existing = self.db.query(Application).filter(
                Application.user_id == current_user.id,
                Application.company_name == company,
                Application.role == role,
                Application.id != application.id,
                Application.deleted_at.is_(None)
            ).first()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Application already exists"
                )

        for key, value in update_fields.items():
            setattr(application, key, value)

        AuditLogService(self.db).create_log(
            user_id=current_user.id,
            action="APPLICATION_UPDATED",
            entity_type="application",
            entity_id=application.id
        )

        self.db.commit()
        self.db.refresh(application)

        redis_client.delete(
            f"dashboard_stats:{current_user.id}"
        )

        return application

    def delete_application(
        self,
        application_id: str,
        current_user: User
    ):
        application = self._get_user_application(
            application_id,
            current_user
        )

        AuditLogService(self.db).create_log(
            user_id=current_user.id,
            action="APPLICATION_DELETED",
            entity_type="application",
            entity_id=application.id
        )

        application.deleted_at  = datetime.utcnow()
        self.db.commit()

        redis_client.delete(
            f"dashboard_stats:{current_user.id}"
        )

        return {
            "message": "Application deleted successfully"
        }

    def update_application_status(
        self,
        application_id: str,
        update_status: ApplicationStatusUpdate,
        current_user: User
    ):
        application = self._get_user_application(
            application_id,
            current_user
        )

        allowed_transitions = {
            ApplicationStatus.APPLIED: [
                ApplicationStatus.INTERVIEWING,
                ApplicationStatus.REJECTED,
                ApplicationStatus.GHOSTED
            ],
            ApplicationStatus.INTERVIEWING: [
                ApplicationStatus.OFFER,
                ApplicationStatus.REJECTED,
                ApplicationStatus.GHOSTED
            ],
            ApplicationStatus.OFFER: [
                ApplicationStatus.ACCEPTED,
                ApplicationStatus.REJECTED
            ],
            ApplicationStatus.ACCEPTED: [],

            ApplicationStatus.REJECTED: [],

            ApplicationStatus.GHOSTED: [
                ApplicationStatus.INTERVIEWING
            ]
        }

        current_status = application.status
        new_status = update_status.status

        if new_status == current_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status is already the same"
            )

        if (
            new_status
            not in allowed_transitions[current_status]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transition not allowed"
            )

        application.status = new_status

        history = ApplicationStatusHistory(
            application_id=application.id,
            old_status=current_status,
            new_status=new_status
        )

        self.db.add(history)
        self.db.commit()
        self.db.refresh(application)

        return application