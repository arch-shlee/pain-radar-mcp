# ADR 003: Tool을 3개로 분리 (search / signals / gap)

- **날짜**: 2026-03-22
- **상태**: 확정

## 맥락

HN 분석 기능을 단일 tool로 만들지, 여러 tool로 분리할지 결정해야 한다.

## 결정

3개 tool로 분리:
1. `search_hn_pain_points` — 도메인 키워드로 페인포인트 검색
2. `get_hn_thread_signals` — 단일 스레드의 댓글 공감 신호 분석
3. `find_market_gap` — 위 두 tool을 조합한 종합 분석

## 근거

- **Claude가 필요에 따라 조합 가능** — LLM이 tool을 단계적으로 호출하는 것이 단일 monolithic tool보다 유연
- **단계별 비용 제어** — `search_hn_pain_points`만 쓰면 빠르고, `get_hn_thread_signals`는 필요한 스레드에만 호출
- **테스트 용이성** — 각 tool을 독립적으로 단위 테스트 가능
- **`find_market_gap`은 편의 tool** — Claude가 직접 조합 대신 편하게 쓸 수 있는 shortcut

## 결과

- `tools/hn.py`에 3개 함수 구현, 각각 `@mcp.tool` 데코레이터
- `include_comments` 기본값 `False` — 댓글 분석은 명시적으로 켜야 함
- Tool 간 숨겨진 상태 공유 없음 (각 tool 독립 실행 가능)
