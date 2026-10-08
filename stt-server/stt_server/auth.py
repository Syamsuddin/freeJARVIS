"""Bearer token + rate limit sederhana (docs/21)."""

from __future__ import annotations

import hmac
import time
from collections import deque


def bearer_matches(header: str | None, expected: str) -> bool:
    if not header or not header.startswith("Bearer "):
        return False
    return hmac.compare_digest(header.removeprefix("Bearer ").encode(), expected.encode())


class RateLimiter:
    """Jendela geser per proses; satu token = satu pengguna (docs/05)."""

    def __init__(self, limit: int, window_s: float = 60.0) -> None:
        self.limit = limit
        self.window_s = window_s
        self._hits: deque[float] = deque()

    def allow(self, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        while self._hits and current - self._hits[0] >= self.window_s:
            self._hits.popleft()
        if len(self._hits) >= self.limit:
            return False
        self._hits.append(current)
        return True
