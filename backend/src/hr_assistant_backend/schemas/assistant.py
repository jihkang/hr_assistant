from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class AssetItem(BaseModel):
    name: str
    category: str
    status: str
    eligible: bool


class AssetListResponse(BaseModel):
    items: list[AssetItem]


class ChatRequest(BaseModel):
    user_id: str = Field(default="emp-1001")
    message: str


class Citation(BaseModel):
    source: str
    note: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
