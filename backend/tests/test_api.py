from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from hr_assistant_backend.core.database import get_db
from hr_assistant_backend.core.security import hash_password
from hr_assistant_backend.main import app
from hr_assistant_backend.models.base import Base
from hr_assistant_backend.models.user import Department, Rank, User


@pytest.fixture
def client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with testing_session_local() as db:
        db.add(
            User(
                name="인사 관리자",
                email="hr-admin@example.com",
                password_hash=hash_password("Password123!"),
                department=Department.HR,
                rank=Rank.MANAGER,
                hire_date=date(2022, 1, 1),
                annual_leave_total=15,
                annual_leave_used=2,
            )
        )
        db.add(
            User(
                name="개발 부장",
                email="dev-gm@example.com",
                password_hash=hash_password("Password123!"),
                department=Department.DEVELOPMENT,
                rank=Rank.GENERAL_MANAGER,
                hire_date=date(2021, 6, 1),
                annual_leave_total=18,
                annual_leave_used=4,
            )
        )
        db.commit()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_returns_tokens_name_and_department(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "hr-admin@example.com", "password": "Password123!"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["name"] == "인사 관리자"
    assert payload["department"] == "인사"
    assert response.cookies.get("hr_access_token")
    assert response.cookies.get("hr_refresh_token")


def test_hr_admin_can_register_user(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "hr-admin@example.com", "password": "Password123!"},
    )
    assert login_response.status_code == 200

    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "신규 직원",
            "email": "new-user@example.com",
            "password": "Password123!",
            "department": "영업",
            "rank": "사원",
            "hire_date": "2026-03-17",
            "annual_leave_total": 15,
            "annual_leave_used": 0,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["user"]["name"] == "신규 직원"
    assert payload["user"]["department"] == "영업"
    assert payload["user"]["is_admin"] is False


def test_non_hr_admin_can_create_user_via_admin_endpoint(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "dev-gm@example.com", "password": "Password123!"},
    )
    assert login_response.status_code == 200

    response = client.post(
        "/api/v1/admin/users",
        json={
            "name": "총무 승인 사용자",
            "email": "ga-approved@example.com",
            "password": "Password123!",
            "department": "운영",
            "rank": "사원",
            "hire_date": "2026-03-17",
            "annual_leave_total": 15,
            "annual_leave_used": 0,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["user"]["email"] == "ga-approved@example.com"
    assert payload["user"]["is_admin"] is False


def test_non_hr_admin_cannot_register_user(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "dev-gm@example.com", "password": "Password123!"},
    )
    assert login_response.status_code == 200

    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "권한 없는 생성 시도",
            "email": "blocked@example.com",
            "password": "Password123!",
            "department": "마케팅",
            "rank": "사원",
            "hire_date": "2026-03-17",
            "annual_leave_total": 15,
            "annual_leave_used": 0,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "HR admin access required."
