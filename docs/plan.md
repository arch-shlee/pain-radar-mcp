# Plan

_단기 실행 계획. 완료 후 삭제._

## Day 1~2 (완료)

- [x] `uv init --package` 및 pyproject.toml 작성
- [x] `server.py` 뼈대 — FastMCP 인스턴스, main() 진입점
- [x] `utils/http.py`, `cache.py`, `rate_limiter.py`, `scorer.py`
- [x] `tools/hn.py` — 3개 tool 전부 구현
- [x] pytest 8개 통과
- [x] `.mcp.json` 생성, Claude Code 연결 확인

## Day 3 (진행 중)

- [ ] README 작성 (설치, 사용법, Claude Desktop 설정)

## Day 4

- [ ] pytest 커버리지 60% 이상
- [ ] `pyproject.toml` 정비 (classifiers, 키워드, 링크)
- [ ] `uv publish` → PyPI

## Day 5

- [ ] `uvx pain-radar-mcp` 설치 검증 (클린 환경)
- [ ] awesome-mcp-servers PR
- [ ] 사용 시나리오 GIF 녹화

## 보류 (v2+)

- Stack Overflow API 통합
- G2 통합
- `find_market_gap deep`에서 멀티소스 병합
