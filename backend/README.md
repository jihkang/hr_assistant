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

## Security-related environment variables

기본 인증 설정은 아래 환경 변수를 기준으로 동작합니다.

- `SECRET_KEY`: 최소 32자 이상이어야 합니다.
- `COOKIE_SAMESITE`: `lax`, `strict`, `none` 중 하나여야 합니다.
- `COOKIE_SECURE`: `COOKIE_SAMESITE=none` 인 경우 반드시 `true` 여야 합니다.

예시:

```text
SECRET_KEY=replace-this-with-a-32-character-secret
COOKIE_SAMESITE=lax
COOKIE_SECURE=false
```
