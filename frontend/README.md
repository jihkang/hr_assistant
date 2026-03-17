## Frontend

개발 실행:

```powershell
cd C:\Users\user\hr_assistant\frontend
npm.cmd run dev
```

도커 이미지 빌드:

```powershell
cd C:\Users\user\hr_assistant\frontend
docker build -t hr-assistant-frontend .
```

프론트엔드는 `NEXT_PUBLIC_API_BASE_URL` 환경변수로 백엔드 주소를 주입받습니다.
