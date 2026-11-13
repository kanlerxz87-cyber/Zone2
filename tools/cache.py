"""Tiny content cache + politeness helpers used by the collectors.

Keeps the pipeline cheap and repeatable: identical requests hit disk cache, expiring records are re-fetched,
and a token bucket keeps us inside the operator's configured request budget instead of discovering a limit
at runtime.  No cache entry is ever used to claim a *current* price or availability (R-04): the freshness
class travels with the record and the renderer checks it.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable

CACHE_ROOT = Path(__file__).resolve().parents[1] / ".cache" / "kv"

FRESHNESS_S = {
    "identity": 60 * 60 * 24 * 30,  # ASIN -> title/brand/category: changes rarely
    "offer": 60 * 60 * 6,  # price/availability: re-check often; never display as current when stale
    "reference": 60 * 60 * 24 * 3,  # policy/rate pages: re-read on a schedule, flagged as of <date>
}


@dataclass
class Entry:
    value: Any
    stored_utc: float
    class_: str
    hit: bool = False

    @property
    def age_s(self) -> float:
        return time.time() - self.stored_utc

    def stale(self) -> bool:
        return self.age_s > FRESHNESS_S.get(self.class_, FRESHNESS_S["reference"])


class Cache:
    def __init__(self, root: Path = CACHE_ROOT):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    @staticmethod
    def key(*parts: Any) -> str:
        return sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:40]

    def path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str, *, allow_stale: bool = False) -> Entry | None:
        p = self.path(key)
        if not p.exists():
            return None
        doc = json.loads(p.read_text(encoding="utf-8"))
        entry = Entry(doc["value"], doc["stored_utc"], doc["class_"], hit=True)
        if entry.stale() and not allow_stale:
            return None
        return entry

    def put(self, key: str, value: Any, *, class_: str = "reference") -> None:
        with self._lock:
            self.path(key).write_text(
                json.dumps({"key": key, "class_": class_, "stored_utc": time.time(), "value": value}, indent=2, sort_keys=True),
                encoding="utf-8",
            )

    def memo(self, class_: str, *key_parts: Any):
        def deco(fn: Callable[..., Any]):
            def wrapper(*a, **kw):
                key = self.key(fn.__name__, *key_parts, *a, sorted(kw.items()))
                found = self.get(key)
                if found is not None:
                    return found.value
                value = fn(*a, **kw)
                self.put(key, value, class_=class_)
                return value

            return wrapper

        return deco


class TokenBucket:
    """Request pacing.  Limits are the operator's own budget, not an invented API number."""

    def __init__(self, rate_per_min: float, burst: int = 5):
        self.rate = max(1.0, rate_per_min) / 60.0
        self.capacity = max(1, int(burst))
        self.tokens = float(self.capacity)
        self.updated = time.time()
        self._lock = threading.Lock()

    def acquire(self, block: bool = True) -> bool:
        deadline = time.time() + 30
        while True:
            with self._lock:
                now = time.time()
                self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
                self.updated = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
            if not block:
                return False
            if time.time() > deadline:
                return False
            time.sleep(0.2)


CACHE = Cache()
