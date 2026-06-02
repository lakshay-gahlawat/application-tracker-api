from tests.conftest import register_and_login, create_application, BASE_URL


class TestCreateApplication:
    def test_create_success(self, client):
        headers = register_and_login(client)
        res = create_application(client, headers)
        assert res.status_code == 201
        data = res.json()
        assert data["company_name"] == "Google"
        assert data["role"] == "Backend Engineer"
        assert data["status"] == "applied"

    def test_create_requires_auth(self, client):
        res = client.post(f"{BASE_URL}/applications/", json={"company_name": "Google", "role": "Engineer"})
        assert res.status_code == 401

    def test_create_duplicate_application(self, client):
        headers = register_and_login(client)
        create_application(client, headers)
        res = create_application(client, headers)
        assert res.status_code == 409

    def test_create_missing_role(self, client):
        headers = register_and_login(client)
        res = client.post(f"{BASE_URL}/applications/", headers=headers, json={"company_name": "Google"})
        assert res.status_code == 422

    def test_create_missing_company(self, client):
        headers = register_and_login(client)
        res = client.post(f"{BASE_URL}/applications/", headers=headers, json={"role": "Engineer"})
        assert res.status_code == 422

    def test_create_with_optional_fields(self, client):
        headers = register_and_login(client)
        res = client.post(f"{BASE_URL}/applications/", headers=headers, json={
            "company_name": "Amazon",
            "role": "SDE",
            "notes": "Referral from friend",
            "job_link": "https://amazon.jobs/123"
        })
        assert res.status_code == 201
        assert res.json()["notes"] == "Referral from friend"


class TestGetApplications:
    def test_list_applications(self, client):
        headers = register_and_login(client)
        create_application(client, headers)
        res = client.get(f"{BASE_URL}/applications/", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 1
        assert len(data["data"]) == 1

    def test_empty_list(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/applications/", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] == 0

    def test_users_see_only_own(self, client):
        headers1 = register_and_login(client, email="user1@example.com")
        create_application(client, headers1)
        headers2 = register_and_login(client, email="user2@example.com")
        res = client.get(f"{BASE_URL}/applications/", headers=headers2)
        assert res.json()["total"] == 0

    def test_filter_by_company(self, client):
        headers = register_and_login(client)
        create_application(client, headers, company="Google", role="SWE")
        create_application(client, headers, company="Meta", role="SWE")
        res = client.get(f"{BASE_URL}/applications/?company=Google", headers=headers)
        assert res.json()["total"] == 1
        assert res.json()["data"][0]["company_name"] == "Google"

    def test_filter_by_status(self, client):
        headers = register_and_login(client)
        create_application(client, headers, company="Google", role="SWE")
        res = client.get(f"{BASE_URL}/applications/?status=applied", headers=headers)
        assert res.json()["total"] == 1

    def test_pagination(self, client):
        headers = register_and_login(client)
        for i in range(5):
            create_application(client, headers, company=f"Company{i}", role="Engineer")
        res = client.get(f"{BASE_URL}/applications/?page=1&limit=2", headers=headers)
        assert len(res.json()["data"]) == 2
        assert res.json()["pages"] >= 3

    def test_deleted_application_not_in_list(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        client.delete(f"{BASE_URL}/applications/{app_id}", headers=headers)
        res = client.get(f"{BASE_URL}/applications/", headers=headers)
        assert res.json()["total"] == 0


class TestGetApplicationById:
    def test_get_own_application(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = client.get(f"{BASE_URL}/applications/{app_id}", headers=headers)
        assert res.status_code == 200
        assert res.json()["id"] == app_id

    def test_cannot_get_other_users_application(self, client):
        headers1 = register_and_login(client, email="user1@example.com")
        app_id = create_application(client, headers1).json()["id"]
        headers2 = register_and_login(client, email="user2@example.com")
        res = client.get(f"{BASE_URL}/applications/{app_id}", headers=headers2)
        assert res.status_code == 404

    def test_get_nonexistent(self, client):
        headers = register_and_login(client)
        res = client.get(f"{BASE_URL}/applications/nonexistent-id", headers=headers)
        assert res.status_code == 404


class TestUpdateApplication:
    def test_update_success(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = client.put(f"{BASE_URL}/applications/{app_id}", headers=headers, json={
            "company_name": "Microsoft", "role": "Senior Engineer"
        })
        assert res.status_code == 200
        assert res.json()["company_name"] == "Microsoft"

    def test_update_notes(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = client.put(f"{BASE_URL}/applications/{app_id}", headers=headers, json={
            "company_name": "Google", "role": "Backend Engineer", "notes": "Great opportunity"
        })
        assert res.status_code == 200
        assert res.json()["notes"] == "Great opportunity"

    def test_cannot_update_other_users(self, client):
        headers1 = register_and_login(client, email="user1@example.com")
        app_id = create_application(client, headers1).json()["id"]
        headers2 = register_and_login(client, email="user2@example.com")
        res = client.put(f"{BASE_URL}/applications/{app_id}", headers=headers2, json={"company_name": "Hack"})
        assert res.status_code == 404


class TestDeleteApplication:
    def test_soft_delete(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = client.delete(f"{BASE_URL}/applications/{app_id}", headers=headers)
        assert res.status_code == 200
        # Soft delete — not visible anymore
        gone = client.get(f"{BASE_URL}/applications/{app_id}", headers=headers)
        assert gone.status_code == 404

    def test_cannot_delete_other_users(self, client):
        headers1 = register_and_login(client, email="user1@example.com")
        app_id = create_application(client, headers1).json()["id"]
        headers2 = register_and_login(client, email="user2@example.com")
        res = client.delete(f"{BASE_URL}/applications/{app_id}", headers=headers2)
        assert res.status_code == 404


class TestUpdateApplicationStatus:
    def test_applied_to_interviewing(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = client.patch(f"{BASE_URL}/applications/{app_id}/status", headers=headers, json={
            "status": "interviewing"
        })
        assert res.status_code == 200
        assert res.json()["status"] == "interviewing"

    def test_applied_to_rejected(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = client.patch(f"{BASE_URL}/applications/{app_id}/status", headers=headers, json={
            "status": "rejected"
        })
        assert res.status_code == 200
        assert res.json()["status"] == "rejected"

    def test_applied_to_ghosted(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = client.patch(f"{BASE_URL}/applications/{app_id}/status", headers=headers, json={
            "status": "ghosted"
        })
        assert res.status_code == 200

    def test_invalid_transition_applied_to_accepted(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = client.patch(f"{BASE_URL}/applications/{app_id}/status", headers=headers, json={
            "status": "accepted"
        })
        assert res.status_code == 400

    def test_same_status_rejected(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        res = client.patch(f"{BASE_URL}/applications/{app_id}/status", headers=headers, json={
            "status": "applied"
        })
        assert res.status_code == 400

    def test_full_flow_to_offer(self, client):
        headers = register_and_login(client)
        app_id = create_application(client, headers).json()["id"]
        client.patch(f"{BASE_URL}/applications/{app_id}/status", headers=headers, json={"status": "interviewing"})
        res = client.patch(f"{BASE_URL}/applications/{app_id}/status", headers=headers, json={"status": "offer"})
        assert res.status_code == 200
        assert res.json()["status"] == "offer"