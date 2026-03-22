from cachetools import TTLCache
from typing import Any

# search 결과: 1시간
_search_cache: TTLCache = TTLCache(maxsize=256, ttl=3600)

# 단일 스레드 댓글: 30분
_thread_cache: TTLCache = TTLCache(maxsize=512, ttl=1800)


def get_search_cache() -> TTLCache:
    return _search_cache


def get_thread_cache() -> TTLCache:
    return _thread_cache


def make_key(*args: Any) -> str:
    return ":".join(str(a) for a in args)
