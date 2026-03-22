# ADR 002: MCP 프레임워크로 FastMCP 선택

- **날짜**: 2026-03-22
- **상태**: 확정

## 맥락

Python으로 MCP 서버를 구현할 때 사용할 프레임워크를 선정해야 한다.
후보는 FastMCP, 공식 MCP Python SDK (`mcp` 패키지), 직접 구현이다.

## 결정

`fastmcp>=3.1,<4` 사용.

## 근거

- **데코레이터 기반 tool 등록** (`@mcp.tool`)으로 boilerplate 최소화
- 공식 SDK보다 추상화 수준이 높아 tool 로직에 집중 가능
- `uvx` 배포 타깃과 궁합이 좋음 (진입점 패턴이 동일)
- 직접 구현 대비 stdio transport, 에러 직렬화 등 처리 내장

## 트레이드오프

- FastMCP 메이저 버전 업 시 breaking change 위험 → `<4` 상한선으로 방어
- 공식 SDK보다 커뮤니티 규모 작음 → 장기적으로 마이그레이션 가능성 존재

## 결과

- `pyproject.toml`에 `fastmcp>=3.1,<4` 고정
- `server.py`에서 `from fastmcp import FastMCP` 패턴 사용
