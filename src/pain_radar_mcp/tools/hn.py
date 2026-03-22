import asyncio
import time
from datetime import datetime, timezone

from pain_radar_mcp.utils.cache import get_search_cache, get_thread_cache, make_key
from pain_radar_mcp.utils.http import get_client
from pain_radar_mcp.utils.rate_limiter import hn_limiter
from pain_radar_mcp.utils.scorer import sort_by_signal, signal_score

# 댓글에서 공감 반응을 나타내는 패턴
EMPATHY_PATTERNS = [
    "+1",
    "same problem",
    "same issue",
    "been looking for this",
    "been waiting for",
    "we need this",
    "would love this",
    "wish this existed",
    "looking for the same",
    "same here",
    "this is exactly",
    "been wanting",
]


def _hn_url(story_id: str) -> str:
    return f"https://news.ycombinator.com/item?id={story_id}"


def _since_timestamp(days: int) -> int:
    now = datetime.now(timezone.utc)
    return int(now.timestamp()) - days * 86400


async def _search(query: str, tags: str, numeric_filters: str, hits_per_page: int = 20) -> list[dict]:
    await hn_limiter.acquire()
    client = get_client()
    resp = await client.get(
        "/search",
        params={
            "query": query,
            "tags": tags,
            "numericFilters": numeric_filters,
            "hitsPerPage": hits_per_page,
        },
    )
    resp.raise_for_status()
    return resp.json().get("hits", [])


async def _fetch_item(story_id: str) -> dict:
    await hn_limiter.acquire()
    client = get_client()
    resp = await client.get(f"/items/{story_id}")
    resp.raise_for_status()
    return resp.json()


def _count_empathy(comments: list[dict]) -> int:
    count = 0
    for c in comments:
        text = (c.get("text") or "").lower()
        if any(p in text for p in EMPATHY_PATTERNS):
            count += 1
        # 재귀적으로 대댓글도 확인
        for child in c.get("children") or []:
            child_text = (child.get("text") or "").lower()
            if any(p in child_text for p in EMPATHY_PATTERNS):
                count += 1
    return count


def _format_pain_point(hit: dict, empathy: int = 0) -> str:
    story_id = hit.get("objectID") or hit.get("story_id") or ""
    title = hit.get("title") or "(제목 없음)"
    points = hit.get("points") or 0
    num_comments = hit.get("num_comments") or 0
    created = hit.get("created_at") or ""
    text = hit.get("story_text") or ""
    score = signal_score(points, num_comments)

    lines = [
        f"**{title}**",
        f"- 신호 강도: {score:.0f} (포인트 {points}, 댓글 {num_comments}개)",
    ]
    if empathy:
        lines.append(f"- 댓글 공감 반응: {empathy}건")
    if created:
        lines.append(f"- 작성일: {created[:10]}")
    if text:
        snippet = text[:300].replace("\n", " ").strip()
        if len(text) > 300:
            snippet += "..."
        lines.append(f"- 본문 요약: {snippet}")
    if story_id:
        lines.append(f"- 링크: {_hn_url(story_id)}")

    return "\n".join(lines)


