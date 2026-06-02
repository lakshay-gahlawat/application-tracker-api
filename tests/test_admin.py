from tests.conftest import register_and_login, register_user, get_auth_headers, BASE_URL
from tests.conftest import register_and_login, BASE_URL
from app.models.user_model import User
from app.models.enums import UserRole
from app.dependencies.deps import get_db


def promote_to_admin(client, email):
    """Helper to promote a user to admin directly via DB."""
    db = next(client.app.dependency_overrides[get_db]())
    user = db.query(User).filter(User.email == email).first()
    user.role = UserRole.ADMIN
    db.commit()


class TestAdminAccess:
    def test_admin_me_success(self, client):
        register_and_login(client, email="admin@example.com")
        promote_to_admin(client, "admin@example.com")
        from tests.conftest import get_auth_headers
        headers = get_auth_headers(client, email="admin@example.com")
        res = client.get(f"{BASE_URL}/admin/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["role"] == "admin"

    def test_regular_user_cannot_access_admin(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/admin/me", headers=headers)
        assert res.status_code == 403

    def test_admin_requires_auth(self, client):
        res = client.get(f"{BASE_URL}/admin/me")
        assert res.status_code == 401


class TestAdminGetUsers:
    def test_admin_can_list_all_users(self, client):
        # Register all users first
        register_user(client, email="user1@example.com")
        register_user(client, email="user2@example.com")
        register_user(client, email="admin@example.com")

        # Then promote admin
        promote_to_admin(client, "admin@example.com")

        # Then login as admin
        headers = get_auth_headers(client, email="admin@example.com")

        res = client.get(f"{BASE_URL}/admin/users", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) >= 3

    def test_regular_user_cannot_list_users(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/admin/users", headers=headers)
        assert res.status_code == 403


class TestAdminAuditLogs:
    def test_admin_can_get_audit_logs(self, client):
        register_and_login(client, email="admin@example.com")
        promote_to_admin(client, "admin@example.com")
        from tests.conftest import get_auth_headers, create_application
        headers = get_auth_headers(client, email="admin@example.com")
        create_application(client, headers)  # This creates an audit log
        res = client.get(f"{BASE_URL}/admin/audit-logs", headers=headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_regular_user_cannot_get_audit_logs(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/admin/audit-logs", headers=headers)
        assert res.status_code == 403