import json
import pytest
from pytest_httpx import HTTPXMock

from pain_radar_mcp.utils.http import close_client, get_client
from pain_radar_mcp.tools.hn import (
    search_hn_pain_points,
    get_hn_thread_signals,
    find_market_gap,
)
from pain_radar_mcp.utils.cache import get_search_cache, get_thread_cache


@pytest.fixture(autouse=True)
def clear_caches():
    get_search_cache().clear()
    get_thread_cache().clear()
    yield


@pytest.fixture(autouse=True)
async def reset_client():
    yield
    await close_client()


SAMPLE_HITS = [
    {
        "objectID": "111",
        "title": "Ask HN: Why is there no simple log aggregator?",
        "points": 87,
        "num_comments": 143,
        "created_at": "2025-01-10T12:00:00Z",
        "story_text": "Loki is heavy, CloudWatch is expensive, self-hosted ELK is a maintenance nightmare.",
    },
    {
        "objectID": "222",
        "title": "Ask HN: Best observability tool for small teams?",
        "points": 45,
        "num_comments": 60,
        "created_at": "2025-03-01T09:00:00Z",
        "story_text": "Looking for something lightweight.",
    },
]

SAMPLE_ITEM = {
    "objectID": "111",
    "title": "Ask HN: Why is there no simple log aggregator?",
    "points": 87,
    "children": [
        {"author": "alice", "text": "+1 been looking for this for years", "children": []},
        {"author": "bob", "text": "Have you tried Loki?", "children": []},
        {"author": "carol", "text": "same problem here, nothing works well", "children": []},
    ],
}


def _algolia_response(hits: list[dict]) -> dict:
    return {"hits": hits, "nbHits": len(hits), "page": 0, "hitsPerPage": 20}


@pytest.mark.asyncio
async def test_search_returns_formatted_markdown(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=_algolia_response(SAMPLE_HITS))
    httpx_mock.add_response(json=_algolia_response([]))
    httpx_mock.add_response(json=_algolia_response([]))

    result = await search_hn_pain_points("observability", days=365, min_points=10, max_results=5)

    assert "HN 페인포인트 분석" in result
    assert "observability" in result
    assert "Ask HN: Why is there no simple log aggregator?" in result
    assert "news.ycombinator.com" in result


@pytest.mark.asyncio
async def test_search_no_results(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=_algolia_response([]))
    httpx_mock.add_response(json=_algolia_response([]))
    httpx_mock.add_response(json=_algolia_response([]))

    result = await search_hn_pain_points("unknownxyz123", days=30, min_points=100)

    assert "결과 없음" in result


@pytest.mark.asyncio
async def test_search_deduplicates_hits(httpx_mock: HTTPXMock):
    # 같은 hit을 두 쿼리에서 반환
    httpx_mock.add_response(json=_algolia_response(SAMPLE_HITS))
    httpx_mock.add_response(json=_algolia_response(SAMPLE_HITS))  # 중복
    httpx_mock.add_response(json=_algolia_response([]))

    result = await search_hn_pain_points("observability", days=365, min_points=5, max_results=10)

    # 제목이 한 번만 나와야 함
    assert result.count("Why is there no simple log aggregator") == 1


@pytest.mark.asyncio
async def test_search_uses_cache(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=_algolia_response(SAMPLE_HITS))
    httpx_mock.add_response(json=_algolia_response([]))
    httpx_mock.add_response(json=_algolia_response([]))

    result1 = await search_hn_pain_points("observability", days=365, min_points=10, max_results=5)
    result2 = await search_hn_pain_points("observability", days=365, min_points=10, max_results=5)

    # 두 번째 호출은 캐시에서 — API는 3번만 호출됨
    assert result1 == result2
    assert len(httpx_mock.get_requests()) == 3


@pytest.mark.asyncio
async def test_thread_signals_counts_empathy(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=SAMPLE_ITEM)

    result = await get_hn_thread_signals("111")

    assert "공감 반응 감지: 2건" in result
    assert "alice" in result
    assert "been looking for this" in result


@pytest.mark.asyncio
async def test_thread_signals_no_empathy(httpx_mock: HTTPXMock):
    item = {**SAMPLE_ITEM, "children": [{"author": "dave", "text": "Have you tried X?", "children": []}]}
    httpx_mock.add_response(json=item)

    result = await get_hn_thread_signals("111")

    assert "공감 패턴 댓글 없음" in result


@pytest.mark.asyncio
@pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
async def test_find_market_gap_quick(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=_algolia_response(SAMPLE_HITS))
    httpx_mock.add_response(json=_algolia_response([]))
    httpx_mock.add_response(json=_algolia_response([]))

    result = await find_market_gap("observability", depth="quick")

    assert "시장 공백 분석" in result
    assert "depth=quick" in result
    assert "HN 페인포인트 분석" in result


@pytest.mark.asyncio
@pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
async def test_find_market_gap_invalid_depth(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=_algolia_response(SAMPLE_HITS))
    httpx_mock.add_response(json=_algolia_response([]))
    httpx_mock.add_response(json=_algolia_response([]))

    # 잘못된 depth는 quick으로 fallback
    result = await find_market_gap("observability", depth="invalid")

    assert "depth=quick" in result
