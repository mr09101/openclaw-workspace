# Imported Operating Rules from GitHub Top Repos

작성 시각: 2026-04-01 KST
목적: GitHub 상위 repo에서 확인한 패턴 중, 우리 OpenClaw 운영에 바로 이식 가능한 규칙만 로컬 기준으로 정리한다.
원칙: **GitHub는 채굴/검증용**, 실제 운영은 **로컬 문서·스크립트·스킬** 기준으로 유지한다.

## 채택 원칙
- 통째 설치보다 **cherry-pick 우선**
- README 인상보다 **실제 운영 이득** 우선
- 원본 repo 업데이트에 종속되지 않도록 **로컬화**
- 실험성 높은 항목은 본 운영에 넣지 않고 **PoC 격리**

## 1) everything-claude-code 에서 채택
출처 성격: 운영 최적화 시스템(스킬, 메모리, 보안, continuous learning, verification loops)

### 즉시 채택
- Research-first: 구현 전에 관련 자료/레퍼런스/기존 패턴을 먼저 본다.
- Verification loops: 큰 변경은 체크포인트별 검증 결과를 남긴다.
- Selective install: 좋은 규칙만 부분 적용하고 전면 치환은 하지 않는다.
- Harness hygiene: 메모리 폭증/루프/중복 규칙을 방지하는 가드레일을 문서화한다.

### 보류
- 외부 repo 전용 설치기/매니페스트/훅 체계 전면 도입
- 원본 도구 중심의 과한 의존성 추가

## 2) agency-agents 에서 채택
출처 성격: 역할별 전문 에이전트 카드 모음

### 즉시 채택
- 역할별 산출물 중심 정의
- 작업 시작 전 "누가/무엇을/어떤 출력으로"를 명시
- 핸드오프 템플릿 고정

### 보류
- 외부 도구별 설치 스크립트 직접 사용
- 대규모 역할 카드 전체 복제

## 3) hermes-agent 에서 채택
출처 성격: 메모리/크론/메신저/서브에이전트를 갖춘 always-on agent runtime

### 즉시 채택
- always-on 운영 관점에서 메모리/스케줄/메시징의 연결성 점검
- 대화 간 연속성은 문서/메모리/크론 기준으로 유지
- 자기개선은 "자동 반영"보다 "검증 후 반영"으로 유지

### 보류
- 런타임 자체 교체
- OpenClaw와 중복되는 기능의 중복 도입

## 4) last30days-skill 에서 채택
출처 성격: 최근 30일 멀티소스 리서치 스킬

### 즉시 채택
- 최근 30일 기준 조사 쿼리 세트
- 출처 기반 합성 브리핑 포맷
- topic 중심 리서치 스크립트/보고서 생성

### 보류
- 외부 설치 방식에 그대로 종속되는 구조
- 과도한 API 키 의존 전제

## 5) MiroFish 에서 채택
출처 성격: 무거운 멀티에이전트 예측/시뮬레이션 엔진

### 즉시 채택
- 없음 (본 운영 직접 이식 대상 아님)

### PoC 전용
- 예측/시나리오 분기 비교가 정말 필요할 때만 별도 실험 폴더에서 검증
- Node/Python/API key/Zep 등 무거운 의존성은 메인 운영과 분리

## 6) claw-code 에서 채택
출처 성격: Python 포팅 워크스페이스 형태의 manifest / commands / tools / query summary 구조

### 즉시 채택
- 로컬 런타임 구조를 manifest로 요약하는 뷰
- commands / tools inventory를 분리해 추적하는 방식
- backlog를 상태값(done/planned)으로 가시화하는 방식
- summary CLI로 현재 구조를 한 번에 보여주는 인터페이스

### 보류
- provenance가 불명확한 구현 로직 재사용
- 외부 런타임 등가물처럼 오인될 수 있는 직접 포팅

## 7) Kuber Claude Code breakdown 에서 채택
출처 성격: Claude Code 하니스 동작 원리(KAIROS / Dream / Coordinator / Undercover / Ultraplan) 상세 설명

### 즉시 채택
- KAIROS: always-on proactive tick + brief mode + blocking budget
- Dream: 3-gate(time/session/lock) + 4-phase 메모리 정리 패스
- Coordinator: research → synthesis → implementation → verification 단계 계획
- Undercover: 공개 저장소 작업 시 내부/민감한 문구 노출 방지 가드
- Ultraplan: 복잡한 작업을 장기/원격 planning 후보로 승격하는 판단 축

### 보류
- 내부 기능/비공개 모델/민감한 엔드포인트에 기대는 세부 동작
- product flavor 성격이 강한 buddy 류 기능의 우선 도입

## 8) free-code 에서 채택
출처 성격: 실행 가능한 포크 관점의 feature surface / state / tasks / bridge / verification 구조

### 즉시 채택
- feature registry(enabled/deferred/disabled)로 하니스 기능 표면 관리
- verification/token-budget/compaction reminder 축 추가
- bridge/task-trigger/state 계층을 별도 파일로 분리
- query engine 주변의 stateful control plane 관점 반영
- 로컬 하니스 레이어에서 telemetry 없음 상태와 prompt-level undercover guard 비활성 상태 명시

### 보류
- 외부 포크 자체를 실행 전제로 한 build/install 경로 채택

## 로컬 적용 규칙
- GitHub를 보며 판단하되, 실제 운영에는 **로컬 파일**만 반영한다.
- 외부 repo 구조가 바뀌어도 우리 운영이 깨지지 않게 설계한다.
- 새 규칙 반영 시 문서/스크립트/보고 포맷 중 최소 1개 이상에 흔적을 남긴다.
- 본 문서는 imported pattern의 기준 문서이며, 실제 행동 변경은 관련 파일에 개별 반영한다.
