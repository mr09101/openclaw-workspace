# OpenClaw 점검/복구 정리 (2026-02-18)

## 1) 오늘 발생한 이슈 요약
- VS Code 터미널에서 `openclaw` 실행 시 채팅 UI가 바로 안 뜨고 명령 도움말 화면만 표시됨.
- Claude 연동/에이전트 분리 적용 과정에서 원하는 동작이 안 나와서 설정 롤백 진행.
- 터미널이 빙글빙글 돌며 입력이 안 먹는 상황(중지 방법 필요).

## 2) 원인/핵심 포인트
- `openclaw` 단독 실행은 도움말(명령 목록) 화면일 수 있음.
- 채팅 UI는 `openclaw tui`로 진입.
- Claude OAuth가 확인되기 전 모델 분리 적용 시 체감상 “안 붙는” 상태처럼 보일 수 있음.

## 3) 실제로 사용한 해결 절차
### A. 대화 UI 열기
```bash
openclaw tui
```

### B. 게이트웨이 상태 확인/복구
```bash
openclaw gateway status
openclaw gateway start
# 필요 시
openclaw gateway restart
```

### C. 설정 롤백
백업본으로 `openclaw.json` 복원 완료:
- `/home/hskim/.openclaw/openclaw.json.backup-20260218-114531`

(복원 후 게이트웨이 재시작하면 이전 상태로 복귀)

## 4) 터미널 먹통(무한 로딩) 시 중지 방법
1. 기본 중지: `Ctrl + C` (1~3회)
2. 일시정지: `Ctrl + Z` → `jobs` 확인 → `kill %<번호>`
3. 강제 종료:
```bash
ps -ef | grep openclaw
kill -9 <PID>
```
4. 전체 정리(주의):
```bash
pkill -f openclaw
```

## 5) Claude 연동 권장 순서 (다시 시도할 때)
1. 인증 먼저
```bash
openclaw models auth add
openclaw models status
```
2. 인증 확인 후 에이전트/모델 분리 적용
3. 마지막에 재시작
```bash
openclaw gateway restart
```

## 6) 첨부 스크린샷
### 6-1. 도움말 화면(명령 목록)
![openclaw help screen](assets/openclaw-help-screen.jpg)

### 6-2. 추가 대화/로그 캡처
![additional capture 01](assets/additional-chat-capture-01.jpg)
![additional capture 02](assets/additional-chat-capture-02.png)
![additional capture 03](assets/additional-chat-capture-03.png)

---
필요하면 다음 버전에서
- Claude 연동 체크리스트(성공/실패 판별 기준)
- 롤백/복원 스크립트 자동화
- 에이전트별 모델 배치안(비용 최적화 버전)
까지 추가 가능.
