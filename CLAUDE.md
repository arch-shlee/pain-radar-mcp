# CLAUDE.md

## 프로젝트 개요

HN/SO/G2에서 개발자 도메인 페인포인트를 실시간으로 발굴하는 MCP 서버.
`uvx pain-radar-mcp`로 설치하며, API key 불필요.

## 기술 스택

| 레이어 | 선택 | 이유 |
|--------|------|------|
| MCP framework | `fastmcp>=3.1,<4` | Python-native, 가장 적은 boilerplate |
| HTTP client | `httpx` | async-first, timeout/retry 내장 |
| Cache | `cachetools` TTLCache | 외부 의존성 없는 인메모리 TTL |
| Python | `>=3.11` | asyncio.TaskGroup, tomllib 내장 |
| 패키지 관리 | `uv` | 빠른 설치, uvx 배포 타깃 |

## 데이터 소스

- **v1**: HN Algolia API — 무인증, 10k req/h 무료
- **v2**: Stack Overflow API (예정)
- **v3**: G2 (예정)

## 프로젝트 구조

```
src/pain_radar_mcp/
├── server.py          # FastMCP 진입점, tool 등록
├── tools/
│   ├── hn.py          # search_hn_pain_points, get_hn_thread_signals, find_market_gap
│   └── (so.py, g2.py — v2, v3)
└── utils/
    ├── http.py        # httpx 공용 클라이언트
    ├── cache.py       # TTLCache 래퍼
    ├── scorer.py      # points + comments 기반 signal 강도 계산
    └── rate_limiter.py  # Algolia 한도 초과 방지
```

## 코딩 규칙

- **Tool은 팩트만 반환** — 비즈니스 방향 추천, 해석은 포함하지 않는다. LLM 역할.
- **출력 포맷은 마크다운 고정** — Claude가 읽기 좋은 구조화된 텍스트.
- **include_comments 기본값 False** — 댓글 API는 명시적으로 켜야 작동.
- **각 tool은 독립 실행 가능** — tool 간 숨겨진 의존성 없음.
- **예외는 user-facing 메시지로** — MCP 클라이언트에 스택 트레이스 노출 금지.

## 제약

- HN Algolia API: 10,000 req/h. `find_market_gap deep`은 rate_limiter 필수.
- PyPI 배포 타깃이므로 로컬 파일 경로 의존성 금지.
- `fastmcp` breaking change 방어: `>=3.1,<4` 고정.
