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
- Password: `infra/.env`의 `POSTGRES_PASSWORD`
- Port: `5432`

초기 관리자 계정은 문서에 고정값으로 두지 않고 `infra/.env`에서 주입합니다.

백엔드 기본 연결 문자열:

```text
postgresql://postgres:${POSTGRES_PASSWORD}@localhost:5432/hr_assistant
```

권장 설정:

1. `infra/.env.example`을 복사해서 `infra/.env`를 만듭니다.
2. `POSTGRES_PASSWORD`, `ADMIN_SEED_EMAIL`, `ADMIN_SEED_PASSWORD`를 실제 값으로 바꿉니다.
3. 백엔드 보안 설정을 함께 쓰려면 `SECRET_KEY`, `COOKIE_SAMESITE`, `COOKIE_SECURE`도 `infra/.env`에 설정합니다.

## Init Scripts

초기화 스크립트는 `infra/scripts` 아래에 있습니다.

- `001_extensions.sql`: `pgcrypto`, `citext`, `vector` 확장 생성
- `002_schema.sql`: enum, 테이블, 인덱스, 뷰, 트리거 생성
- `003_seed_admin.sh`: `infra/.env` 값으로 초기 admin 계정 생성

주의:

- `docker-entrypoint-initdb.d` 스크립트는 새 볼륨에서만 자동 실행됩니다.
- 이미 생성된 볼륨이 있으면 스키마를 다시 적용하지 않습니다.
- `ADMIN_SEED_EMAIL` 또는 `ADMIN_SEED_PASSWORD`가 비어 있으면 admin 시드는 건너뜁니다.
- 스키마를 처음부터 다시 적용하려면 볼륨을 지우고 다시 올려야 합니다.

```powershell
cd C:\Users\user\hr_assistant\infra
docker compose down -v
docker compose up -d
```

필요하면 `infra/.env`에서 `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`를 바꿔 사용할 수 있습니다.
