# Task 004: Policy Documents and RAG Base

- Status: `todo`
- Priority: `high`

## Goal

인사/총무 정책 문서를 저장하고 검색 가능한 RAG 기반을 구현한다.

## Scope

- `policy_documents` ORM 모델 구현
- 관리자 정책 문서 등록/수정 API
- 정책 문서 검색 API
- visibility / department / effective_date 메타데이터 필터링
- 임베딩 저장 전략 확정
- 필요 시 chunk 테이블 분리 여부 결정

## Done When

- 정책 문서 CRUD 기본 구현
- 사용자 권한에 맞는 문서만 검색됨
- 답변 근거로 사용할 수 있는 검색 결과 구조가 준비됨
