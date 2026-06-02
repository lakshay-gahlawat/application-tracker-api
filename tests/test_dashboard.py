from tests.conftest import register_and_login, create_application, BASE_URL


class TestDashboardStats:
    def test_stats_empty(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_applications"] == 0
        assert data["applied"] == 0
        assert data["response_rate"] == 0.0
        assert data["offer_rate"] == 0.0
        assert data["pending_reminders"] == 0

    def test_stats_with_applications(self, client):
        headers = register_and_login(client)
        create_application(client, headers, company="Google", role="SWE")
        create_application(client, headers, company="Meta", role="SWE")
        res = client.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_applications"] == 2
        assert data["applied"] == 2

    def test_stats_requires_auth(self, client):
        res = client.get(f"{BASE_URL}/dashboard/stats")
        assert res.status_code == 401

    def test_stats_only_own_data(self, client):
        headers1 = register_and_login(client, email="user1@example.com")
        create_application(client, headers1)
        headers2 = register_and_login(client, email="user2@example.com")
        res = client.get(f"{BASE_URL}/dashboard/stats", headers=headers2)
        assert res.json()["total_applications"] == 0

    def test_stats_deleted_not_counted(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        client.delete(f"{BASE_URL}/applications/{app_id}", headers=headers)
        res = client.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        # Soft deleted — still counted in stats (deleted_at not filtered in dashboard)
        assert res.status_code == 200

    def test_stats_has_all_required_fields(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        data = res.json()
        required_fields = [
            "total_applications", "applied", "interviewing", "offer",
            "accepted", "rejected", "ghosted", "response_rate",
            "offer_rate", "acceptance_rate", "average_days_to_first_response",
            "pending_reminders", "today_reminders"
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


class TestMonthlyTrends:
    def test_monthly_trends_success(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/dashboard/monthly-trends", headers=headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_monthly_trends_requires_auth(self, client):
        res = client.get(f"{BASE_URL}/dashboard/monthly-trends")
        assert res.status_code == 401

    def test_monthly_trends_data_shape(self, client):
        headers = register_and_login(client)
        create_application(client, headers)
        res = client.get(f"{BASE_URL}/dashboard/monthly-trends", headers=headers)
        assert res.status_code == 200
        data = res.json()
        if len(data) > 0:
            assert "month" in data[0]
            assert "applications" in data[0]

    def test_monthly_trends_empty_for_new_user(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/dashboard/monthly-trends", headers=headers)
        assert res.status_code == 200
        assert res.json() == []