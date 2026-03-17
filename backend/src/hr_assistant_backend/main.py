from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hr_assistant_backend.api.routes import router
from hr_assistant_backend.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="사내 총무·인사 상담을 위한 FastAPI 백엔드",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix=settings.api_prefix)

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(
        "hr_assistant_backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
