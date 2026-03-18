from datetime import timedelta

import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from hr_assistant_backend.api.dependencies import (
    build_user_summary,
    get_current_user,
    require_hr_admin,
    update_last_login,
)
from hr_assistant_backend.core.config import settings
from hr_assistant_backend.core.database import get_db
from hr_assistant_backend.core.security import create_token, decode_token, hash_password, verify_password
from hr_assistant_backend.models.user import User
from hr_assistant_backend.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from hr_assistant_backend.schemas.user import MeResponse, UserListResponse

router = APIRouter(prefix="/auth", tags=["auth"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _issue_tokens(user_id: str) -> tuple[str, str]:
    access_token = create_token(
        subject=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = create_token(
        subject=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )
    return access_token, refresh_token


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    common_kwargs = {
        "httponly": True,
        "secure": settings.cookie_secure,
        "samesite": settings.cookie_samesite,
        "path": "/",
    }
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        **common_kwargs,
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        **common_kwargs,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.access_cookie_name, path="/")
    response.delete_cookie(settings.refresh_cookie_name, path="/")


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> LoginResponse:
    email = _normalize_email(payload.email)
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    update_last_login(user)
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token, refresh_token = _issue_tokens(user.id)
    _set_auth_cookies(response, access_token, refresh_token)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        name=user.name,
        department=user.department,
        user=build_user_summary(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    _clear_auth_cookies(response)
    return response


@router.post("/refresh", response_model=LoginResponse)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=settings.refresh_cookie_name),
    db: Session = Depends(get_db),
) -> LoginResponse:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing.",
        )

    try:
        payload = decode_token(refresh_token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        ) from exc

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type.",
        )

    user = db.get(User, payload.get("sub"))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
        )

    access_token, new_refresh_token = _issue_tokens(user.id)
    _set_auth_cookies(response, access_token, new_refresh_token)
    return LoginResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        name=user.name,
        department=user.department,
        user=build_user_summary(user),
    )


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(user=build_user_summary(current_user))


def _create_user(payload: RegisterRequest, db: Session) -> User:
    email = _normalize_email(payload.email)
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        )

    user = User(
        name=payload.name,
        email=email,
        password_hash=hash_password(payload.password),
        department=payload.department,
        rank=payload.rank,
        hire_date=payload.hire_date,
        annual_leave_total=payload.annual_leave_total,
        annual_leave_used=payload.annual_leave_used,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_hr_admin),
) -> RegisterResponse:
    user = _create_user(payload, db)
    return RegisterResponse(message="User created successfully.", user=build_user_summary(user))


@admin_router.post("/users", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def create_user_from_admin(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_hr_admin),
) -> RegisterResponse:
    user = _create_user(payload, db)
    return RegisterResponse(message="User created successfully.", user=build_user_summary(user))


@admin_router.get("/users", response_model=UserListResponse)
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_hr_admin),
) -> UserListResponse:
    users = db.scalars(select(User).order_by(User.email.asc())).all()
    summaries = [build_user_summary(user) for user in users]
    return UserListResponse(total=len(summaries), users=summaries)
