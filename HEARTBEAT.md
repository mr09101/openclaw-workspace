# HEARTBEAT.md

## Cadence-Based Checks
Read `memory/heartbeat-state.json`. Run whichever check is most overdue.

> Google-related checks are disabled until explicitly re-enabled by the user.

Cadences:
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
- tasks: report only blocked/stalled work
- git: report only significant pending state
- system: report only errors/failures
