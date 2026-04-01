#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

ROOT = Path('/home/hskim/.openclaw/workspace')
RUNTIME_DIR = ROOT / 'runtime' / 'assistant_structure'
COMMANDS = RUNTIME_DIR / 'commands_snapshot.json'
TOOLS = RUNTIME_DIR / 'tools_snapshot.json'
FEATURES = RUNTIME_DIR / 'features.json'
BACKLOG = RUNTIME_DIR / 'backlog.json'
TASKS = RUNTIME_DIR / 'tasks.json'
SESSIONS = RUNTIME_DIR / 'sessions.json'
STATE = RUNTIME_DIR / 'state.json'
POLICIES = RUNTIME_DIR / 'policies.json'


@dataclass(frozen=True)
class Subsystem:
    name: str
    path: str
    file_count: int
    notes: str


@dataclass(frozen=True)
class RuntimeManifest:
    root: Path
    total_files: int
    subsystems: tuple[Subsystem, ...]

    def to_markdown(self) -> str:
        lines = [
            f'Runtime root: `{self.root}`',
            f'Total tracked files (selected areas): **{self.total_files}**',
            '',
            'Subsystems:',
        ]
        for s in self.subsystems:
            lines.append(f'- `{s.name}` ({s.file_count} files) — {s.notes}')
        return '\n'.join(lines)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec='seconds')


def load_json(path: Path, default: Any) -> Any:
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def build_manifest() -> RuntimeManifest:
    selected = {
        'memory': '일일/장기 메모리 계층',
        'runtime': '런타임 상태/산출물/운영 규칙',
        'scripts': '실행 스크립트와 자동화 코드',
        'skills': '로컬 스킬 계층',
        'templates': 'handoff/출력 템플릿',
        'reports': '보고서/브리핑 산출물',
    }
    subsystems: list[Subsystem] = []
    total = 0
    for name, notes in selected.items():
        path = ROOT / name
        if not path.exists():
            continue
        count = sum(1 for p in path.rglob('*') if p.is_file())
        total += count
        subsystems.append(Subsystem(name=name, path=str(path.relative_to(ROOT)), file_count=count, notes=notes))
    subsystems.sort(key=lambda x: x.file_count, reverse=True)
    return RuntimeManifest(root=ROOT, total_files=total, subsystems=tuple(subsystems))


def token_set(text: str) -> set[str]:
    import re
    toks = re.findall(r'[A-Za-z][A-Za-z0-9_\-]{1,}|[가-힣]{2,}', text.lower())
    return set(toks)


def render_list(rows: list[dict[str, Any]], limit: int) -> str:
    lines: list[str] = []
    for row in rows[:limit]:
        label = row.get('name') or row.get('title')
        desc = row.get('responsibility') or row.get('notes', '')
        hint = row.get('source_hint')
        if hint:
            lines.append(f'- {label} — {desc} ({hint})')
        else:
            lines.append(f'- {label} — {desc}')
    return '\n'.join(lines)


def render_features(limit: int = 50) -> str:
    features = load_json(FEATURES, [])
    counter = Counter(item.get('status', 'unknown') for item in features)
    lines = [f'Feature registry: {len(features)} | {dict(counter)}', '']
    lines.extend(
        f"- {row['name']} [{row['status']}] — {row['kind']} — {row['notes']}"
        for row in features[:limit]
    )
    return '\n'.join(lines)


def render_backlog(limit: int) -> str:
    rows = load_json(BACKLOG, [])
    return '\n'.join(f"- {row['title']} [{row['status']}] — {row['notes']}" for row in rows[:limit])


def render_tasks(limit: int) -> str:
    rows = load_json(TASKS, [])
    return '\n'.join(
        f"- {row['id']} [{row['status']}] — {row['title']} (trigger={row.get('trigger', 'manual')})"
        for row in rows[:limit]
    )


