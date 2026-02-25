#!/usr/bin/env bash
set -euo pipefail
cd /home/hskim/.openclaw/workspace/skills/openclaw-acp
exec /usr/bin/npx tsx bin/acp.ts serve start --json
