# 오늘 저녁 연동 체크리스트 (국장+코인 모의)

## 0) 시작 전
- [ ] OpenClaw/Gateway 실행 확인
- [ ] API 키를 채팅으로 공유하지 않기 (.env에만 저장)

## 1) 환경파일 준비
```bash
cd ~/.openclaw/workspace/trading-automation
cp -n .env.example .env
```
- [ ] `.env` 파일 생성 완료

## 2) .env 값 입력 (마스킹 예시)
```env
# KIS (Paper)
KIS_PAPER_APP_KEY=<KIS_PAPER_APP_KEY>
KIS_PAPER_APP_SECRET=<KIS_PAPER_APP_SECRET>
KIS_PAPER_ACCOUNT_NO=<계좌8자리-상품2자리>
KIS_HTS_ID=<HTS_ID>

# Upbit (Spot)
UPBIT_ACCESS_KEY=<UPBIT_ACCESS_KEY>
UPBIT_SECRET_KEY=<UPBIT_SECRET_KEY>

# Runtime
TRADING_MODE=paper
MARKET_SCOPE=kr_stock,crypto_spot
KILL_SWITCH=0
```
- [ ] KIS 모의 키/계좌 입력
- [ ] Upbit 키 입력 + 업비트 허용 IP 등록 확인

## 3) 리스크 기본값 점검
파일: `config/risk.yaml`
- [ ] daily_loss_limit_pct = 2.0
- [ ] symbol_max_alloc_pct = 15.0
- [ ] max_concurrent_positions = 5

## 4) KIS 모의 연동 테스트
- [ ] 토큰 발급 성공
- [ ] 계좌 잔고 조회 성공
- [ ] 종목 현재가 조회 성공
- [ ] 모의 주문 1건 제출/취소 성공

## 5) 코인(Upbit) 연동 테스트
- [ ] 인증(JWT) 성공
- [ ] 잔고 조회 성공
- [ ] KRW-BTC 현재가 조회 성공
- [ ] 소액 주문/취소 테스트(또는 모의 시뮬레이터 체결) 성공

## 6) 알림/로그 확인
- [ ] 주문/체결/실패 로그 저장 확인
- [ ] 텔레그램 알림 수신 확인

## 7) 오늘 종료 기준
- [ ] 테스트 모두 성공하면: 내일 모의 운용 시작
- [ ] 실패 항목 있으면: 실패 로그 3줄 요약 후 재시도 계획 확정