def render_sessions(limit: int) -> str:
    rows = load_json(SESSIONS, [])
    if not rows:
        return '- no sessions'
    lines = []
    for row in rows[:limit]:
        lines.append(
            f"- {row['id']} [{row['status']}] turns={len(row.get('turns', []))} prompt={row['prompt']}"
        )
    return '\n'.join(lines)


def score_rows(rows: list[dict[str, Any]], prompt: str) -> list[tuple[float, dict[str, Any]]]:
    q = token_set(prompt)
    prompt_lc = prompt.lower()
    scored: list[tuple[float, dict[str, Any]]] = []
    for row in rows:
        keywords = {str(k).lower() for k in row.get('keywords', [])}
        responsibility = token_set(str(row.get('responsibility', '')))
        name_tokens = token_set(str(row.get('name', '')))
        overlap = len(q & keywords) * 2 + len(q & responsibility) + len(q & name_tokens)
        substring_hits = sum(1 for kw in keywords if kw and kw in prompt_lc)
        overlap += substring_hits * 1.5
        if overlap > 0:
            scored.append((float(overlap), row))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored


def get_route_hits(prompt: str, limit: int = 5) -> tuple[list[tuple[float, dict[str, Any]]], list[tuple[float, dict[str, Any]]]]:
    commands = load_json(COMMANDS, [])
    tools = load_json(TOOLS, [])
    return score_rows(commands, prompt)[:limit], score_rows(tools, prompt)[:limit]


def save_last_route(prompt: str, command_hits: list[tuple[float, dict[str, Any]]], tool_hits: list[tuple[float, dict[str, Any]]]) -> None:
    state = load_json(STATE, {})
    state['lastRoute'] = {
        'at': now_iso(),
        'prompt': prompt,
        'commands': [row['name'] for _, row in command_hits],
        'tools': [row['name'] for _, row in tool_hits],
    }
    save_json(STATE, state)


def route_prompt(prompt: str, limit: int = 5) -> str:
    command_hits, tool_hits = get_route_hits(prompt, limit)
    save_last_route(prompt, command_hits, tool_hits)
    lines = [f'Prompt: {prompt}', '', 'Command matches:']
    if command_hits:
        lines.extend(f"- {row['name']} (score={score:.0f}) — {row['responsibility']}" for score, row in command_hits)
    else:
        lines.append('- none')
    lines += ['', 'Tool matches:']
    if tool_hits:
        lines.extend(f"- {row['name']} (score={score:.0f}) — {row['responsibility']}" for score, row in tool_hits)
    else:
        lines.append('- none')
    return '\n'.join(lines)


def render_summary() -> str:
    manifest = build_manifest()
    commands = load_json(COMMANDS, [])
    tools = load_json(TOOLS, [])
    features = load_json(FEATURES, [])
    backlog = load_json(BACKLOG, [])
    tasks = load_json(TASKS, [])
    sessions = load_json(SESSIONS, [])
    state = load_json(STATE, {})
    backlog_counter = Counter(item.get('status', 'unknown') for item in backlog)
    feature_counter = Counter(item.get('status', 'unknown') for item in features)

    lines = [
        '# SONIC Runtime Structure Summary',
        '',
        manifest.to_markdown(),
        '',
        f'Command surface: {len(commands)} entries',
    ]
    lines.extend(f"- {c['name']} — {c['responsibility']}" for c in commands[:12])
    lines += [
        '',
        f'Tool surface: {len(tools)} entries',
    ]
    lines.extend(f"- {t['name']} — {t['responsibility']}" for t in tools[:10])
    lines += [
        '',
        f'Feature surface: {len(features)} | {dict(feature_counter)}',
    ]
    lines.extend(f"- {f['name']} [{f['status']}] — {f['notes']}" for f in features[:10])
    lines += [
        '',
        f'Backlog: {len(backlog)} items | {dict(backlog_counter)}',
    ]
    lines.extend(f"- {b['title']} [{b['status']}] — {b['notes']}" for b in backlog[:10])
    lines += [
        '',
        f'Task queue: {len(tasks)} entries',
    ]
    lines.extend(f"- {t['id']} [{t['status']}] — {t['title']}" for t in tasks[:8])
    lines += [
        '',
        f'Session store: {len(sessions)} entries',
    ]
    lines.extend(f"- {s['id']} [{s['status']}] — {s['prompt']}" for s in sessions[:5])
    lines += [
        '',
        'Harness state:',
        f"- activeMode: {state.get('activeMode')}",
        f"- blockingBudgetSec: {state.get('blockingBudgetSec')}",
        f"- sessionCountSinceDream: {state.get('sessionCountSinceDream')}",
        f"- currentTask: {state.get('currentTask')}",
        f"- currentTaskStatus: {state.get('currentTaskStatus')}",
        f"- currentSessionId: {state.get('currentSessionId')}",
        f"- contextUtilizationPct: {state.get('contextUtilizationPct')}",
        f"- bridgeMode: {state.get('bridgeMode')}",
        f"- lastRoute: {state.get('lastRoute')}",
    ]
    return '\n'.join(lines)


