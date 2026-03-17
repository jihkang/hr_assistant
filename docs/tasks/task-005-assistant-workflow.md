# Task 005: Assistant Workflow

- Status: `todo`
- Priority: `high`

## Goal

LangGraph 기반으로 챗봇 워크플로우를 구성한다.

## Scope

- 요청 분류
- 사용자 컨텍스트 로드
- 권한 체크
- 정책 문서 retrieval
- 자산/인사 데이터 조회
- LLM 응답 생성
- citation 포함 응답 포맷 정리
- 채팅 로그 저장

## Done When

- `POST /api/v1/assistant/chat`가 실제 워크플로우를 탄다
- 답변에 근거가 포함된다
- 권한 위반 요청은 모델 호출 전 차단된다
