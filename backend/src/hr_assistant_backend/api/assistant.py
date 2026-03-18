from fastapi import APIRouter

from hr_assistant_backend.schemas.assistant import ChatRequest, ChatResponse
from hr_assistant_backend.schemas.common import HealthResponse
from hr_assistant_backend.services.assistant import AssistantService

router = APIRouter(tags=["assistant"])
service = AssistantService()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="hr-assistant-backend")


@router.post("/assistant/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return service.answer(payload)
