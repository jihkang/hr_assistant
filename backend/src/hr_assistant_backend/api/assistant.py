from fastapi import APIRouter, Query

from hr_assistant_backend.schemas.assistant import (
    AssetItem,
    AssetListResponse,
    ChatRequest,
    ChatResponse,
)
from hr_assistant_backend.schemas.common import HealthResponse
from hr_assistant_backend.services.assistant import AssistantService

router = APIRouter(tags=["assistant"])
service = AssistantService()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="hr-assistant-backend")


@router.get("/assets", response_model=AssetListResponse)
def list_assets(
    user_id: str = Query(default="emp-1001"),
    category: str | None = Query(default=None),
    available_only: bool = Query(default=True),
) -> AssetListResponse:
    items = service.list_assets(
        user_id=user_id,
        category=category,
        available_only=available_only,
    )
    return AssetListResponse(items=[AssetItem(**item) for item in items])


@router.post("/assistant/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return service.answer(payload)
