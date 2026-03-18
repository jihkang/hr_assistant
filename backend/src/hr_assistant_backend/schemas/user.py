from pydantic import BaseModel

from hr_assistant_backend.schemas.auth import UserSummary


class MeResponse(BaseModel):
    user: UserSummary


class UserListResponse(BaseModel):
    total: int
    users: list[UserSummary]
