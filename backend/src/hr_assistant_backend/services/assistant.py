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

    def answer(self, payload: ChatRequest) -> ChatResponse:
        user = USERS.get(payload.user_id, USERS["emp-1001"])

        if "연차" in payload.message or "휴가" in payload.message:
            return ChatResponse(
                answer=(
                    f"{user['name']}님 기준 연차 조회는 인사 시스템 연동 후 제공할 수 있습니다. "
                    "현재 MVP는 휴가 정책과 신청 절차 안내를 우선 지원합니다."
                ),
                citations=[
                    Citation(
                        source="HR_POLICY_2026_01",
                        note="휴가 정책은 최신 인사 규정 기준입니다.",
                    )
                ],
            )

        if "대여" in payload.message or "자산" in payload.message or "모니터" in payload.message:
            monitors = self.list_assets(
                user_id=payload.user_id,
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

        return ChatResponse(
            answer="현재 MVP는 자산 조회와 인사 정책 안내를 우선 지원합니다.",
            citations=[
                Citation(source="MVP_SCOPE", note="초기 범위 안내"),
            ],
        )
