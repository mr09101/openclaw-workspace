# PRO Mode (Skill Graph)

## Purpose
- 반복/심화 요청을 안정적으로 처리하고 재사용 가능한 지식으로 남긴다.

## Pipeline
1. Ingest
   - FxTwitter JSON 수집
   - 미디어 URL, 외부 링크, 스레드 여부 추출
2. Normalize
   - 텍스트 정제(줄바꿈/링크 치환)
   - 주장/사실/의견 분리
3. Analyze
   - 핵심 주장 3~5개
   - 근거 수준(강/중/약)
   - 과장/광고성/검증 필요 포인트 표시
4. Persist
   - 필요 시 memory 일자 메모에 요약 저장
   - 후속 추적 키워드 등록(요청 시)

## Escalation Rules
- 숫자/통계/투자 주장 포함 시: 검증 필요 라벨 기본 부여
- 이미지 기반 주장 시: 텍스트와 스샷 불일치 여부 확인
- 외부 아티클 포함 시: 원문 1차 확인 후 요약

## Response Template
- TL;DR
- 핵심 포인트
- 무엇이 사실/의견인지
- 확인이 필요한 부분
- 다음 액션(원하면)
