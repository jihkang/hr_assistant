# Task 001: DB Bootstrap

- Status: `todo`
- Priority: `high`

## Goal

실제 PostgreSQL 인스턴스를 띄우고, 현재 작성된 스키마를 적용하고, 관리자 시드 계정을 넣을 수 있는 상태를 만든다.

## Scope

- Docker 기반 PostgreSQL 실행 확인
- `infra/scripts/001_extensions.sql` 적용 확인
- `infra/scripts/002_schema.sql` 적용 확인
- 인사 관리자 시드 계정 생성 방식 확정
- 로컬 DB 접속/조회 확인 명령 정리

## Done When

- `localhost:5432` 연결 가능
- `users`, `assets`, `policy_documents` 등 주요 테이블 존재
- 최소 1개 인사 관리자 계정이 존재

## Dependencies

- Docker Desktop 실행
- `docker compose` 사용 가능
