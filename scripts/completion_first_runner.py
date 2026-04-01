#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

ROOT = Path('/home/hskim/.openclaw/workspace')
RUNTIME_DIR = ROOT / 'runtime' / 'assistant_structure'
JOBS_PATH = RUNTIME_DIR / 'background_jobs.json'


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec='seconds')


def load_jobs() -> list[dict[str, Any]]:
    if not JOBS_PATH.exists():
        return []
    return json.loads(JOBS_PATH.read_text(encoding='utf-8'))


def save_jobs(rows: list[dict[str, Any]]) -> None:
    JOBS_PATH.parent.mkdir(parents=True, exist_ok=True)
    JOBS_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def upsert_job(job: dict[str, Any]) -> None:
    rows = load_jobs()
    for idx, row in enumerate(rows):
        if row.get('id') == job['id']:
            rows[idx] = job
            save_jobs(rows)
            return
    rows.insert(0, job)
    save_jobs(rows)


def read_summary(path: Path | None) -> str:
    if not path or not path.exists():
        return '요약 파일이 없어 기본 완료 보고만 보냅니다.'
    text = path.read_text(encoding='utf-8', errors='ignore').strip()
    if not text:
        return '요약 파일이 비어 있어 기본 완료 보고만 보냅니다.'
    return text[:1400]


def run_shell(command: str, cwd: Path) -> int:
    proc = subprocess.run(['bash', '-lc', command], cwd=str(cwd))
    return int(proc.returncode)


def build_report_text(label: str, status: str, verify_status: str, summary: str, result_path: str, job_id: str) -> str:
    lines = [
        '끝났습니다.',
        f'작업: {label}',
        f'상태: {status}',
        f'검증: {verify_status}',
        f'결과: {result_path}',
        f'작업ID: {job_id}',
        '',
        '핵심 변경:',
        summary,
    ]
    return '\n'.join(lines)


def send_system_event(text: str, mode: str) -> int:
    proc = subprocess.run([
        'openclaw', 'system', 'event',
        '--mode', mode,
        '--text', text,
    ])
    return int(proc.returncode)


def main() -> int:
    ap = argparse.ArgumentParser(description='Run a background coding/shell job and emit a completion-first system event when it ends.')
    ap.add_argument('--label', required=True, help='Human-facing job label')
    ap.add_argument('--workdir', required=True, help='Working directory')
    ap.add_argument('--command', required=True, help='Shell command to run')
    ap.add_argument('--verify-command', help='Optional shell command to run after main command')
    ap.add_argument('--summary-file', help='Optional file path containing human summary to include in the completion report')
    ap.add_argument('--result-path', help='Optional result path to show in completion report')
    ap.add_argument('--mode', default='now', choices=['now', 'next-heartbeat'])
    ap.add_argument('--no-notify', action='store_true', help='Skip sending openclaw system event (for dry-run tests)')
    args = ap.parse_args()

    workdir = Path(args.workdir).expanduser().resolve()
    summary_file = Path(args.summary_file).expanduser().resolve() if args.summary_file else None
    result_path = args.result_path or str(workdir)
    job_id = f'bgjob-{uuid4().hex[:10]}'

    job: dict[str, Any] = {
        'id': job_id,
        'label': args.label,
        'workdir': str(workdir),
        'command': args.command,
        'verifyCommand': args.verify_command,
        'summaryFile': str(summary_file) if summary_file else None,
        'resultPath': result_path,
        'status': 'running',
        'startedAt': now_iso(),
        'finishedAt': None,
        'commandExitCode': None,
        'verifyExitCode': None,
        'notifyExitCode': None,
        'notifiedAt': None,
    }
    upsert_job(job)

    command_exit = run_shell(args.command, workdir)
    verify_exit = None
    verify_status = '검증 생략'
    if args.verify_command:
        verify_exit = run_shell(args.verify_command, workdir)
        verify_status = '검증 통과' if verify_exit == 0 else f'검증 실패({verify_exit})'

    summary = read_summary(summary_file)
    status = '완료' if command_exit == 0 else f'실패({command_exit})'
    text = build_report_text(args.label, status, verify_status, summary, result_path, job_id)

    notify_exit = None
    if not args.no_notify:
        notify_exit = send_system_event(text, args.mode)

    job['status'] = 'completed' if command_exit == 0 else 'failed'
    job['finishedAt'] = now_iso()
    job['commandExitCode'] = command_exit
    job['verifyExitCode'] = verify_exit
    job['notifyExitCode'] = notify_exit
    job['notifiedAt'] = None if args.no_notify else now_iso()
    job['summaryPreview'] = summary[:300]
    upsert_job(job)

    print(json.dumps({
        'jobId': job_id,
        'status': job['status'],
        'commandExitCode': command_exit,
        'verifyExitCode': verify_exit,
        'notifyExitCode': notify_exit,
        'workdir': str(workdir),
    }, ensure_ascii=False))
    return command_exit


if __name__ == '__main__':
    raise SystemExit(main())
