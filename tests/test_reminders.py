from tests.conftest import register_and_login, create_application, BASE_URL

FUTURE_DATE = "2099-12-01T10:00:00"


def create_reminder(client, headers, application_id, date=FUTURE_DATE, message="Follow up"):
    return client.post(f"{BASE_URL}/reminders/", headers=headers, json={
        "application_id": application_id,
        "message": message,
        "reminder_date": date
    })


class TestCreateReminder:
    def test_create_success(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = create_reminder(client, headers, app_id)
        assert res.status_code == 201
        data = res.json()
        assert data["message"] == "Follow up"
        assert data["is_done"] is False

    def test_create_requires_auth(self, client):
        res = client.post(f"{BASE_URL}/reminders/", json={
            "application_id": "fake-id", "reminder_date": FUTURE_DATE
        })
        assert res.status_code == 401

    def test_cannot_create_for_other_users_application(self, client):
        headers1 = register_and_login(client, email="user1@example.com")
        app_id = create_application(client, headers1).json()["id"]
        headers2 = register_and_login(client, email="user2@example.com")
        res = create_reminder(client, headers2, app_id)
        assert res.status_code == 404

    def test_create_for_nonexistent_application(self, client):
        headers = register_and_login(client)
        res = create_reminder(client, headers, "nonexistent-id")
        assert res.status_code == 404

    def test_duplicate_reminder_same_date(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        create_reminder(client, headers, app_id)
        res = create_reminder(client, headers, app_id)
        assert res.status_code == 409


class TestGetReminders:
    def test_get_own_reminders(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        create_reminder(client, headers, app_id)
        res = client.get(f"{BASE_URL}/reminders/", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_cannot_see_other_users_reminders(self, client):
        headers1 = register_and_login(client, email="user1@example.com")
        app_id = create_application(client, headers1).json()["id"]
        create_reminder(client, headers1, app_id)
        headers2 = register_and_login(client, email="user2@example.com")
        res = client.get(f"{BASE_URL}/reminders/", headers=headers2)
        assert len(res.json()) == 0

    def test_empty_reminders(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/reminders/", headers=headers)
        assert res.status_code == 200
        assert res.json() == []

    def test_multiple_reminders(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        create_reminder(client, headers, app_id, date="2099-01-01T10:00:00", message="First")
        create_reminder(client, headers, app_id, date="2099-02-01T10:00:00", message="Second")
        res = client.get(f"{BASE_URL}/reminders/", headers=headers)
        assert len(res.json()) == 2


class TestCompleteReminder:
    def test_complete_own_reminder(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        reminder_id = create_reminder(client, headers, app_id).json()["id"]
        res = client.patch(f"{BASE_URL}/reminders/{reminder_id}/complete", headers=headers)
        assert res.status_code == 200
        assert res.json()["is_done"] is True

    def test_cannot_complete_already_done(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        reminder_id = create_reminder(client, headers, app_id).json()["id"]
        client.patch(f"{BASE_URL}/reminders/{reminder_id}/complete", headers=headers)
        res = client.patch(f"{BASE_URL}/reminders/{reminder_id}/complete", headers=headers)
        assert res.status_code == 400

    def test_cannot_complete_other_users_reminder(self, client):
        headers1 = register_and_login(client, email="user1@example.com")
        app_id = create_application(client, headers1).json()["id"]
        reminder_id = create_reminder(client, headers1, app_id).json()["id"]
        headers2 = register_and_login(client, email="user2@example.com")
        res = client.patch(f"{BASE_URL}/reminders/{reminder_id}/complete", headers=headers2)
        assert res.status_code == 404


class TestTodayReminders:
    def test_get_today_reminders_returns_list(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/reminders/today", headers=headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_today_requires_auth(self, client):
        res = client.get(f"{BASE_URL}/reminders/today")
        assert res.status_code == 401