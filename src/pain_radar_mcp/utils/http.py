import httpx

_client: httpx.AsyncClient | None = None

HN_ALGOLIA_BASE = "https://hn.algolia.com/api/v1"


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=HN_ALGOLIA_BASE,
            timeout=httpx.Timeout(10.0, connect=5.0),
            headers={"User-Agent": "pain-radar-mcp/0.1"},
        )
    return _client


async def close_client() -> None:
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None
