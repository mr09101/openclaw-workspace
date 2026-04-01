# Last 30 Days Research: Claude Code

- generated_at: 2026-04-01T11:34:03+09:00
- raw_topic: Claude Code
- parsed_topic: Claude Code
- query_type: GENERAL
- target_tool: unknown
- source_fetch_counts: {'hybrid': 16, 'reddit': 8, 'hn': 8}
- final_items: 8
- final_sources: {'reddit-public': 2, 'hackernews': 2, 'hybrid:naver': 4}
- top_domains: {'code.claude.com': 4, 'reddit.com': 2, 'twitter.com': 1, 'news.ycombinator.com': 1}

## 검색 계획
- 전용 수집: Reddit public JSON, Hacker News Algolia API
- 보조 수집: hybrid search (google/naver/x + 본문 추출)
- Claude Code last 30 days
- Claude Code recent discussion
- Claude Code trends
- site:reddit.com Claude Code
- site:news.ycombinator.com Claude Code
- site:youtube.com Claude Code
- site:polymarket.com Claude Code
- site:x.com Claude Code

## 핵심 메모
- 이번 버전은 검색엔진 링크 수집만 하지 않고, Reddit/HN 전용 수집 신호를 함께 반영합니다.
- Reddit는 score/comment, HN은 points/comments를 사용해 우선순위를 보강합니다.
- hybrid 결과는 보조 소스로만 쓰고, 전용 수집 결과를 우선 배치합니다.
- 외부 skill을 통설치하지 않고, 우리 로컬 검색 체인 위에 cherry-pick으로 강화한 버전입니다.

## 상위 신호
1. 4 months of Claude Code and honestly the hardest part isn’t coding | score=0.940 | reddit score 951 / comments 319
2. I stopped using Claude.ai entirely. I run my entire business through Claude Code. | score=0.940 | reddit score 778 / comments 265
3. Claude Code's source code has been leaked via a map file in their NPM registry | score=0.940 | HN points 1904 / comments 938
4. Tell HN: I'm 60 years old. Claude Code has re-ignited a passion | score=0.940 | HN points 1086 / comments 989
5. code.claude.com›docs | score=0.633 | domain code.claude.com

## 후보 링크
1. [4 months of Claude Code and honestly the hardest part isn’t coding](https://www.reddit.com/r/ClaudeAI/comments/1rr1069/4_months_of_claude_code_and_honestly_the_hardest/)
   - source: reddit-public
   - domain: reddit.com
   - score: 0.940
   - engagement: {'score': 951, 'comments': 319}
   - preview: I’ve been building a full iOS app with Claude Code for about 5 months now. 220k lines, real users starting to test it. The thing nobody talks about is that the coding is actually the easy part at this point.

The hard part is making design decisions. Claude Co…
2. [I stopped using Claude.ai entirely. I run my entire business through Claude Code.](https://www.reddit.com/r/ClaudeAI/comments/1rwmj25/i_stopped_using_claudeai_entirely_i_run_my_entire/)
   - source: reddit-public
   - domain: reddit.com
   - score: 0.940
   - engagement: {'score': 778, 'comments': 265}
   - preview: Someone asked me today why I never use the web app. I realized I haven't opened it in months.

Everything I do runs through Claude Code. Not just coding. My morning routine, my CRM, my content pipeline, my lead sourcing, my follow-ups. All of it.

I built a sy…
3. [Claude Code's source code has been leaked via a map file in their NPM registry](https://twitter.com/Fried_rice/status/2038894956459290963)
   - source: hackernews
   - domain: twitter.com
   - score: 0.940
   - engagement: {'points': 1904, 'comments': 938}
   - hn_discussion: https://news.ycombinator.com/item?id=47584540
   - preview: HN points 1904, comments 938
4. [Tell HN: I'm 60 years old. Claude Code has re-ignited a passion](https://news.ycombinator.com/item?id=47282777)
   - source: hackernews
   - domain: news.ycombinator.com
   - score: 0.940
   - engagement: {'points': 1086, 'comments': 989}
   - hn_discussion: https://news.ycombinator.com/item?id=47282777
   - preview: HN points 1086, comments 989
5. [code.claude.com›docs](https://code.claude.com/docs/en/desktop)
   - source: hybrid:naver
   - domain: code.claude.com
   - score: 0.633
   - preview: Use Claude Code Desktop - Claude Code Docs (function(a,b){try{let c=document.getElementById("banner")?.innerText;if(c){for(let d=0;d ((a,b,c,d,e,f,g,h)=>{let i=document.documentElement,j=["light","dark"];function k(b){va…
6. [Use Claude Code in VS Code - Claude Code Docs](https://code.claude.com/docs/en/vs-code)
   - source: hybrid:naver
   - domain: code.claude.com
   - score: 0.633
   - preview: Use Claude Code in VS Code - Claude Code Docs (function(a,b){try{let c=document.getElementById("banner")?.innerText;if(c){for(let d=0;d ((a,b,c,d,e,f,g,h)=>{let i=document.documentElement,j=["light","dark"];function k(b)…
7. [code.claude.com›common-workflows](https://code.claude.com/docs/en/common-workflows)
   - source: hybrid:naver
   - domain: code.claude.com
   - score: 0.633
   - preview: Common workflows - Claude Code Docs (function(a,b){try{let c=document.getElementById("banner")?.innerText;if(c){for(let d=0;d ((a,b,c,d,e,f,g,h)=>{let i=document.documentElement,j=["light","dark"];function k(b){var c;(Ar…
8. [Claude Code GitLab CI/CD - Claude Code Docs](https://code.claude.com/docs/en/gitlab-ci-cd)
   - source: hybrid:naver
   - domain: code.claude.com
   - score: 0.633
   - preview: Claude Code GitLab CI/CD - Claude Code Docs (function(a,b){try{let c=document.getElementById("banner")?.innerText;if(c){for(let d=0;d ((a,b,c,d,e,f,g,h)=>{let i=document.documentElement,j=["light","dark"];function k(b){v…

## 후속 액션 제안
- 상위 3~5개 링크를 읽고 공통 주장/중복 키워드를 묶는다.
- 출처 간 반복되는 주장만 “강한 신호”로 승격한다.
- 다음 단계로는 Reddit 댓글 상위 의견과 HN top comments까지 추가 enrichment 하면 질이 더 올라갑니다.
