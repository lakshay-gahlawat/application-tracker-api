from tests.conftest import register_user, register_and_login, BASE_URL


class TestRegister:
    def test_register_success(self, client):
        res = client.post(f"{BASE_URL}/auth/register", json={
            "email": "new@example.com", "password": "testpass1"
        })
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "new@example.com"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client):
        payload = {"email": "dup@example.com", "password": "testpass1"}
        client.post(f"{BASE_URL}/auth/register", json=payload)
        res = client.post(f"{BASE_URL}/auth/register", json=payload)
        assert res.status_code == 409

    def test_register_missing_password(self, client):
        res = client.post(f"{BASE_URL}/auth/register", json={"email": "x@x.com"})
        assert res.status_code == 422

    def test_register_missing_email(self, client):
        res = client.post(f"{BASE_URL}/auth/register", json={"password": "testpass1"})
        assert res.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        register_user(client)
        res = client.post(f"{BASE_URL}/auth/login", json={
            "email": "test@example.com", "password": "testpass1"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"

    def test_login_wrong_password(self, client):
        register_user(client)
        res = client.post(f"{BASE_URL}/auth/login", json={
            "email": "test@example.com", "password": "wrongpass"
        })
        assert res.status_code == 401

    def test_login_unknown_email(self, client):
        res = client.post(f"{BASE_URL}/auth/login", json={
            "email": "ghost@example.com", "password": "testpass1"
        })
        assert res.status_code == 401


class TestGetMe:
    def test_get_me_success(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/users/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["email"] == "test@example.com"

    def test_get_me_no_token(self, client):
        res = client.get(f"{BASE_URL}/users/me")
        assert res.status_code == 401

    def test_get_me_invalid_token(self, client):
        res = client.get(f"{BASE_URL}/users/me", headers={"Authorization": "Bearer badtoken"})
        assert res.status_code == 401


class TestUpdateUser:
    def test_update_email_success(self, client):
        headers = register_and_login(client)
        res = client.put(f"{BASE_URL}/users/me", json={"email": "updated@example.com"}, headers=headers)
        assert res.status_code == 200
        assert res.json()["email"] == "updated@example.com"

    def test_update_duplicate_email(self, client):
        register_user(client, email="other@example.com")
        headers = register_and_login(client, email="main@example.com")
        res = client.put(f"{BASE_URL}/users/me", json={"email": "other@example.com"}, headers=headers)
        assert res.status_code == 409

    def test_update_requires_auth(self, client):
        res = client.put(f"{BASE_URL}/users/me", json={"email": "x@x.com"})
        assert res.status_code == 401


class TestDeleteUser:
    def test_delete_success(self, client):
        headers = register_and_login(client)
        res = client.delete(f"{BASE_URL}/users/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["message"] == "User deleted successfully"

    def test_deleted_user_cannot_login(self, client):
        headers = register_and_login(client)
        client.delete(f"{BASE_URL}/users/me", headers=headers)
        res = client.post(f"{BASE_URL}/auth/login", json={
            "email": "test@example.com", "password": "testpass1"
        })
        assert res.status_code == 401

    def test_delete_requires_auth(self, client):
        res = client.delete(f"{BASE_URL}/users/me")
        assert res.status_code == 401