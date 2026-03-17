# Task 002: User and Admin API

- Status: `in_progress`
- Priority: `high`

## Goal

사용자/관리자 관리 API를 스펙 수준까지 확장한다.

## Current State

- 로그인/로그아웃/재발급 구현됨
- `GET /auth/me` 구현됨
- 인사 관리자 전용 사용자 생성 구현됨

## Remaining Scope

- `GET /api/v1/admin/users`
- `GET /api/v1/admin/users/{user_id}`
- `PATCH /api/v1/admin/users/{user_id}`
- `GET /api/v1/users/me`
- `GET /api/v1/users/me/leave`
- DB 기반 현재 연차 계산/응답 검증

## Done When

- 관리자 사용자 목록/상세/수정 가능
- 일반 사용자는 본인 정보와 연차만 조회 가능
- 권한 규칙 테스트 추가 완료
