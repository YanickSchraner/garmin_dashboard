# Cache Redesign — 2026-02-23

## Goal

Prevent Garmin account bans from excessive API requests by caching all fetcher-level results. Cache invalidation is triggered manually via a "sync garmin" UI action.

## Constraints

- Single-user now, up to 2–3 users (local deployment) in the future
- No persistence required across server restarts
- Primary concern: rate-limit protection, not latency

## Decision

Replace `diskcache` with `cachetools` (in-memory TTL cache).

**Rationale:** disk persistence is not needed; `cachetools` is simpler, faster (no disk I/O), and purpose-built for in-memory TTL caching.

---

## Architecture

### New `cache.py` module

Module-level singleton cache — shared across all fetcher instances.

```
src/garmin_dashboard/cache.py
├── _cache_long:  TTLCache(maxsize=4500, ttl=86400)   # 24h
├── _cache_short: TTLCache(maxsize=500,  ttl=3600)    # 1h
├── _lock:        threading.Lock
│
├── cached_fetch(user, key, ttl, fetch_fn) → value
│     Routes to _cache_long or _cache_short based on ttl.
│     Thread-safe via _lock.
│
└── invalidate_user(email: str) → None
      Deletes all keys where key[0] == email from both caches.
```

### Cache keys

Tuple-based: `(user_email, method_name, *args)`

Examples:
- `("alice@gmail.com", "get_rhr_day", "2024-01-15")`
- `("alice@gmail.com", "get_activity_hr_zones", "12345678")`
- `("alice@gmail.com", "get_recent_activities", 25)`

User-scoped so that invalidating one user's cache does not affect another.

### TTL tiers

| TTL   | Methods                                                                 | Reason                          |
|-------|-------------------------------------------------------------------------|---------------------------------|
| 24h   | `get_rhr_day`, `get_sleep_data`, `get_health_stats`                    | Historical daily data, immutable |
| 24h   | `get_activity_summary`, `get_activity_hr_zones`, `get_activity_splits_data` | Per-activity data, immutable |
| 24h   | `get_full_name`                                                         | Rarely changes                  |
| 1h    | `get_activities`, `get_recent_activities`                              | Changes when new runs are synced |

### Cache placement: `GarminFetcher` method level

Each fetcher method checks the cache before calling the Garmin API. This ensures the same underlying data point is never fetched more than once per TTL period, regardless of which endpoint requests it.

Pattern in each method:
```python
def get_rhr_day(self, date_str: str):
    return cached_fetch(
        self.user_email,
        ("get_rhr_day", date_str),
        ttl=86400,
        fetch_fn=lambda: self._client.get_rhr_day(date_str),
    )
```

`GarminFetcher` gains a `user_email` attribute (sourced from `settings.email`).

### `POST /sync` endpoint

```
POST /sync
→ invalidate_user(settings.email)
← {"cleared": true}
```

Triggered by the "sync garmin" button in the UI. Clears all cached entries for the current user, forcing fresh Garmin API calls on the next request.

---

## Changes Required

| File | Change |
|------|--------|
| `pyproject.toml` | Replace `diskcache>=5.6.3` with `cachetools>=5.5.0` |
| `src/garmin_dashboard/cache.py` | **New file** — cache store, `cached_fetch`, `invalidate_user` |
| `src/garmin_dashboard/fetcher.py` | Add `user_email` attribute; wrap all public methods with `cached_fetch` |
| `src/garmin_dashboard/main.py` | Remove manual cache logic from `/stats/weekly`; remove diskcache setup; add `POST /sync` endpoint |
| `tests/` | Update mocks; add tests for cache hit/miss and invalidation |