def render_state() -> str:
    state = load_json(STATE, {})
    policies = load_json(POLICIES, {})
    lines = ['# SONIC Harness State', '', json.dumps(state, ensure_ascii=False, indent=2), '', '# Active Policy Keys', '']
    lines.extend(f'- {k}' for k in policies.keys())
    return '\n'.join(lines)


def compute_token_budget() -> dict[str, Any]:
    state = load_json(STATE, {})
    policies = load_json(POLICIES, {})
    budget = state.get('tokenBudget', {})
    current = float(budget.get('currentEstimate') or 0)
    max_tokens = float(budget.get('maxTokens') or 1)
    pct = round((current / max_tokens) * 100, 1) if max_tokens else 0.0
    warn = float((policies.get('tokenBudget') or {}).get('warnAtPct', budget.get('warnAtPct', 75)))
    hard = float((policies.get('tokenBudget') or {}).get('hardAtPct', budget.get('hardAtPct', 90)))
    verdict = 'OK'
    if pct >= hard:
        verdict = 'HARD'
    elif pct >= warn:
        verdict = 'WARN'
    state['contextUtilizationPct'] = pct
    save_json(STATE, state)
    return {
        'currentEstimate': int(current),
        'maxTokens': int(max_tokens),
        'utilizationPct': pct,
        'warnAtPct': warn,
        'hardAtPct': hard,
        'verdict': verdict,
    }


def render_token_budget() -> str:
    info = compute_token_budget()
    return '\n'.join([
        '# Token Budget',
        f"- currentEstimate: {info['currentEstimate']}",
        f"- maxTokens: {info['maxTokens']}",
        f"- utilizationPct: {info['utilizationPct']}",
        f"- warnAtPct: {info['warnAtPct']}",
        f"- hardAtPct: {info['hardAtPct']}",
        f"- verdict: {info['verdict']}",
    ])


def render_compaction_reminder() -> str:
    state = load_json(STATE, {})
    policies = load_json(POLICIES, {})
    pct = float(state.get('contextUtilizationPct') or compute_token_budget()['utilizationPct'])
    compaction = policies.get('compaction', {})
    remind = float(compaction.get('remindAbovePct', 75))
    hard = float(compaction.get('hardAbovePct', 90))
    if pct >= hard:
        msg = 'HARD: 컨텍스트가 높습니다. summarize/checkpoint/prune repetition 순으로 즉시 정리해야 합니다.'
    elif pct >= remind:
        msg = 'WARN: 컨텍스트가 올라왔습니다. 장문 반복을 줄이고 체크포인트 요약을 권장합니다.'
    else:
        msg = 'OK: 아직 compaction reminder가 필요하지 않습니다.'
    return '\n'.join(['# Compaction Reminder', f'- contextUtilizationPct: {pct}', f'- decision: {msg}'])


