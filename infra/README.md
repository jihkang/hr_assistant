# Infra

기본 데이터베이스는 PostgreSQL + pgvector 조합을 사용합니다.

## Local Database

```powershell
cd C:\Users\user\hr_assistant\infra
docker compose up -d
```

기본 접속 정보:

- DB: `hr_assistant`
- User: `postgres`
- Password: `postgres`
- Port: `5432`

백엔드 기본 연결 문자열:

```text
postgresql://postgres:postgres@localhost:5432/hr_assistant
```

## Init Scripts

초기화 스크립트는 `infra/scripts` 아래에 있습니다.

- `001_extensions.sql`: `pgcrypto`, `citext`, `vector` 확장 생성
- `002_schema.sql`: enum, 테이블, 인덱스, 뷰, 트리거 생성

주의:

- `docker-entrypoint-initdb.d` 스크립트는 새 볼륨에서만 자동 실행됩니다.
- 이미 생성된 볼륨이 있으면 스키마를 다시 적용하지 않습니다.
- 스키마를 처음부터 다시 적용하려면 볼륨을 지우고 다시 올려야 합니다.

```powershell
cd C:\Users\user\hr_assistant\infra
docker compose down -v
docker compose up -d
```

필요하면 `infra/.env`에서 `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`를 바꿔 사용할 수 있습니다.
