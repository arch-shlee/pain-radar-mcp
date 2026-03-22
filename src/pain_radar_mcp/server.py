from fastmcp import FastMCP

from pain_radar_mcp.tools.hn import (
    find_market_gap,
    get_hn_thread_signals,
    search_hn_pain_points,
)
from pain_radar_mcp.utils.http import close_client

mcp = FastMCP(
    name="pain-radar",
    instructions=(
        "HN(Hacker News)에서 개발자 도메인의 페인포인트와 미충족 수요를 발굴합니다. "
        "search_hn_pain_points로 키워드 검색, get_hn_thread_signals로 단일 스레드 깊이 분석, "
        "find_market_gap으로 종합 시장 공백 분석을 실행합니다."
    ),
)

mcp.tool()(search_hn_pain_points)
mcp.tool()(get_hn_thread_signals)
mcp.tool()(find_market_gap)


def main() -> None:
    try:
        mcp.run()
    finally:
        import asyncio
        asyncio.get_event_loop().run_until_complete(close_client())


if __name__ == "__main__":
    main()
