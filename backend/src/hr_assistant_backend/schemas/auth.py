from datetime import date

from pydantic import BaseModel, EmailStr, Field

from hr_assistant_backend.models.user import Department, Rank


class UserSummary(BaseModel):
    id: str
    name: str
    email: EmailStr
    department: Department
    rank: Rank
    is_admin: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    name: str
    department: Department
    user: UserSummary


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    department: Department
    rank: Rank
    hire_date: date
    annual_leave_total: int = Field(ge=0)
    annual_leave_used: int = Field(default=0, ge=0)


class RegisterResponse(BaseModel):
    message: str
    user: UserSummary
