# Trading Automation Plan (KR Stock + Crypto)

## Goal
- Start with **paper trading** for:
  - Korean stocks (KIS Open API mock account)
  - Crypto spot (paper simulator using real market prices)
- Move to **live trading** after stability checks.
- Later expand crypto from spot to **futures**.

## Important constraints
- **Upbit has no futures market.**
  - Spot: Upbit 가능
  - Futures: Binance/Bybit/OKX 등 별도 거래소 필요
- Live trading requires strict risk controls and kill-switch.

## Architecture
1. Signal engine (strategy output)
2. Risk engine (position limits, daily loss cap, cooldown)
3. Broker/exchange adapters
   - KIS adapter (paper/live)
   - Upbit adapter (spot live)
   - Crypto paper simulator (virtual account)
   - Futures adapter (future phase)
4. Execution engine (idempotent order submit + retry)
5. Journal & alerting (fills, pnl, errors)

## Phase roadmap
### Phase 1 — Paper (now)
- KIS mock account: order/position/balance loop test
- Crypto paper simulator: execute virtual fills on real ticker stream
- Telegram alerts for: order accepted/filled/rejected/stop-triggered
- 7~10 trading days stability test

### Phase 2 — Crypto spot live
- Upbit live key with minimal capital
- One-strategy, one-market start (e.g. KRW-BTC)
- Daily drawdown hard stop

### Phase 3 — KR stock live
- KIS live key, reduced order size
- Session guards (장 시작/종료, 주문 가능 시간)
- Slippage + partial fill handling

### Phase 4 — Crypto futures (later)
- Select exchange: Binance/Bybit/OKX
- Add leverage constraints + liquidation distance checks
- Start at 1x~2x only, isolated margin preferred

## Minimum risk controls (must-have)
- Max daily loss (% or KRW)
- Max position per symbol (% of equity)
- Max concurrent positions
- Max orders per minute
- Circuit breaker (N consecutive failures)
- Global kill-switch (manual + auto)

## What we need from user
1. KIS: app key/secret (paper first)
2. Upbit: access/secret (spot when going live)
3. Risk numbers:
   - daily loss cap
   - symbol max allocation
   - max concurrent positions
4. Crypto futures preferred exchange (later)

## Recommended first live checklist
- Paper win-rate or expectancy verified
- API/network/retry logs clean for 1 week
- Stop-loss trigger tested in paper
- Kill-switch tested manually
- Small capital dry live for 3~5 days
