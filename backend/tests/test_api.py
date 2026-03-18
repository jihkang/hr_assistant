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
        db.add(
            User(
                name="일반 사원",
                email="staff@example.com",
                password_hash=hash_password("Password123!"),
                department=Department.SALES,
                rank=Rank.STAFF,
                hire_date=date(2024, 1, 15),
                annual_leave_total=15,
                annual_leave_used=1,
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


def test_hr_admin_can_list_users(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "hr-admin@example.com", "password": "Password123!"},
    )
    assert login_response.status_code == 200

    response = client.get("/api/v1/admin/users")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 3
    assert [user["email"] for user in payload["users"]] == [
        "dev-gm@example.com",
        "hr-admin@example.com",
        "staff@example.com",
    ]
    assert payload["users"][1]["is_admin"] is True
    assert payload["users"][2]["is_admin"] is False


def test_non_hr_admin_cannot_list_users(client: TestClient) -> None:
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "내 연차 잔여 일수 알려줘"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "인사 관리자" in payload["answer"]
    assert "13일" in payload["answer"]
    assert payload["citations"]
    assert payload["citations"][0]["source"] == "USER_LEAVE_BALANCE"


def test_assistant_chat_blocks_other_employee_leave_lookup_before_model_call(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "dev-gm@example.com", "password": "Password123!"},
    )
    assert login_response.status_code == 200

    response = client.get("/api/v1/admin/users")

    assert response.status_code == 403
    assert response.json()["detail"] == "HR admin access required."
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "인사 관리자의 연차 잔여 일수 알려줘"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You can only access your own leave information."


def test_assistant_chat_returns_asset_response_with_citations(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "dev-gm@example.com", "password": "Password123!"},
    )
    assert login_response.status_code == 200

    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "대여 가능한 모니터 알려줘"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "현재 대여 가능한 모니터는 2대" in payload["answer"]
    assert len(payload["citations"]) == 2
    assert {citation["source"] for citation in payload["citations"]} == {
        "ASSET_INVENTORY",
        "GA_POLICY_2026_01",
    }
