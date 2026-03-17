# HR Assistant

사내 총무·인사 문의를 통합 처리하는 챗봇형 업무 어시스턴트의 초기 스캐폴드입니다.

## Stack

- `frontend`: Next.js 16
- `backend`: FastAPI + uv
- `docs`: 프로젝트 개요와 범위 정리
- `infra`: Docker Compose 기반 PostgreSQL 기본 인프라

## Run

### Infra

```powershell
cd C:\Users\user\hr_assistant\infra
docker compose up -d --build
```

### Frontend

```powershell
cd C:\Users\user\hr_assistant\frontend
npm.cmd run dev
```

### Backend

```powershell
cd C:\Users\user\hr_assistant\backend
uv run hr-assistant-backend
```

백엔드는 기본적으로 아래 PostgreSQL 연결 문자열을 사용하도록 설정했습니다.

```text
postgresql://postgres:${POSTGRES_PASSWORD}@localhost:5432/hr_assistant
```

컨테이너 기준 서비스 포트:

- `frontend`: `http://localhost:3000`
- `backend`: `http://localhost:8000`
- `postgres`: `localhost:5432`

초기 관리자 계정은 코드나 문서에 고정하지 않고 `infra/.env`의 `ADMIN_SEED_*` 값으로 주입합니다.

주요 엔드포인트:

- `GET /api/v1/health`
- `GET /api/v1/assets`
- `POST /api/v1/assistant/chat`
