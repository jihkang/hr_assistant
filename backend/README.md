## Backend

기본 데이터베이스 연결은 PostgreSQL 기준입니다.

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hr_assistant
```

실행:

```powershell
cd C:\Users\user\hr_assistant\backend
uv run hr-assistant-backend
```

도커 이미지 빌드:

```powershell
cd C:\Users\user\hr_assistant\backend
docker build -t hr-assistant-backend .
```
