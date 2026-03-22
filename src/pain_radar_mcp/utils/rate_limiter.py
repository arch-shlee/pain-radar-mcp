import asyncio
import time


class TokenBucket:
    """간단한 token bucket rate limiter."""

    def __init__(self, rate: float, capacity: float) -> None:
        self._rate = rate          # tokens/second
        self._capacity = capacity  # max tokens
        self._tokens = capacity
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
            self._last = now

            if self._tokens < 1:
                wait = (1 - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._tokens = 0
            else:
                self._tokens -= 1


# HN Algolia: 10,000 req/h → ~2.77 req/s. 안전하게 2 req/s로 제한
hn_limiter = TokenBucket(rate=2.0, capacity=10.0)
