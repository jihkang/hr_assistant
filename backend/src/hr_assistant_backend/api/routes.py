from fastapi import APIRouter

from hr_assistant_backend.api.assistant import router as assistant_router
from hr_assistant_backend.api.auth import admin_router, router as auth_router

router = APIRouter()
router.include_router(assistant_router)
router.include_router(auth_router)
router.include_router(admin_router)