def run_tick() -> str:
    state = load_json(STATE, {})
    state['lastTickAt'] = now_iso()
    state['sessionCountSinceDream'] = int(state.get('sessionCountSinceDream') or 0) + 1
    save_json(STATE, state)
    current_task = state.get('currentTask')
    if current_task:
        action = f'BRIEF: 현재 활성 작업 `{current_task}` 진행 중이라 새 proactive 액션은 보류합니다.'
    else:
        action = 'BRIEF: 지금은 새 proactive 액션 없이 조용히 유지합니다.'
    return '\n'.join([
        '# KAIROS Tick',
        f'- lastTickAt: {state["lastTickAt"]}',
        f'- sessionCountSinceDream: {state["sessionCountSinceDream"]}',
        f'- blockingBudgetSec: {state.get("blockingBudgetSec")}',
        f'- decision: {action}',
    ])


def dream_gate_status(state: dict[str, Any], policies: dict[str, Any]) -> tuple[bool, list[str]]:
    dream = policies.get('dream', {})
    reasons: list[str] = []
    ok = True
    last_dream_at = state.get('lastDreamAt')
    hours_needed = int(dream.get('timeGateHours', 24))
    session_gate = int(dream.get('sessionGate', 5))
    if last_dream_at:
        try:
            last = datetime.fromisoformat(last_dream_at)
            base_now = datetime.now(last.tzinfo or timezone.utc)
            if base_now - last < timedelta(hours=hours_needed):
                ok = False
                reasons.append(f'time gate not met (< {hours_needed}h)')
        except Exception:
            reasons.append('lastDreamAt parse failed, treating time gate as open')
    if int(state.get('sessionCountSinceDream') or 0) < session_gate:
        ok = False
        reasons.append(f'session gate not met (< {session_gate})')
    if bool(state.get('dreamLock')):
        ok = False
        reasons.append('lock gate closed (dreamLock=true)')
    return ok, reasons


def render_dream_plan(mark_done: bool = False) -> str:
    state = load_json(STATE, {})
    policies = load_json(POLICIES, {})
    ok, reasons = dream_gate_status(state, policies)
    dream = policies.get('dream', {})
    phases = dream.get('phases', [])
    if mark_done:
        state['lastDreamAt'] = now_iso()
        state['sessionCountSinceDream'] = 0
        state['dreamLock'] = False
        state['lastMemoryExtractAt'] = now_iso()
        save_json(STATE, state)
    lines = ['# Dream Plan', f'- ready: {ok}']
    if reasons:
        lines.append(f'- blockers: {", ".join(reasons)}')
    lines.append(f'- lastDreamAt: {state.get("lastDreamAt")}')
    lines.append(f'- sessionCountSinceDream: {state.get("sessionCountSinceDream")}')
    lines.append('- phases:')
    lines.extend(f'  - {phase}' for phase in phases)
    lines.append('- actions:')
    lines.append('  - orient: memory 디렉토리와 MEMORY.md 훑기')
    lines.append('  - gather_recent_signal: daily log / drift / transcript 기반 최근 신호 수집')
    lines.append('  - consolidate: 절대날짜화 + 중요 사실 정리')
    lines.append('  - prune_and_index: MEMORY.md 크기/중복/모순 정리')
    if mark_done:
        lines.append('- marked_done: true')
    return '\n'.join(lines)


