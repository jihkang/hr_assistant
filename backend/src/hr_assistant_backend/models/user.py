from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, Computed, Date, DateTime, Enum as SqlEnum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from hr_assistant_backend.models.base import Base


class Department(str, Enum):
    HR = "인사"
    DEVELOPMENT = "개발"
    MARKETING = "마케팅"
    FINANCE = "재무"
    SALES = "영업"
    OPERATIONS = "운영"


class Rank(str, Enum):
    PRESIDENT = "사장"
    VICE_PRESIDENT = "부사장"
    DIRECTOR = "부서장"
    GENERAL_MANAGER = "부장"
    MANAGER = "과장"
    ASSISTANT_MANAGER = "대리"
    STAFF = "사원"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[Department] = mapped_column(
        SqlEnum(Department, native_enum=False),
        nullable=False,
    )
    rank: Mapped[Rank] = mapped_column(
        SqlEnum(Rank, native_enum=False),
        nullable=False,
    )
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    annual_leave_total: Mapped[int] = mapped_column(Integer, nullable=False)
    annual_leave_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    annual_leave_remaining: Mapped[int] = mapped_column(
        Integer,
        Computed("annual_leave_total - annual_leave_used"),
        nullable=False,
    )
    employment_status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
