def register_test_user(
    client,
    name="Lakshay",
    email="lakshay@test.com",
    password="test1234"
):

    return client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password
        }
    )


def login_test_user(
    client,
    email="lakshay@test.com",
    password="test1234"
):

    return client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )


def get_auth_headers(
    client,
    email,
    password="test1234"
):
    login_response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }