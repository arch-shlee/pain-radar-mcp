# Architecture

_Last updated: 2026-03-22 | v0.1 (pre-implementation)_

## 흐름도

```
Claude (MCP Client)
    │
    │  MCP Protocol (stdio)
    ▼
server.py (FastMCP)
    ├── search_hn_pain_points(domain, days, min_points, ...)
    ├── get_hn_thread_signals(story_id)
    └── find_market_gap(domain, depth)
         │
         ▼
    tools/hn.py
         │  병렬 쿼리 (asyncio.gather)
         ▼
    utils/http.py  ──→  HN Algolia API
    utils/cache.py      https://hn.algolia.com/api/v1/
    utils/scorer.py
    utils/rate_limiter.py
```

## Tool 책임 분리

| Tool | 입력 | 출력 | 비고 |
|------|------|------|------|
| `search_hn_pain_points` | domain, days, min_points | 페인포인트 목록 (markdown) | 핵심 tool |
| `get_hn_thread_signals` | story_id | 댓글 공감 신호 요약 | 단일 스레드 깊이 분석 |
| `find_market_gap` | domain, depth | 미해결 문제 Top 5 + 수요 강도 | 두 tool을 조합 |

## 쿼리 전략

`search_hn_pain_points` 내부에서 3개 패턴을 병렬 실행 후 병합:

```python
PAIN_QUERIES = [
    f"why doesn't {domain} exist",
    f"{domain} tool wish",
    f"{domain} frustrated",
]
```

결과 파이프라인: 병렬 fetch → 중복 제거 (story_id 기준) → scorer 정렬 → 상위 N개 반환

## 캐시 전략

| 대상 | TTL | 이유 |
|------|-----|------|
| search 결과 | 1시간 | Algolia 한도 절약 |
| 단일 스레드 댓글 | 30분 | 댓글은 조금 더 빠르게 변함 |

## v2, v3 확장 지점

`tools/` 아래 `so.py`, `g2.py` 추가. `server.py`에 import만 추가하면 됨.
`find_market_gap`은 depth='deep'에서 소스 확장 예정.
