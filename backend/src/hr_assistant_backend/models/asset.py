from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hr_assistant_backend.models.base import Base
from hr_assistant_backend.models.user import Department


class AssetStatus(str, Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class RentalStatus(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    DENIED = "denied"
    RETURNED = "returned"


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(255), unique=True)
    status: Mapped[AssetStatus] = mapped_column(
        SqlEnum(AssetStatus, native_enum=False),
        nullable=False,
        default=AssetStatus.AVAILABLE,
    )
    location: Mapped[str | None] = mapped_column(String(255))
    owner_department: Mapped[Department | None] = mapped_column(SqlEnum(Department, native_enum=False))
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    rentals: Mapped[list[AssetRental]] = relationship(back_populates="asset")


class AssetRental(Base):
    __tablename__ = "asset_rentals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    asset_id: Mapped[str] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    approved_by: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[RentalStatus] = mapped_column(SqlEnum(RentalStatus, native_enum=False), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    asset: Mapped[Asset] = relationship(back_populates="rentals")
