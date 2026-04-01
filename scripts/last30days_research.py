#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path('/home/hskim/.openclaw/workspace')
HYBRID = ROOT / 'scripts' / 'hybrid_scrapling_search.py'
OUT_DIR = ROOT / 'reports' / 'last30days'
UA = 'OpenClaw-Last30Days/2.0'

COMPARISON_RE = re.compile(r'\s+(?:vs\.?|versus)\s+', re.IGNORECASE)
TOOL_RE = re.compile(r'\bfor\s+([A-Za-z0-9][A-Za-z0-9 .+\-_/]{1,40})$', re.IGNORECASE)
WORD_RE = re.compile(r'[A-Za-z][A-Za-z0-9_\-]{1,}|[가-힣]{2,}')
LOW_SIGNAL_DOMAINS = {'m.search.naver.com', 'search.naver.com'}


def slugify(text: str) -> str:
    slug = re.sub(r'[^A-Za-z0-9가-힣]+', '-', text.strip()).strip('-').lower()
    return slug[:80] or 'topic'


def clean_topic(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip(' -')


def q_tokens(text: str) -> set[str]:
    return {tok.lower() for tok in WORD_RE.findall(text)}


def classify_query_type(text: str) -> str:
    low = text.lower()
    if COMPARISON_RE.search(text):
        return 'COMPARISON'
    if any(k in low for k in ['prompt', 'prompts', 'prompting']):
        return 'PROMPTING'
    if any(k in low for k in ['best ', 'top ', '추천', 'recommend', 'recommended']):
        return 'RECOMMENDATIONS'
    if any(k in low for k in ['news', 'latest', 'update', 'release', 'what\'s happening', '무슨 일', '업데이트']):
        return 'NEWS'
    return 'GENERAL'


def parse_intent(raw_topic: str) -> dict[str, Any]:
    text = clean_topic(raw_topic)
    query_type = classify_query_type(text)
    target_tool = None
    match_tool = TOOL_RE.search(text)
    if match_tool and query_type != 'COMPARISON':
        target_tool = clean_topic(match_tool.group(1))
        text = clean_topic(text[:match_tool.start()])

    parsed: dict[str, Any] = {
        'raw_topic': raw_topic,
        'topic': text,
        'query_type': query_type,
        'target_tool': target_tool,
    }
    if query_type == 'COMPARISON':
        parts = COMPARISON_RE.split(text, maxsplit=1)
        if len(parts) == 2:
            parsed['topic_a'] = clean_topic(parts[0])
            parsed['topic_b'] = clean_topic(parts[1])
    return parsed


def queries_for_single(topic: str, days: int, query_type: str, target_tool: str | None = None) -> list[str]:
    base = [
        f'{topic} last {days} days',
        f'{topic} recent discussion',
        f'{topic} trends',
        f'site:reddit.com {topic}',
        f'site:news.ycombinator.com {topic}',
        f'site:youtube.com {topic}',
        f'site:polymarket.com {topic}',
        f'site:x.com {topic}',
    ]
    if query_type == 'PROMPTING':
        base += [f'{topic} prompt tips', f'{topic} workflow', f'{topic} best prompts']
    elif query_type == 'RECOMMENDATIONS':
        base += [f'best {topic}', f'top {topic}', f'{topic} recommended']
    elif query_type == 'NEWS':
        base += [f'{topic} latest update', f'{topic} release', f'{topic} news']
    if target_tool:
        base += [f'{topic} for {target_tool}', f'{topic} {target_tool} workflow']
    return base


def build_queries(parsed: dict[str, Any], days: int) -> list[str]:
    if parsed['query_type'] == 'COMPARISON' and parsed.get('topic_a') and parsed.get('topic_b'):
        a = parsed['topic_a']
        b = parsed['topic_b']
        queries = [
            f'{a} vs {b} last {days} days',
            f'{a} versus {b}',
            f'{a} or {b}',
        ]
        queries += queries_for_single(a, days, 'GENERAL')[:4]
        queries += queries_for_single(b, days, 'GENERAL')[:4]
        return queries
    return queries_for_single(parsed['topic'], days, parsed['query_type'], parsed.get('target_tool'))


def http_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as resp:
        return json.loads(resp.read().decode('utf-8', errors='ignore'))


def domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        return netloc.removeprefix('www.') or 'unknown'
    except Exception:
        return 'unknown'


def iso_date_from_ts(ts: float | int | None) -> str | None:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime('%Y-%m-%d')
    except Exception:
        return None


def score_match(text: str, query_tokens: set[str]) -> float:
    tokens = q_tokens(text)
    if not tokens or not query_tokens:
        return 0.0
    overlap = len(tokens & query_tokens)
    return min(1.0, overlap / max(2, min(len(query_tokens), 6)))


def infer_bucket(item: dict[str, Any], parsed: dict[str, Any]) -> str:
    if parsed['query_type'] != 'COMPARISON':
        return 'main'
    a = str(parsed.get('topic_a') or '').lower()
    b = str(parsed.get('topic_b') or '').lower()
    hay = ' '.join([
        str(item.get('title') or ''),
        str(item.get('preview') or ''),
        str(item.get('url') or ''),
    ]).lower()
    hit_a = a and a in hay
    hit_b = b and b in hay
    if hit_a and hit_b:
        return 'both'
    if hit_a:
        return 'topic_a'
    if hit_b:
        return 'topic_b'
    return 'shared'


def is_low_signal(item: dict[str, Any]) -> bool:
    url = str(item.get('url') or '').strip()
    title = str(item.get('title') or '').strip().lower()
    dom = domain_of(url)
    if not url or dom in LOW_SIGNAL_DOMAINS:
        return True
    if title in {'google-result', 'x-post', 'untitled'}:
        return True
    return False


def queries_topic_for_source(parsed: dict[str, Any]) -> str:
    if parsed['query_type'] == 'COMPARISON' and parsed.get('topic_a') and parsed.get('topic_b'):
        return f"{parsed['topic_a']} {parsed['topic_b']}"
    return parsed['topic']


def search_reddit_public(parsed: dict[str, Any], days: int, limit: int) -> list[dict[str, Any]]:
    topic = queries_topic_for_source(parsed)
    q = urllib.parse.quote_plus(topic)
    url = f'https://www.reddit.com/search.json?q={q}&sort=relevance&t=month&limit={limit}&raw_json=1'
    try:
        data = http_json(url, timeout=20)
    except Exception:
        return []

    items: list[dict[str, Any]] = []
    children = data.get('data', {}).get('children', [])
    min_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')
    for child in children:
        if child.get('kind') != 't3':
            continue
        post = child.get('data', {})
        permalink = str(post.get('permalink') or '')
        if '/comments/' not in permalink:
            continue
        date = iso_date_from_ts(post.get('created_utc'))
        if date and date < min_date:
            continue
        title = str(post.get('title') or '').strip()
        selftext = str(post.get('selftext') or '').strip()
        score = int(post.get('score') or 0)
        comments = int(post.get('num_comments') or 0)
        items.append({
            'title': title,
            'url': f'https://www.reddit.com{permalink}',
            'source': 'reddit-public',
            'author': str(post.get('author') or ''),
            'date': date,
            'preview': (selftext[:260] + '…') if len(selftext) > 260 else selftext,
            'engagement': {'score': score, 'comments': comments},
        })
    return items


def search_hn(parsed: dict[str, Any], days: int, limit: int) -> list[dict[str, Any]]:
    topic = queries_topic_for_source(parsed)
    from_ts = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    params = urllib.parse.urlencode({
        'query': topic,
        'tags': 'story',
        'numericFilters': f'created_at_i>{from_ts}',
        'hitsPerPage': str(limit),
    })
    url = f'https://hn.algolia.com/api/v1/search?{params}'
    try:
        data = http_json(url, timeout=20)
    except Exception:
        return []

    items: list[dict[str, Any]] = []
    for hit in data.get('hits', []):
        object_id = str(hit.get('objectID') or '').strip()
        title = str(hit.get('title') or '').strip()
        if not object_id or not title:
            continue
        story_url = str(hit.get('url') or '').strip() or f'https://news.ycombinator.com/item?id={object_id}'
        points = int(hit.get('points') or 0)
        comments = int(hit.get('num_comments') or 0)
        date = None
        created_at_i = hit.get('created_at_i')
        if created_at_i:
            date = iso_date_from_ts(created_at_i)
        items.append({
            'title': title,
            'url': story_url,
            'source': 'hackernews',
            'author': str(hit.get('author') or ''),
            'date': date,
            'preview': f"HN points {points}, comments {comments}",
            'engagement': {'points': points, 'comments': comments},
            'hn_discussion_url': f'https://news.ycombinator.com/item?id={object_id}',
        })
    return items


def run_hybrid(queries: list[str], max_items: int) -> list[dict[str, Any]]:
    cmd = [sys.executable, str(HYBRID)]
    for q in queries:
        cmd += ['--query', q]
    cmd += ['--max-items', str(max_items)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        return []
    raw = proc.stdout.strip()
    if not raw:
        return []
    data = json.loads(raw)
    if not data.get('ok'):
        return []
    items = data.get('items') or []
    for item in items:
        item['source'] = f"hybrid:{item.get('source') or 'unknown'}"
        item.setdefault('engagement', {})
    return items


def compute_item_score(item: dict[str, Any], parsed: dict[str, Any]) -> float:
    topic_text = parsed['raw_topic'] if parsed['query_type'] == 'COMPARISON' else parsed['topic']
    query_tokens = q_tokens(topic_text)
    title = str(item.get('title') or '')
    preview = str(item.get('preview') or '')
    source = str(item.get('source') or '')
    match = max(score_match(title, query_tokens), score_match(preview, query_tokens) * 0.8)

    engagement = item.get('engagement') or {}
    engagement_score = 0.0
    if source == 'reddit-public':
        engagement_score = min(1.0, (float(engagement.get('score') or 0) / 300.0) * 0.65 + (float(engagement.get('comments') or 0) / 120.0) * 0.35)
    elif source == 'hackernews':
        engagement_score = min(1.0, (float(engagement.get('points') or 0) / 200.0) * 0.65 + (float(engagement.get('comments') or 0) / 80.0) * 0.35)
    else:
        engagement_score = 0.15

    bucket_bonus = 0.0
    bucket = infer_bucket(item, parsed)
    if parsed['query_type'] == 'COMPARISON':
        if bucket == 'both':
            bucket_bonus = 0.18
        elif bucket in {'topic_a', 'topic_b'}:
            bucket_bonus = 0.08

    source_bonus = 0.12 if source in {'reddit-public', 'hackernews'} else 0.0
    return round(match * 0.6 + engagement_score * 0.22 + source_bonus + bucket_bonus, 4)


def merge_items(parsed: dict[str, Any], hybrid_items: list[dict[str, Any]], reddit_items: list[dict[str, Any]], hn_items: list[dict[str, Any]], max_items: int) -> list[dict[str, Any]]:
    merged = reddit_items + hn_items + hybrid_items
    seen: set[str] = set()
    cleaned: list[dict[str, Any]] = []
    for item in merged:
        url = str(item.get('url') or '').strip()
        if not url or url in seen or is_low_signal(item):
            continue
        seen.add(url)
        item['score'] = compute_item_score(item, parsed)
        cleaned.append(item)
    cleaned.sort(key=lambda x: (x.get('score') or 0.0), reverse=True)

    quotas = {'reddit-public': max(2, max_items // 3), 'hackernews': max(2, max_items // 3)}
    picked: list[dict[str, Any]] = []
    counts = defaultdict(int)

    # first pass: favor source diversity
    for item in cleaned:
        source = str(item.get('source') or '')
        if source in quotas and counts[source] >= quotas[source]:
            continue
        picked.append(item)
        counts[source] += 1
        if len(picked) >= max_items:
            return picked

    # second pass: fill remaining regardless of source
    if len(picked) < max_items:
        picked_urls = {str(i.get('url')) for i in picked}
        for item in cleaned:
            if str(item.get('url')) in picked_urls:
                continue
            picked.append(item)
            if len(picked) >= max_items:
                break
    return picked[:max_items]


def summarize(items: list[dict[str, Any]], parsed: dict[str, Any], days: int, queries: list[str], raw_counts: dict[str, int]) -> str:
    engine_counter = Counter(str(item.get('source') or 'unknown') for item in items)
    domain_counter = Counter(domain_of(str(item.get('url') or '')) for item in items)
    bucket_counter = Counter(infer_bucket(item, parsed) for item in items)

    lines: list[str] = []
    lines.append(f"# Last {days} Days Research: {parsed['raw_topic']}")
    lines.append('')
    lines.append(f'- generated_at: {datetime.now().astimezone().isoformat(timespec="seconds")}')
    lines.append(f"- raw_topic: {parsed['raw_topic']}")
    lines.append(f"- parsed_topic: {parsed['topic']}")
    lines.append(f"- query_type: {parsed['query_type']}")
    lines.append(f"- target_tool: {parsed.get('target_tool') or 'unknown'}")
    if parsed['query_type'] == 'COMPARISON':
        lines.append(f"- topic_a: {parsed.get('topic_a')}")
        lines.append(f"- topic_b: {parsed.get('topic_b')}")
    lines.append(f'- source_fetch_counts: {raw_counts}')
    lines.append(f'- final_items: {len(items)}')
    lines.append(f'- final_sources: {dict(engine_counter)}')
    lines.append(f'- top_domains: {dict(domain_counter.most_common(8))}')
    if parsed['query_type'] == 'COMPARISON':
        lines.append(f'- buckets: {dict(bucket_counter)}')
    lines.append('')

    lines.append('## 검색 계획')
    lines.append('- 전용 수집: Reddit public JSON, Hacker News Algolia API')
    lines.append('- 보조 수집: hybrid search (google/naver/x + 본문 추출)')
    for q in queries:
        lines.append(f'- {q}')
    lines.append('')

    lines.append('## 핵심 메모')
    lines.append('- 이번 버전은 검색엔진 링크 수집만 하지 않고, Reddit/HN 전용 수집 신호를 함께 반영합니다.')
    lines.append('- Reddit는 score/comment, HN은 points/comments를 사용해 우선순위를 보강합니다.')
    lines.append('- hybrid 결과는 보조 소스로만 쓰고, 전용 수집 결과를 우선 배치합니다.')
    lines.append('- 외부 skill을 통설치하지 않고, 우리 로컬 검색 체인 위에 cherry-pick으로 강화한 버전입니다.')
    lines.append('')

    lines.append('## 상위 신호')
    for idx, item in enumerate(items[:5], start=1):
        source = str(item.get('source') or 'unknown')
        score = item.get('score') or 0.0
        title = str(item.get('title') or 'untitled').strip()
        why = []
        if source == 'reddit-public':
            eng = item.get('engagement') or {}
            why.append(f"reddit score {eng.get('score', 0)} / comments {eng.get('comments', 0)}")
        elif source == 'hackernews':
            eng = item.get('engagement') or {}
            why.append(f"HN points {eng.get('points', 0)} / comments {eng.get('comments', 0)}")
        else:
            why.append(f"domain {domain_of(str(item.get('url') or ''))}")
        if parsed['query_type'] == 'COMPARISON':
            why.append(f"bucket {infer_bucket(item, parsed)}")
        lines.append(f'{idx}. {title} | score={score:.3f} | ' + ' | '.join(why))
    lines.append('')

    lines.append('## 후보 링크')
    for idx, item in enumerate(items, start=1):
        title = str(item.get('title') or 'untitled').strip()
        url = str(item.get('url') or '').strip()
        source = str(item.get('source') or 'unknown').strip()
        preview = str(item.get('preview') or '').strip()
        dom = domain_of(url)
        score = item.get('score') or 0.0
        lines.append(f'{idx}. [{title}]({url})')
        lines.append(f'   - source: {source}')
        lines.append(f'   - domain: {dom}')
        lines.append(f'   - score: {score:.3f}')
        if parsed['query_type'] == 'COMPARISON':
            lines.append(f"   - bucket: {infer_bucket(item, parsed)}")
        eng = item.get('engagement') or {}
        if eng:
            lines.append(f'   - engagement: {eng}')
        if 'hn_discussion_url' in item:
            lines.append(f"   - hn_discussion: {item['hn_discussion_url']}")
        if preview:
            lines.append(f'   - preview: {preview}')
    lines.append('')

    lines.append('## 후속 액션 제안')
    lines.append('- 상위 3~5개 링크를 읽고 공통 주장/중복 키워드를 묶는다.')
    if parsed['query_type'] == 'COMPARISON':
        lines.append('- topic_a / topic_b 각각 장점·약점·반복 언급 포인트를 분리한다.')
        lines.append('- 양쪽에 동시에 등장하는 비교 포인트만 “실전 비교축”으로 승격한다.')
    else:
        lines.append('- 출처 간 반복되는 주장만 “강한 신호”로 승격한다.')
    lines.append('- 다음 단계로는 Reddit 댓글 상위 의견과 HN top comments까지 추가 enrichment 하면 질이 더 올라갑니다.')
    return '\n'.join(lines) + '\n'


def main() -> None:
    ap = argparse.ArgumentParser(description='Build a local last-30-days research brief with source-specific collection.')
    ap.add_argument('topic', help='research topic')
    ap.add_argument('--days', type=int, default=30)
    ap.add_argument('--max-items', type=int, default=10)
    ap.add_argument('--save', action='store_true', help='save markdown report under reports/last30days/')
    args = ap.parse_args()

    parsed = parse_intent(args.topic)
    queries = build_queries(parsed, args.days)

    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = {
            ex.submit(run_hybrid, queries, max(12, args.max_items * 2)): 'hybrid',
            ex.submit(search_reddit_public, parsed, args.days, max(8, args.max_items)): 'reddit',
            ex.submit(search_hn, parsed, args.days, max(8, args.max_items)): 'hn',
        }
        results: dict[str, list[dict[str, Any]]] = {'hybrid': [], 'reddit': [], 'hn': []}
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception:
                results[key] = []

    items = merge_items(parsed, results['hybrid'], results['reddit'], results['hn'], args.max_items)
    report = summarize(items, parsed, args.days, queries, {k: len(v) for k, v in results.items()})

    if args.save:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().astimezone().strftime('%Y-%m-%d')
        path = OUT_DIR / f'{stamp}-{slugify(args.topic)}.md'
        path.write_text(report, encoding='utf-8')
        print(str(path))
        return

    print(report)


if __name__ == '__main__':
    main()
