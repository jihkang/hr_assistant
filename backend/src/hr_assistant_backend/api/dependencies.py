from datetime import UTC, datetime
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from hr_assistant_backend.core.config import settings
from hr_assistant_backend.core.database import get_db
from hr_assistant_backend.core.security import decode_token
from hr_assistant_backend.models.user import Department, Rank, User

RANK_ORDER = {
    Rank.PRESIDENT: 7,
    Rank.VICE_PRESIDENT: 6,
    Rank.DIRECTOR: 5,
    Rank.GENERAL_MANAGER: 4,
    Rank.MANAGER: 3,
    Rank.ASSISTANT_MANAGER: 2,
    Rank.STAFF: 1,
}


def is_admin_user(user: User) -> bool:
    threshold = Rank.MANAGER if user.department == Department.HR else Rank.GENERAL_MANAGER
    return RANK_ORDER[user.rank] >= RANK_ORDER[threshold]


def is_hr_admin_user(user: User) -> bool:
    return user.department == Department.HR and is_admin_user(user)


def build_user_summary(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "department": user.department,
        "rank": user.rank,
        "is_admin": is_admin_user(user),
    }


def get_current_user(
    db: Session = Depends(get_db),
    access_token: Annotated[str | None, Cookie(alias=settings.access_cookie_name)] = None,
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    try:
        payload = decode_token(access_token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
        ) from exc

    if payload.get("type") != "access":
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

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not is_admin_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


def require_hr_admin(current_user: User = Depends(get_current_user)) -> User:
    if not is_hr_admin_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR admin access required.",
        )
    return current_user


def update_last_login(user: User) -> None:
    user.last_login_at = datetime.now(UTC)