def render_coordinator_plan(task: str) -> str:
    lines = [
        '# Coordinator Plan',
        f'- task: {task}',
        '- phase 1 / research: 관련 파일, 기존 구조, 제약, 참고 구현 탐색',
        '- phase 2 / synthesis: research 결과를 읽고 명확한 spec/handoff로 종합',
        '- phase 3 / implementation: 독립 작업은 병렬, 충돌 작업은 직렬 구현',
        '- phase 4 / verification: 테스트, 리뷰, 리스크/롤백 점검',
        '',
        '## SONIC DEV TEAM Mapping',
        '- 소닉: synthesis + 최종 판단',
        '- 테일즈/에이미/너클즈: implementation',
        '- 실버: verification',
        '- 섀도우: 리뷰/리스크 게이트',
        '',
        '## Rule',
        '- 병렬 가능한 일은 병렬로 보낸다.',
        '- "based on your findings" 같은 애매한 handoff 금지; 실제 findings를 읽고 명시적으로 지시한다.',
    ]
    return '\n'.join(lines)


def render_verify_plan(task: str) -> str:
    policies = load_json(POLICIES, {})
    verify = policies.get('verification', {})
    stages = verify.get('stages', ['build', 'test', 'smoke', 'review'])
    lines = ['# Verification Plan', f'- task: {task}', f'- requireEvidence: {verify.get("requireEvidence", False)}', '- stages:']
    for stage in stages:
        lines.append(f'  - {stage}')
    lines += [
        '- checklist:',
        '  - changed files identified',
        '  - relevant build/test command prepared',
        '  - smoke path defined',
        '  - rollback/risk noted',
    ]
    return '\n'.join(lines)


def choose_execution_mode(task: str) -> tuple[str, list[str]]:
    prompt = task.lower()
    direct_markers = ['문구', '한줄', 'one-liner', 'small fix', '오타', '간단']
    agent_markers = ['기능', '로그인', '리팩토링', '대규모', 'multi-file', '아키텍처', '개발', 'build', '구현']
    if any(marker in prompt for marker in direct_markers):
        return 'direct-edit', ['read', 'edit', 'write', 'exec']
    if any(marker in prompt for marker in agent_markers):
        return 'coding-agent', ['sessions_spawn', 'exec', 'process']
    return 'hybrid', ['read', 'edit', 'exec', 'sessions_spawn']


def render_execution_plan(task: str) -> str:
    mode, tools = choose_execution_mode(task)
    lines = [
        '# Execution Plan',
        f'- task: {task}',
        f'- mode: {mode}',
        f'- recommended_tools: {", ".join(tools)}',
        '- steps:',
    ]
    if mode == 'direct-edit':
        lines += [
            '  - 관련 파일 read',
            '  - 직접 edit/write로 수정',
            '  - exec로 최소 테스트 실행',
        ]
    elif mode == 'coding-agent':
        lines += [
            '  - 요구사항을 handoff로 정리',
            '  - sessions_spawn 또는 코딩 에이전트 실행 경로 선택',
            '  - exec/process로 테스트와 진행상황 확인',
        ]
    else:
        lines += [
            '  - 작은 수정은 직접 처리',
            '  - 큰 범위/반복 작업은 코딩 에이전트로 위임',
            '  - 마지막에 exec로 테스트 및 검증',
        ]
    lines += [
        '- outputs:',
        '  - 변경 파일 목록',
        '  - 실행/테스트 명령',
        '  - 리스크/롤백 메모',
    ]
    return '\n'.join(lines)


def render_bridge_status() -> str:
    state = load_json(STATE, {})
    bridge = state.get('bridgeMode', {})
    return '\n'.join([
        '# Bridge Status',
        f'- enabled: {bridge.get("enabled")}',
        f'- target: {bridge.get("target")}',
        f'- lastBridgeAt: {bridge.get("lastBridgeAt")}',
    ])


def set_bridge(enabled: bool, target: str | None = None) -> str:
    state = load_json(STATE, {})
    bridge = state.get('bridgeMode', {})
    bridge['enabled'] = enabled
    bridge['target'] = target if enabled else None
    bridge['lastBridgeAt'] = now_iso()
    state['bridgeMode'] = bridge
    save_json(STATE, state)
    return render_bridge_status()


