# HEARTBEAT.md

## Cadence-Based Checks
Read `memory/heartbeat-state.json`. Run whichever check is most overdue.

Cadences:
- email: every 30m (09:00-21:00)
- calendar: every 2h (08:00-22:00)
- tasks: every 30m (always)
- git: every 24h (always)
- system: every 24h (03:00 only)

Process:
1) Load timestamps from `memory/heartbeat-state.json`
2) Compute most overdue allowed check
3) Run that single check
4) Update timestamp
5) Report only actionable findings
6) If nothing needs attention, reply `HEARTBEAT_OK`

## Check Rules
- email: report only actionable/new important sender items
- calendar: report only near-term important events
- tasks: report only blocked/stalled work
- git: report only significant pending state
- system: report only errors/failures
