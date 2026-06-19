import os
os.environ["TESTING"] = "true"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database.session import Base
from app.dependencies.deps import get_db
from app.core.config import TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ── helpers ───────────────────────────────────────────────────────────────────

BASE_URL = "/api/v1"


def register_user(client, email="test@example.com", password="testpass1"):
    client.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    return {"email": email, "password": password}


def get_auth_headers(client, email="test@example.com", password="testpass1"):
    res = client.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def register_and_login(client, email="test@example.com", password="testpass1"):
    register_user(client, email, password)
    return get_auth_headers(client, email, password)


def register_and_login_admin(client, email="admin@example.com", password="adminpass1"):
    """Register a user then manually set their role to admin in DB."""
    register_user(client, email, password)
    # Promote to admin via direct DB — only way since there's no promote endpoint
    from app.models.user_model import User
    from app.models.enums import UserRole
    # Get db from the client's override
    db = next(client.app.dependency_overrides[get_db]())
    user = db.query(User).filter(User.email == email).first()
    user.role = UserRole.ADMIN
    db.commit()
    return get_auth_headers(client, email, password)


def create_application(client, headers, company="Google", role="Backend Engineer"):
    return client.post(f"{BASE_URL}/applications/", headers=headers, json={
        "company_name": company,
        "role": role,
    })