# Status

_수시 업데이트. 완료 항목은 삭제하지 않고 체크만._

## 현재 단계: Day 1~2 완료

### 완료
- [x] HN Algolia API 스펙 검증
- [x] Tool 설계 (3개 tool, 입출력 확정)
- [x] 프로젝트 구조 확정
- [x] 문서 구조 수립 (CLAUDE.md, docs/)
- [x] `uv init --package` 및 pyproject.toml 작성
- [x] `server.py` 뼈대 + FastMCP 등록
- [x] `utils/http.py` — httpx AsyncClient
- [x] `utils/cache.py` — TTLCache (search 1h, thread 30m)
- [x] `utils/rate_limiter.py` — token bucket (2 req/s)
- [x] `utils/scorer.py` — signal score 공식
- [x] `tools/hn.py` — 3개 tool 구현 (search / signals / gap)
- [x] pytest 8개 통과 (mock 기반)
- [x] 실제 HN API 연동 확인 (observability, kubernetes)

### 완료 (추가)
- [x] `.mcp.json` 생성 — 프로젝트 전용 MCP 서버 등록
- [x] Claude Code에서 pain-radar MCP 서버 연결 확인

### 진행 중
- [ ] README 작성

### 블로커
- 없음

## 마일스톤

| 마일스톤 | 목표일 | 상태 |
|----------|--------|------|
| v0.1 — HN 3개 tool 작동 | Day 3 | 미시작 |
| v0.1 — Claude Desktop 연결 확인 | Day 3 | 미시작 |
| v0.1 — PyPI 배포 | Day 5 | 미시작 |
| v0.2 — SO 통합 | 미정 | 미시작 |
