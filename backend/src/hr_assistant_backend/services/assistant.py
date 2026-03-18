from fastapi import HTTPException, status

from hr_assistant_backend.models.user import User
from hr_assistant_backend.schemas.assistant import ChatRequest, ChatResponse, Citation

USERS = {
    "emp-1001": {
        "name": "강지호",
        "department": "개발",
        "eligible_categories": {"노트북", "모니터", "헤드셋", "키보드"},
    },
    "emp-2001": {
        "name": "박은서",
        "department": "인사",
        "eligible_categories": {"노트북", "모니터", "헤드셋", "키보드", "회의 장비"},
    },
}

ASSETS = [
    {"name": "ThinkPad X1 Carbon", "category": "노트북", "status": "대여 가능"},
    {"name": "MacBook Pro 14", "category": "노트북", "status": "재고 없음"},
    {"name": "LG 32UN650", "category": "모니터", "status": "대여 가능"},
    {"name": "Dell P2723QE", "category": "모니터", "status": "대여 가능"},
    {"name": "Jabra Speak 750", "category": "회의 장비", "status": "승인 필요"},
]


class AssistantService:
    def list_assets(
        self,
        user_id: str,
        category: str | None = None,
        available_only: bool = True,
    ) -> list[dict[str, object]]:
        user = USERS.get(user_id, USERS["emp-1001"])
        items: list[dict[str, object]] = []

        for asset in ASSETS:
            if category and asset["category"] != category:
                continue
            if available_only and asset["status"] != "대여 가능":
                continue

            items.append(
                {
                    **asset,
                    "eligible": asset["category"] in user["eligible_categories"],
                }
            )

        return items

    def answer(self, payload: ChatRequest, current_user: User) -> ChatResponse:
        request_type = self._classify_request(payload.message)

        if request_type == "leave":
            self._validate_leave_access(payload.message, current_user)
            return self._build_leave_response(current_user)

        if request_type == "asset":
            return self._build_asset_response(current_user.id)

        return ChatResponse(
            answer="현재 MVP는 자산 조회와 인사 정책 안내를 우선 지원합니다.",
            citations=[
                Citation(source="MVP_SCOPE", note="초기 범위 안내"),
            ],
        )

    def _classify_request(self, message: str) -> str:
        if any(keyword in message for keyword in ("연차", "휴가")):
            return "leave"
        if any(keyword in message for keyword in ("대여", "자산", "모니터")):
            return "asset"
        return "general"

    def _validate_leave_access(self, message: str, current_user: User) -> None:
        if "내" in message or current_user.name in message:
            return

        if any(keyword in message for keyword in ("님", "관리자", "직원", "사원", "부장", "과장")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own leave information.",
            )

    def _build_leave_response(self, current_user: User) -> ChatResponse:
        remaining_leave = current_user.annual_leave_total - current_user.annual_leave_used
        return ChatResponse(
            answer=(
                f"{current_user.name}님의 현재 연차 잔여 일수는 {remaining_leave}일입니다. "
                f"총 {current_user.annual_leave_total}일 중 {current_user.annual_leave_used}일을 사용했습니다."
            ),
            citations=[
                Citation(source="USER_LEAVE_BALANCE", note="현재 로그인한 사용자 연차 정보 기준"),
                Citation(source="HR_POLICY_2026_01", note="휴가 정책은 최신 인사 규정 기준입니다."),
            ],
        )

    def _build_asset_response(self, user_id: str) -> ChatResponse:
        monitors = self.list_assets(
            user_id=user_id,
            category="모니터",
            available_only=True,
        )
        names = ", ".join(item["name"] for item in monitors) or "조회 가능한 모니터가 없습니다."
        return ChatResponse(
            answer=(
                f"현재 대여 가능한 모니터는 {len(monitors)}대입니다. "
                f"{names}를 확인했습니다."
            ),
            citations=[
                Citation(source="ASSET_INVENTORY", note="자산 재고 기준"),
                Citation(source="GA_POLICY_2026_01", note="모니터 대여 정책 기준"),
            ],
        )
