# SONIC Harness Structure

이 구조는 Claude Code 계열 하니스 설명과 free-code의 feature surface를 **로컬 OpenClaw 운영에 맞게 흡수**한 것입니다.

## 핵심 축
- **KAIROS**: always-on proactive tick + brief mode + blocking budget
- **Dream**: 메모리 정리용 3-gate / 4-phase 패스
- **Coordinator**: research → synthesis → implementation → verification
- **Turn Loop**: route → coordinator → execution → verification → token-budget → task/checkpoint 세션 루프
- **Undercover**: 현재 비활성화됨 (free-code 방향 반영)
- **Ultraplan**: 복잡한 문제를 장기 계획 작업으로 승격하는 게이트
- **Feature Registry**: 활성/보류 기능 표면 관리
- **Verification / Token Budget / Compaction**: 구현 검증 + 컨텍스트 관리
- **Bridge / Task Trigger**: 원격 연동 상태와 후속 작업 큐

## 상태 파일
- `commands_snapshot.json` — 현재 command surface
- `tools_snapshot.json` — 현재 tool surface
- `features.json` — enabled/deferred 기능 표면
- `backlog.json` — done/planned 상태 추적
- `tasks.json` — task queue / trigger 상태
- `sessions.json` — turn-loop 세션/체크포인트 저장
- `state.json` — tick/dream/route/currentTask/tokenBudget/bridge/session 상태
- `policies.json` — 하니스 정책 묶음

## 실행 인터페이스
- `python3 scripts/sonic_runtime_structure.py summary`
- `python3 scripts/sonic_runtime_structure.py route "요청 문장"`
- `python3 scripts/sonic_runtime_structure.py features`
- `python3 scripts/sonic_runtime_structure.py state`
- `python3 scripts/sonic_runtime_structure.py tick`
- `python3 scripts/sonic_runtime_structure.py dream-plan`
- `python3 scripts/sonic_runtime_structure.py coordinator-plan "작업 설명"`
- `python3 scripts/sonic_runtime_structure.py verify-plan "작업 설명"`
- `python3 scripts/sonic_runtime_structure.py execution-plan "작업 설명"`
- `python3 scripts/sonic_runtime_structure.py token-budget`
- `python3 scripts/sonic_runtime_structure.py compaction-reminder`
- `python3 scripts/sonic_runtime_structure.py bridge-status`
- `python3 scripts/sonic_runtime_structure.py bridge-set on browser`
- `python3 scripts/sonic_runtime_structure.py tasks`
- `python3 scripts/sonic_runtime_structure.py task-add "후속 작업" --trigger post-task`
- `python3 scripts/sonic_runtime_structure.py turn-loop "작업 설명" --max-turns 6`
- `python3 scripts/sonic_runtime_structure.py sessions`
- `python3 scripts/sonic_runtime_structure.py session-show <session_id>`
- `python3 scripts/completion_first_runner.py --label "작업명" --workdir ./project --command "codex exec --full-auto '...'" --summary-file ./project/.openclaw-job-report.md --verify-command "node --check app.js"`

## 원칙
- 구조는 제 기본 작업방식에 흡수해서 사용한다.
- 외부 repo를 그대로 복사하는 게 아니라, 우리 런타임/메모리/메시징에 맞게 재정의한다.
- route → backlog/state → coordinator → execution → verification → summary 흐름을 기본 개발 루프로 삼는다.
- 배경/개발 작업 완료 시에는 검증 상세보다 먼저 `끝났습니다 / 뭐가 바뀌었습니다 / 링크·결과` 3요소를 즉시 보고한다.
- 이를 위해 배경 코딩/쉘 작업은 가능하면 `scripts/completion_first_runner.py` 래퍼로 실행해, 종료 직후 OpenClaw system event로 1차 완료 보고를 보내게 한다.
- 로컬 하니스 레이어에서는 telemetry 없음 / prompt-level undercover guard 비활성 상태로 운용한다.
- 다만 OpenClaw 자체의 상위 시스템 안전장치와 도구 정책은 이 README 범위 밖이며 유지된다.