def set_current_task(task: str | None, status: str | None = None) -> str:
    state = load_json(STATE, {})
    state['currentTask'] = task
    if status is not None:
        state['currentTaskStatus'] = status
    save_json(STATE, state)
    return f"currentTask={task} status={state.get('currentTaskStatus')}"


def update_backlog(title: str, status: str) -> str:
    rows = load_json(BACKLOG, [])
    updated = False
    for row in rows:
        if row.get('title') == title:
            row['status'] = status
            updated = True
            break
    if not updated:
        rows.append({'title': title, 'status': status, 'notes': ''})
    save_json(BACKLOG, rows)
    return f'backlog updated: {title} -> {status}'


def slug_task(text: str) -> str:
    import re
    slug = re.sub(r'[^A-Za-z0-9가-힣]+', '-', text.strip()).strip('-').lower()
    return slug[:60] or 'task'


def add_task_record(title: str, trigger: str = 'manual') -> dict[str, Any]:
    rows = load_json(TASKS, [])
    task_id = f"task-{slug_task(title)}-{uuid4().hex[:6]}"
    task = {'id': task_id, 'title': title, 'status': 'queued', 'trigger': trigger, 'notes': ''}
    rows.append(task)
    save_json(TASKS, rows)
    return task


def add_task(title: str, trigger: str = 'manual') -> str:
    task = add_task_record(title, trigger)
    return f"added task: {task['id']} ({trigger})"


def update_task(task_id: str, status: str) -> str:
    rows = load_json(TASKS, [])
    for row in rows:
        if row.get('id') == task_id:
            row['status'] = status
            save_json(TASKS, rows)
            return f'task updated: {task_id} -> {status}'
    return f'task not found: {task_id}'


def add_session_record(record: dict[str, Any]) -> None:
    rows = load_json(SESSIONS, [])
    rows.insert(0, record)
    save_json(SESSIONS, rows)


def find_session(session_id: str) -> dict[str, Any] | None:
    rows = load_json(SESSIONS, [])
    for row in rows:
        if row.get('id') == session_id:
            return row
    return None


def render_session(session_id: str) -> str:
    session = find_session(session_id)
    if not session:
        return f'session not found: {session_id}'
    lines = [
        f"# Session {session['id']}",
        f"- status: {session['status']}",
        f"- prompt: {session['prompt']}",
        f"- createdAt: {session['createdAt']}",
        f"- updatedAt: {session['updatedAt']}",
        f"- stopReason: {session['stopReason']}",
        '',
        '## Turns',
    ]
    for turn in session.get('turns', []):
        lines.append(f"- {turn['index']}. {turn['name']} — {turn['summary']}")
    lines += ['', '## Checkpoints']
    for cp in session.get('checkpoints', []):
        lines.append(f"- {cp['name']}: {cp['summary']}")
    return '\n'.join(lines)


