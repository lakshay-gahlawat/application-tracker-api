"""
Tests for notification endpoints.
Note: Notifications are created internally by the system (e.g. reminders),
not directly by users. We create them via NotificationService directly.
"""
from tests.conftest import register_and_login, BASE_URL
from app.dependencies.deps import get_db
from app.services.notification_service import NotificationService
from app.models.user_model import User


def create_notification_for_user(client, email, title="Test", message="Test message"):
    db = next(client.app.dependency_overrides[get_db]())
    user = db.query(User).filter(User.email == email).first()
    NotificationService(db).create_notification(user.id, title, message)


class TestGetNotifications:
    def test_get_empty_notifications(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/notifications/", headers=headers)
        assert res.status_code == 200
        assert res.json() == []

    def test_get_own_notifications(self, client):
        headers = register_and_login(client)
        create_notification_for_user(client, "test@example.com", title="Reminder", message="Follow up Google")
        res = client.get(f"{BASE_URL}/notifications/", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) == 1
        assert res.json()[0]["title"] == "Reminder"
        assert res.json()[0]["is_read"] is False

    def test_cannot_see_other_users_notifications(self, client):
        register_and_login(client, email="user1@example.com")
        create_notification_for_user(client, "user1@example.com")
        headers2 = register_and_login(client, email="user2@example.com")
        res = client.get(f"{BASE_URL}/notifications/", headers=headers2)
        assert res.json() == []

    def test_requires_auth(self, client):
        res = client.get(f"{BASE_URL}/notifications/")
        assert res.status_code == 401


class TestMarkNotificationRead:
    def test_mark_as_read(self, client):
        headers = register_and_login(client)
        create_notification_for_user(client, "test@example.com")
        notif_id = client.get(f"{BASE_URL}/notifications/", headers=headers).json()[0]["id"]
        res = client.patch(f"{BASE_URL}/notifications/{notif_id}/read", headers=headers)
        assert res.status_code == 200
        assert res.json()["is_read"] is True

    def test_cannot_mark_other_users_notification(self, client):
        register_and_login(client, email="user1@example.com")
        create_notification_for_user(client, "user1@example.com")
        db = next(client.app.dependency_overrides[get_db]())
        from app.models.notification_model import Notification
        notif = db.query(Notification).first()
        headers2 = register_and_login(client, email="user2@example.com")
        res = client.patch(f"{BASE_URL}/notifications/{notif.id}/read", headers=headers2)
        assert res.status_code == 404

    def test_mark_nonexistent_notification(self, client):
        headers = register_and_login(client)
        res = client.patch(f"{BASE_URL}/notifications/nonexistent-id/read", headers=headers)
        assert res.status_code == 404