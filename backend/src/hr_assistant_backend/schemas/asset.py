from datetime import datetime

from pydantic import BaseModel

from hr_assistant_backend.models.asset import AssetStatus, RentalStatus
from hr_assistant_backend.models.user import Department


class AssetSummary(BaseModel):
    id: str
    name: str
    category: str
    serial_number: str | None
    status: AssetStatus
    location: str | None
    owner_department: Department | None
    requires_approval: bool


class AssetListResponse(BaseModel):
    items: list[AssetSummary]
    total: int


class AssetDetailResponse(BaseModel):
    asset: AssetSummary


class RentalRequest(BaseModel):
    note: str | None = None


class RentalSummary(BaseModel):
    id: str
    asset_id: str
    user_id: str
    approved_by: str | None
    requested_at: datetime
    approved_at: datetime | None
    returned_at: datetime | None
    status: RentalStatus
    note: str | None


class RentalResponse(BaseModel):
    rental: RentalSummary
    asset: AssetSummary


class RentalListResponse(BaseModel):
    items: list[RentalSummary]
    total: int
