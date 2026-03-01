import threading
from collections.abc import Callable
from typing import Any

from cachetools import TTLCache

TTL_LONG = 86400  # 24 hours — stable historical data
TTL_SHORT = 3600  # 1 hour  — activity lists

_cache_long: TTLCache = TTLCache(maxsize=4500, ttl=TTL_LONG)
_cache_short: TTLCache = TTLCache(maxsize=500, ttl=TTL_SHORT)
_lock = threading.Lock()

_UNSET = object()  # sentinel to distinguish "not cached" from "cached None"


def cached_fetch(user: str, key: tuple, ttl: int, fetch_fn: Callable[[], Any]) -> Any:
    """Return the cached value for (user, key), or call fetch_fn and cache the result.

    Uses TTL_SHORT cache when ttl == TTL_SHORT, otherwise TTL_LONG cache.
    Thread-safe. Caches None results (Garmin often returns None for missing days).
    """
    cache = _cache_short if ttl == TTL_SHORT else _cache_long
    cache_key = (user, *key)

    with _lock:
        value = cache.get(cache_key, _UNSET)
        if value is not _UNSET:
            return value

    result = fetch_fn()

    with _lock:
        cache[cache_key] = result

    return result


def invalidate_user(email: str) -> int:
    """Delete all cache entries for the given user email.

    Returns the number of entries deleted.
    """
    deleted = 0
    with _lock:
        for cache in (_cache_long, _cache_short):
            keys = [k for k in list(cache.keys()) if k[0] == email]
            for k in keys:
                del cache[k]
                deleted += 1
    return deleted


def clear_all() -> None:
    """Clear every entry across all caches (all users). Used in tests."""
    with _lock:
        _cache_long.clear()
        _cache_short.clear()