async def search_hn_pain_points(
    domain: str,
    days: int = 365,
    min_points: int = 10,
    include_comments: bool = False,
    max_results: int = 10,
) -> str:
    """
    HN에서 특정 도메인의 미충족 수요와 페인포인트를 탐색합니다.

    'Ask HN: Why doesn't X exist', 'Ask HN: What software do you wish existed',
    'Ask HN: Is there a tool for...' 패턴의 스레드를 수집하고
    신호 강도(포인트 + 댓글 수) 순으로 정렬합니다.

    Args:
        domain: 탐색 도메인 (예: "kubernetes", "observability", "data pipeline")
        days: 최근 N일 이내 (기본 365일)
        min_points: 최소 포인트 (노이즈 필터, 기본 10)
        include_comments: 댓글 공감 반응 분석 포함 여부 (기본 False, API 호출 증가)
        max_results: 반환할 최대 결과 수 (기본 10)
    """
    cache_key = make_key("search", domain, days, min_points, include_comments, max_results)
    cache = get_search_cache()
    if cache_key in cache:
        return cache[cache_key]

    since = _since_timestamp(days)
    numeric_filters = f"points>{min_points},created_at_i>{since}"

    # (query, tags) 쌍: ask_hn은 직접 고민/질문, story는 불만/시장 부재 논의
    query_tag_pairs = [
        (domain, "ask_hn"),
        (f"{domain} wish", "ask_hn"),
        (f"{domain} problem", "story"),
    ]

    # 3개 쿼리 병렬 실행
    results = await asyncio.gather(
        *[_search(q, tag, numeric_filters) for q, tag in query_tag_pairs],
        return_exceptions=True,
    )

    # 병합 + 중복 제거
    seen: set[str] = set()
    hits: list[dict] = []
    for batch in results:
        if isinstance(batch, Exception):
            continue
        for hit in batch:
            oid = hit.get("objectID", "")
            if oid and oid not in seen:
                seen.add(oid)
                hits.append(hit)

    hits = sort_by_signal(hits)[:max_results]

    if not hits:
        return f"## HN 페인포인트 분석: \"{domain}\"\n\n결과 없음. 도메인 키워드를 바꿔보세요."

    # 댓글 분석 (선택)
    empathy_map: dict[str, int] = {}
    if include_comments:
        async def _get_empathy(hit: dict) -> tuple[str, int]:
            oid = hit.get("objectID", "")
            thread_cache = get_thread_cache()
            ck = make_key("thread", oid)
            if ck in thread_cache:
                return oid, thread_cache[ck]
            item = await _fetch_item(oid)
            count = _count_empathy(item.get("children") or [])
            thread_cache[ck] = count
            return oid, count

        empathy_results = await asyncio.gather(
            *[_get_empathy(h) for h in hits],
            return_exceptions=True,
        )
        for r in empathy_results:
            if not isinstance(r, Exception):
                oid, count = r
                empathy_map[oid] = count

    # 출력 포맷
    lines = [
        f"## HN 페인포인트 분석: \"{domain}\" (최근 {days}일)",
        f"분석 결과 {len(hits)}개 스레드",
        "",
    ]

    high = [h for h in hits if signal_score(h.get("points") or 0, h.get("num_comments") or 0) >= 50]
    normal = [h for h in hits if h not in high]

    if high:
        lines.append("### 🔥 신호 강도 높음\n")
        for i, hit in enumerate(high, 1):
            oid = hit.get("objectID", "")
            lines.append(f"**{i}. {_format_pain_point(hit, empathy_map.get(oid, 0))}**")
            lines.append("")

    if normal:
        lines.append("### 📌 참고 신호\n")
        for i, hit in enumerate(normal, len(high) + 1):
            oid = hit.get("objectID", "")
            lines.append(f"**{i}. {_format_pain_point(hit, empathy_map.get(oid, 0))}**")
            lines.append("")

    result = "\n".join(lines)
    cache[cache_key] = result
    return result


async def get_hn_thread_signals(story_id: str) -> str:
    """
    특정 HN 스레드의 댓글에서 페인포인트 신호를 추출합니다.

    '+1', 'same problem', 'been waiting for this' 같은 공감 패턴을 찾아
    해당 페인포인트의 실제 수요 강도를 측정합니다.

    Args:
        story_id: HN 스토리 ID (URL의 id= 값)
    """
    cache = get_thread_cache()
    cache_key = make_key("signals", story_id)
    if cache_key in cache:
        return cache[cache_key]

    item = await _fetch_item(story_id)
    title = item.get("title") or "(제목 없음)"
    points = item.get("points") or 0
    children = item.get("children") or []

    # 공감 댓글 수집
    empathy_comments: list[str] = []

    def _collect(comments: list[dict], depth: int = 0) -> None:
        for c in comments:
            text = (c.get("text") or "").lower()
            if any(p in text for p in EMPATHY_PATTERNS):
                raw = (c.get("text") or "").strip()
                snippet = raw[:200].replace("\n", " ")
                author = c.get("author") or "unknown"
                empathy_comments.append(f'  - {author}: "{snippet}"')
            _collect(c.get("children") or [], depth + 1)

    _collect(children)

    lines = [
        f"## 스레드 신호 분석: {title}",
        f"- 포인트: {points}",
        f"- 총 댓글: {len(children)}개",
        f"- 공감 반응 감지: {len(empathy_comments)}건",
        f"- 링크: {_hn_url(story_id)}",
        "",
    ]

    if empathy_comments:
        lines.append("### 공감 댓글 샘플\n")
        lines.extend(empathy_comments[:10])
    else:
        lines.append("공감 패턴 댓글 없음.")

    result = "\n".join(lines)
    cache[cache_key] = result
    return result


async def find_market_gap(domain: str, depth: str = "quick") -> str:
    """
    도메인의 시장 공백을 종합 분석합니다.

    quick: HN Ask 스레드 분석 (빠름)
    deep:  HN + 댓글 공감 분석 포함

    Args:
        domain: 탐색 도메인 (예: "kubernetes", "monitoring", "CI/CD")
        depth: "quick" 또는 "deep" (기본 "quick")
    """
    if depth not in ("quick", "deep"):
        depth = "quick"

    include_comments = depth == "deep"

    pain_result = await search_hn_pain_points(
        domain=domain,
        days=730,
        min_points=5,
        include_comments=include_comments,
        max_results=15,
    )

    header = [
        f"## 시장 공백 분석: \"{domain}\" (depth={depth})",
        "",
    ]

    if depth == "deep":
        header.append("> 댓글 공감 반응 분석 포함\n")

    return "\n".join(header) + pain_result
