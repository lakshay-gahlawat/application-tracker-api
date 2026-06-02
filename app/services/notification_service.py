from app.models.notification_model import Notification
from fastapi import HTTPException, status

class NotificationService:
    def __init__(self, db):
        self.db = db

    def create_notification(self, user_id, title, message):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message
            )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        return notification

    def get_notifications(self, current_user):

        notifications = self.db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).order_by(
            Notification.created_at.desc()
        ).all()

        return notifications
    
    def mark_as_read(self, notification_id, current_user):
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()

        if not notification:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
            )

        notification.is_read = True

        self.db.commit()
        self.db.refresh(notification)

        return notification