def run_turn_loop(prompt: str, max_turns: int) -> str:
    policies = load_json(POLICIES, {})
    state = load_json(STATE, {})
    loop_cfg = policies.get('turnLoop', {})
    stages = list(loop_cfg.get('stages', []))
    if not stages:
        stages = ['route', 'coordinator', 'verification', 'token-budget', 'task-trigger', 'checkpoint']
    max_turns = max(1, min(max_turns, len(stages)))

    session_id = f"loop-{uuid4().hex[:10]}"
    turns: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []
    stop_reason = 'completed'

    def add_turn(index: int, name: str, summary: str, output: str) -> None:
        turns.append({'index': index, 'name': name, 'summary': summary, 'output': output})
        checkpoints.append({'name': name, 'summary': summary})

    stage_index = 0

    if stage_index < max_turns:
        cmd_hits, tool_hits = get_route_hits(prompt, 5)
        save_last_route(prompt, cmd_hits, tool_hits)
        summary = f"commands={','.join(row['name'] for _, row in cmd_hits) or 'none'} | tools={','.join(row['name'] for _, row in tool_hits) or 'none'}"
        output = route_prompt(prompt, 5)
        add_turn(stage_index + 1, 'route', summary, output)
        stage_index += 1

    if stage_index < max_turns:
        output = render_coordinator_plan(prompt)
        add_turn(stage_index + 1, 'coordinator', 'research→synthesis→implementation→verification 계획 생성', output)
        stage_index += 1

    if stage_index < max_turns:
        output = render_execution_plan(prompt)
        mode, _tools = choose_execution_mode(prompt)
        state = load_json(STATE, {})
        state['currentTaskStatus'] = 'execution-planned'
        save_json(STATE, state)
        add_turn(stage_index + 1, 'execution', f'mode={mode}', output)
        stage_index += 1

    if stage_index < max_turns:
        output = render_verify_plan(prompt)
        add_turn(stage_index + 1, 'verification', '검증 단계와 체크리스트 생성', output)
        state = load_json(STATE, {})
        state['lastVerificationAt'] = now_iso()
        save_json(STATE, state)
        stage_index += 1

    if stage_index < max_turns:
        budget = compute_token_budget()
        output = render_token_budget() + '\n\n' + render_compaction_reminder()
        add_turn(stage_index + 1, 'token-budget', f"utilization={budget['utilizationPct']}% verdict={budget['verdict']}", output)
        stage_index += 1

    created_task: dict[str, Any] | None = None
    if stage_index < max_turns:
        created_task = add_task_record(prompt, 'turn-loop')
        output = f"queued task: {created_task['id']} ({created_task['title']})"
        add_turn(stage_index + 1, 'task-trigger', f"queued {created_task['id']}", output)
        stage_index += 1

    if stage_index < max_turns:
        state = load_json(STATE, {})
        state['currentTask'] = prompt
        state['currentTaskStatus'] = 'planned'
        state['currentSessionId'] = session_id
        state['lastCheckpointAt'] = now_iso()
        save_json(STATE, state)
        output = json.dumps({
            'currentTask': state['currentTask'],
            'currentTaskStatus': state['currentTaskStatus'],
            'currentSessionId': state['currentSessionId'],
            'lastCheckpointAt': state['lastCheckpointAt'],
        }, ensure_ascii=False, indent=2)
        add_turn(stage_index + 1, 'checkpoint', f"session={session_id} currentTask planned", output)
        stage_index += 1

    if stage_index < len(stages) and stage_index >= max_turns:
        stop_reason = 'max_turns_reached'

    record = {
        'id': session_id,
        'prompt': prompt,
        'createdAt': now_iso(),
        'updatedAt': now_iso(),
        'status': 'completed' if stop_reason == 'completed' else 'partial',
        'stopReason': stop_reason,
        'turns': turns,
        'checkpoints': checkpoints,
    }
    add_session_record(record)

    lines = [
        '# Turn Loop Result',
        f'- session: {session_id}',
        f'- prompt: {prompt}',
        f'- turnsExecuted: {len(turns)}',
        f'- stopReason: {stop_reason}',
        '',
        '## Stages',
    ]
    lines.extend(f"- {turn['index']}. {turn['name']} — {turn['summary']}" for turn in turns)
    if created_task:
        lines += ['', f"- queuedTask: {created_task['id']}"]
    lines += ['', f"- inspect: python3 scripts/sonic_runtime_structure.py session-show {session_id}"]
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description='SONIC harness structure viewer and lightweight harness control plane.')
    sub = ap.add_subparsers(dest='command', required=True)
    sub.add_parser('summary')
    sub.add_parser('manifest')
    c = sub.add_parser('commands')
    c.add_argument('--limit', type=int, default=20)
    t = sub.add_parser('tools')
    t.add_argument('--limit', type=int, default=20)
    f = sub.add_parser('features')
    f.add_argument('--limit', type=int, default=50)
    b = sub.add_parser('backlog')
    b.add_argument('--limit', type=int, default=20)
    route = sub.add_parser('route')
    route.add_argument('prompt')
    route.add_argument('--limit', type=int, default=5)
    sub.add_parser('state')
    sub.add_parser('tick')
    sub.add_parser('token-budget')
    sub.add_parser('compaction-reminder')
    sub.add_parser('bridge-status')
    bridge_set = sub.add_parser('bridge-set')
    bridge_set.add_argument('mode', choices=['on', 'off'])
    bridge_set.add_argument('target', nargs='?')
    dream = sub.add_parser('dream-plan')
    dream.add_argument('--mark-done', action='store_true')
    coord = sub.add_parser('coordinator-plan')
    coord.add_argument('task')
    verify = sub.add_parser('verify-plan')
    verify.add_argument('task')
    execute = sub.add_parser('execution-plan')
    execute.add_argument('task')
    task = sub.add_parser('set-task')
    task.add_argument('task', nargs='?')
    task.add_argument('--status')
    upd = sub.add_parser('backlog-set')
    upd.add_argument('title')
    upd.add_argument('status')
    tasks = sub.add_parser('tasks')
    tasks.add_argument('--limit', type=int, default=20)
    task_add = sub.add_parser('task-add')
    task_add.add_argument('title')
    task_add.add_argument('--trigger', default='manual')
    task_set = sub.add_parser('task-set')
    task_set.add_argument('task_id')
    task_set.add_argument('status')
    turn = sub.add_parser('turn-loop')
    turn.add_argument('prompt')
    turn.add_argument('--max-turns', type=int, default=6)
    sessions = sub.add_parser('sessions')
    sessions.add_argument('--limit', type=int, default=20)
    show = sub.add_parser('session-show')
    show.add_argument('session_id')
    args = ap.parse_args()

    if args.command == 'summary':
        print(render_summary())
        return 0
    if args.command == 'manifest':
        print(build_manifest().to_markdown())
        return 0
    if args.command == 'commands':
        print(render_list(load_json(COMMANDS, []), args.limit))
        return 0
    if args.command == 'tools':
        print(render_list(load_json(TOOLS, []), args.limit))
        return 0
    if args.command == 'features':
        print(render_features(args.limit))
        return 0
    if args.command == 'backlog':
        print(render_backlog(args.limit))
        return 0
    if args.command == 'route':
        print(route_prompt(args.prompt, args.limit))
        return 0
    if args.command == 'state':
        print(render_state())
        return 0
    if args.command == 'tick':
        print(run_tick())
        return 0
    if args.command == 'token-budget':
        print(render_token_budget())
        return 0
    if args.command == 'compaction-reminder':
        print(render_compaction_reminder())
        return 0
    if args.command == 'bridge-status':
        print(render_bridge_status())
        return 0
    if args.command == 'bridge-set':
        print(set_bridge(args.mode == 'on', args.target))
        return 0
    if args.command == 'dream-plan':
        print(render_dream_plan(mark_done=args.mark_done))
        return 0
    if args.command == 'coordinator-plan':
        print(render_coordinator_plan(args.task))
        return 0
    if args.command == 'verify-plan':
        print(render_verify_plan(args.task))
        return 0
    if args.command == 'execution-plan':
        print(render_execution_plan(args.task))
        return 0
    if args.command == 'set-task':
        print(set_current_task(args.task, args.status))
        return 0
    if args.command == 'backlog-set':
        print(update_backlog(args.title, args.status))
        return 0
    if args.command == 'tasks':
        print(render_tasks(args.limit))
        return 0
    if args.command == 'task-add':
        print(add_task(args.title, args.trigger))
        return 0
    if args.command == 'task-set':
        print(update_task(args.task_id, args.status))
        return 0
    if args.command == 'turn-loop':
        print(run_turn_loop(args.prompt, args.max_turns))
        return 0
    if args.command == 'sessions':
        print(render_sessions(args.limit))
        return 0
    if args.command == 'session-show':
        print(render_session(args.session_id))
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
