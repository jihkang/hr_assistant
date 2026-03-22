from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from hr_assistant_backend.core.database import get_db
from hr_assistant_backend.core.security import hash_password
from hr_assistant_backend.main import app
from hr_assistant_backend.models.asset import Asset, AssetRental, AssetStatus, RentalStatus
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
        hr_admin = User(
            name="인사 관리자",
            email="hr-admin@example.com",
            password_hash=hash_password("Password123!"),
            department=Department.HR,
            rank=Rank.MANAGER,
            hire_date=date(2022, 1, 1),
            annual_leave_total=15,
            annual_leave_used=2,
        )
        dev_admin = User(
            name="개발 부장",
            email="dev-gm@example.com",
            password_hash=hash_password("Password123!"),
            department=Department.DEVELOPMENT,
            rank=Rank.GENERAL_MANAGER,
            hire_date=date(2021, 6, 1),
            annual_leave_total=18,
            annual_leave_used=4,
        )
        employee = User(
            name="일반 직원",
            email="staff@example.com",
            password_hash=hash_password("Password123!"),
            department=Department.DEVELOPMENT,
            rank=Rank.STAFF,
            hire_date=date(2024, 3, 1),
            annual_leave_total=15,
            annual_leave_used=1,
        )
        db.add_all([hr_admin, dev_admin, employee])
        db.flush()

        available_asset = Asset(
            name="ThinkPad X1 Carbon",
            category="노트북",
            serial_number="SN-001",
            status=AssetStatus.AVAILABLE,
            location="HQ-3F",
            owner_department=Department.DEVELOPMENT,
            requires_approval=False,
        )
        approval_asset = Asset(
            name="Jabra Speak 750",
            category="회의 장비",
            serial_number="SN-002",
            status=AssetStatus.AVAILABLE,
            location="HQ-5F",
            owner_department=Department.HR,
            requires_approval=True,
        )
        rented_asset = Asset(
            name="Dell 27 Monitor",
            category="모니터",
            serial_number="SN-003",
            status=AssetStatus.RENTED,
            location="HQ-2F",
            owner_department=Department.DEVELOPMENT,
            requires_approval=False,
        )
        db.add_all([available_asset, approval_asset, rented_asset])
        db.flush()

        db.add(
            AssetRental(
                asset_id=rented_asset.id,
                user_id=employee.id,
                approved_by=dev_admin.id,
                status=RentalStatus.APPROVED,
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


def _login(client: TestClient, email: str, password: str = "Password123!") -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200


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
    _login(client, "hr-admin@example.com")

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
    _login(client, "dev-gm@example.com")

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


def test_authenticated_user_can_list_and_filter_assets(client: TestClient) -> None:
    _login(client, "staff@example.com")

    response = client.get("/api/v1/assets", params={"available_only": True, "category": "노트북"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "ThinkPad X1 Carbon"
    assert payload["items"][0]["status"] == "available"


def test_user_can_request_rental_for_available_asset(client: TestClient) -> None:
    _login(client, "staff@example.com")
    asset_id = client.get("/api/v1/assets", params={"category": "노트북"}).json()["items"][0]["id"]

    response = client.post(
        f"/api/v1/assets/{asset_id}/rentals",
        json={"note": "외근용 노트북이 필요합니다."},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["rental"]["status"] == "approved"
    assert payload["rental"]["asset_id"] == asset_id
    assert payload["asset"]["status"] == "rented"


def test_admin_can_approve_requested_rental(client: TestClient) -> None:
    _login(client, "staff@example.com")
    asset_id = client.get("/api/v1/assets", params={"category": "회의 장비"}).json()["items"][0]["id"]
    create_response = client.post(
        f"/api/v1/assets/{asset_id}/rentals",
        json={"note": "회의 진행용으로 신청합니다."},
    )
    rental_id = create_response.json()["rental"]["id"]

    _login(client, "dev-gm@example.com")
    approve_response = client.post(f"/api/v1/admin/rentals/{rental_id}/approve")

    assert approve_response.status_code == 200
    payload = approve_response.json()
    assert payload["rental"]["status"] == "approved"
    assert payload["asset"]["status"] == "rented"


def test_admin_can_return_approved_rental(client: TestClient) -> None:
    _login(client, "staff@example.com")
    rentals_response = client.get("/api/v1/users/me/rentals")
    rental_id = rentals_response.json()["items"][0]["id"]

    _login(client, "dev-gm@example.com")
    response = client.post(f"/api/v1/admin/rentals/{rental_id}/return")

    assert response.status_code == 200
    payload = response.json()
    assert payload["rental"]["status"] == "returned"
    assert payload["asset"]["status"] == "available"
    assert payload["rental"]["returned_at"] is not None


def test_non_admin_cannot_approve_rental(client: TestClient) -> None:
    _login(client, "staff@example.com")
    asset_id = client.get("/api/v1/assets", params={"category": "회의 장비"}).json()["items"][0]["id"]
    create_response = client.post(
        f"/api/v1/assets/{asset_id}/rentals",
        json={"note": "권한 체크용 신청입니다."},
    )
    rental_id = create_response.json()["rental"]["id"]

    response = client.post(f"/api/v1/admin/rentals/{rental_id}/approve")

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required."
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
