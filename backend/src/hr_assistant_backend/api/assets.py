from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from hr_assistant_backend.api.dependencies import get_current_user, require_admin
from hr_assistant_backend.core.database import get_db
from hr_assistant_backend.models.asset import Asset, AssetRental, AssetStatus, RentalStatus
from hr_assistant_backend.models.user import User
from hr_assistant_backend.schemas.asset import (
    AssetDetailResponse,
    AssetListResponse,
    AssetSummary,
    RentalListResponse,
    RentalRequest,
    RentalResponse,
    RentalSummary,
)

router = APIRouter(tags=["assets"])
admin_router = APIRouter(prefix="/admin", tags=["admin-assets"])


def _to_asset_summary(asset: Asset) -> AssetSummary:
    return AssetSummary.model_validate(asset, from_attributes=True)


def _to_rental_summary(rental: AssetRental) -> RentalSummary:
    return RentalSummary.model_validate(rental, from_attributes=True)


def _get_asset_or_404(db: Session, asset_id: str) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found.")
    return asset


def _get_rental_or_404(db: Session, rental_id: str) -> AssetRental:
    rental = db.get(AssetRental, rental_id)
    if rental is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rental not found.")
    return rental


def _ensure_asset_can_be_requested(asset: Asset) -> None:
    if asset.status != AssetStatus.AVAILABLE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Asset is not available.")


def _sync_asset_status(asset: Asset, rental_status: RentalStatus) -> None:
    asset.status = AssetStatus.AVAILABLE if rental_status in {RentalStatus.DENIED, RentalStatus.RETURNED} else AssetStatus.RENTED


@router.get("/assets", response_model=AssetListResponse)
def list_assets(
    category: str | None = Query(default=None),
    available_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AssetListResponse:
    query = select(Asset)
    if category:
        query = query.where(Asset.category == category)
    if available_only:
        query = query.where(Asset.status == AssetStatus.AVAILABLE)

    items = db.scalars(query.order_by(Asset.name)).all()
    summaries = [_to_asset_summary(asset) for asset in items]
    return AssetListResponse(items=summaries, total=len(summaries))


@router.get("/assets/{asset_id}", response_model=AssetDetailResponse)
def get_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> AssetDetailResponse:
    return AssetDetailResponse(asset=_to_asset_summary(_get_asset_or_404(db, asset_id)))


@router.get("/users/me/rentals", response_model=RentalListResponse)
def list_my_rentals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RentalListResponse:
    rentals = db.scalars(
        select(AssetRental)
        .where(AssetRental.user_id == current_user.id)
        .order_by(AssetRental.requested_at.desc())
    ).all()
    items = [_to_rental_summary(rental) for rental in rentals]
    return RentalListResponse(items=items, total=len(items))


@router.post("/assets/{asset_id}/rentals", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def request_rental(
    asset_id: str,
    payload: RentalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RentalResponse:
    asset = _get_asset_or_404(db, asset_id)
    _ensure_asset_can_be_requested(asset)

    rental_status = RentalStatus.REQUESTED if asset.requires_approval else RentalStatus.APPROVED
    approved_at = datetime.now(UTC) if rental_status == RentalStatus.APPROVED else None
    approved_by = current_user.id if rental_status == RentalStatus.APPROVED else None

    rental = AssetRental(
        asset_id=asset.id,
        user_id=current_user.id,
        approved_by=approved_by,
        approved_at=approved_at,
        status=rental_status,
        note=payload.note,
    )
    _sync_asset_status(asset, rental_status)

    db.add(rental)
    db.add(asset)
    db.commit()
    db.refresh(rental)
    db.refresh(asset)
    return RentalResponse(rental=_to_rental_summary(rental), asset=_to_asset_summary(asset))


@admin_router.post("/rentals/{rental_id}/approve", response_model=RentalResponse)
def approve_rental(
    rental_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RentalResponse:
    rental = _get_rental_or_404(db, rental_id)
    if rental.status != RentalStatus.REQUESTED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only requested rentals can be approved.")

    asset = _get_asset_or_404(db, rental.asset_id)
    rental.status = RentalStatus.APPROVED
    rental.approved_by = current_user.id
    rental.approved_at = datetime.now(UTC)
    _sync_asset_status(asset, rental.status)

    db.add_all([rental, asset])
    db.commit()
    db.refresh(rental)
    db.refresh(asset)
    return RentalResponse(rental=_to_rental_summary(rental), asset=_to_asset_summary(asset))


@admin_router.post("/rentals/{rental_id}/deny", response_model=RentalResponse)
def deny_rental(
    rental_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> RentalResponse:
    rental = _get_rental_or_404(db, rental_id)
    if rental.status != RentalStatus.REQUESTED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only requested rentals can be denied.")

    asset = _get_asset_or_404(db, rental.asset_id)
    rental.status = RentalStatus.DENIED
    _sync_asset_status(asset, rental.status)

    db.add_all([rental, asset])
    db.commit()
    db.refresh(rental)
    db.refresh(asset)
    return RentalResponse(rental=_to_rental_summary(rental), asset=_to_asset_summary(asset))


@admin_router.post("/rentals/{rental_id}/return", response_model=RentalResponse)
def return_rental(
    rental_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> RentalResponse:
    rental = _get_rental_or_404(db, rental_id)
    if rental.status != RentalStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only approved rentals can be returned.")

    asset = _get_asset_or_404(db, rental.asset_id)
    rental.status = RentalStatus.RETURNED
    rental.returned_at = datetime.now(UTC)
    _sync_asset_status(asset, rental.status)

    db.add_all([rental, asset])
    db.commit()
    db.refresh(rental)
    db.refresh(asset)
    return RentalResponse(rental=_to_rental_summary(rental), asset=_to_asset_summary(asset))
