from fastapi import APIRouter

from hr_assistant_backend.schemas.assistant import ChatRequest, ChatResponse
from hr_assistant_backend.schemas.common import HealthResponse
from hr_assistant_backend.api.dependencies import get_current_user
from hr_assistant_backend.models.user import User
from hr_assistant_backend.services.assistant import AssistantService

router = APIRouter(tags=["assistant"])
service = AssistantService()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="hr-assistant-backend")


@router.post("/assistant/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    return service.answer(payload, current_user=current_user)
