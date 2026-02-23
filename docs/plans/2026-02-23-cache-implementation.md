# Cache Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace diskcache with an in-memory cachetools TTL cache, cache every GarminFetcher method (user-scoped keys), and expose a POST /sync endpoint that invalidates the current user's cache.

**Architecture:** A new `cache.py` module holds two module-level `TTLCache` instances (24h for stable historical data, 1h for activity lists) plus a thread-safe `cached_fetch()` helper and `invalidate_user()`. `GarminFetcher` gains a `user_email` attribute and each of its methods wraps the Garmin API call with `cached_fetch`. Manual cache logic in `/stats/weekly` is deleted (now handled at the fetcher level). A new `POST /sync` endpoint calls `invalidate_user`.

**Tech Stack:** Python 3.13, FastAPI, cachetools 5.5+, pytest, threading.Lock

---

### Task 1: Swap dependency diskcache → cachetools

**Files:**
- Modify: `pyproject.toml:9`

**Step 1: Edit pyproject.toml**

Replace:
```toml
"diskcache>=5.6.3",
```
With:
```toml
"cachetools>=5.5.0",
```

**Step 2: Sync the environment**

```bash
uv sync
```
Expected: resolves and installs cachetools, removes diskcache.

**Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: replace diskcache with cachetools"
```

---

### Task 2: Create the cache module

**Files:**
- Create: `src/garmin_dashboard/cache.py`
- Create: `tests/test_cache.py`

**Step 1: Write the failing tests**

Create `tests/test_cache.py`:

```python
import threading

import pytest


@pytest.fixture(autouse=True)
def reset_cache():
    """Clear all caches before every test."""
    from garmin_dashboard.cache import clear_all
    clear_all()
    yield
    clear_all()


def test_cached_fetch_calls_fn_on_miss():
    from garmin_dashboard.cache import TTL_LONG, cached_fetch

    calls = []

    def fetch():
        calls.append(1)
        return "data"

    result = cached_fetch("user@example.com", ("method", "arg1"), TTL_LONG, fetch)

    assert result == "data"
    assert len(calls) == 1


def test_cached_fetch_returns_cached_on_hit():
    from garmin_dashboard.cache import TTL_LONG, cached_fetch

    calls = []

    def fetch():
        calls.append(1)
        return "data"

    cached_fetch("user@example.com", ("method", "arg1"), TTL_LONG, fetch)
    result = cached_fetch("user@example.com", ("method", "arg1"), TTL_LONG, fetch)

    assert result == "data"
    assert len(calls) == 1  # only called once


def test_cached_fetch_different_users_are_independent():
    from garmin_dashboard.cache import TTL_LONG, cached_fetch

    calls = []

    def fetch():
        calls.append(1)
        return "data"

    cached_fetch("alice@example.com", ("method", "arg1"), TTL_LONG, fetch)
    cached_fetch("bob@example.com", ("method", "arg1"), TTL_LONG, fetch)

    assert len(calls) == 2  # each user fetches independently


def test_cached_fetch_stores_none_result():
    from garmin_dashboard.cache import TTL_LONG, cached_fetch

    calls = []

    def fetch():
        calls.append(1)
        return None

    result = cached_fetch("user@example.com", ("method", "arg1"), TTL_LONG, fetch)
    result2 = cached_fetch("user@example.com", ("method", "arg1"), TTL_LONG, fetch)

    assert result is None
    assert result2 is None
    assert len(calls) == 1  # None is cached, not re-fetched


def test_invalidate_user_clears_only_that_user():
    from garmin_dashboard.cache import TTL_LONG, cached_fetch, invalidate_user

    cached_fetch("alice@example.com", ("rhr", "2024-01-01"), TTL_LONG, lambda: 55)
    cached_fetch("alice@example.com", ("sleep", "2024-01-01"), TTL_LONG, lambda: {"hours": 7})
    cached_fetch("bob@example.com", ("rhr", "2024-01-01"), TTL_LONG, lambda: 60)

    count = invalidate_user("alice@example.com")

    assert count == 2

    alice_calls = []
    cached_fetch("alice@example.com", ("rhr", "2024-01-01"), TTL_LONG, lambda: alice_calls.append(1) or 55)
    assert len(alice_calls) == 1  # alice re-fetched

    bob_calls = []
    cached_fetch("bob@example.com", ("rhr", "2024-01-01"), TTL_LONG, lambda: bob_calls.append(1) or 60)
    assert len(bob_calls) == 0  # bob's cache untouched


def test_short_ttl_uses_separate_cache():
    from garmin_dashboard.cache import TTL_LONG, TTL_SHORT, _cache_long, _cache_short, cached_fetch

    cached_fetch("user@example.com", ("activities",), TTL_SHORT, lambda: [1, 2, 3])
    cached_fetch("user@example.com", ("rhr", "2024-01-01"), TTL_LONG, lambda: 55)

    assert len(_cache_short) == 1
    assert len(_cache_long) == 1
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_cache.py -v
```
Expected: `ModuleNotFoundError: No module named 'garmin_dashboard.cache'`

**Step 3: Create `src/garmin_dashboard/cache.py`**

```python
import threading
from collections.abc import Callable
from typing import Any

from cachetools import TTLCache

TTL_LONG = 86400   # 24 hours — stable historical data
TTL_SHORT = 3600   # 1 hour  — activity lists

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
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_cache.py -v
```
Expected: all 6 tests PASS.

**Step 5: Commit**

```bash
git add src/garmin_dashboard/cache.py tests/test_cache.py
git commit -m "feat: add in-memory cachetools cache module"
```

---

### Task 3: Update GarminFetcher to use the cache

**Files:**
- Modify: `src/garmin_dashboard/fetcher.py:11`
- Modify: `tests/test_garmin_fetcher.py` (if it exists, else create it)

**Step 1: Write failing test**

Add to `tests/test_garmin_fetcher.py` (create the file if it does not exist):

```python
import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def reset_cache():
    from garmin_dashboard.cache import clear_all
    clear_all()
    yield
    clear_all()


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def fetcher(mock_client):
    from garmin_dashboard.fetcher import GarminFetcher
    return GarminFetcher(mock_client, user_email="test@example.com")


def test_fetcher_caches_rhr(fetcher, mock_client):
    mock_client.get_rhr_day.return_value = {"restingHeartRate": 55}

    result1 = fetcher.get_rhr_day("2024-01-15")
    result2 = fetcher.get_rhr_day("2024-01-15")

    assert result1 == {"restingHeartRate": 55}
    assert result2 == {"restingHeartRate": 55}
    assert mock_client.get_rhr_day.call_count == 1  # only one Garmin API call


def test_fetcher_caches_sleep(fetcher, mock_client):
    mock_client.get_sleep_data.return_value = {"dailySleepDTO": {"sleepTimeSeconds": 25200}}

    fetcher.get_sleep_data("2024-01-15")
    fetcher.get_sleep_data("2024-01-15")

    assert mock_client.get_sleep_data.call_count == 1


def test_fetcher_caches_activity_summary(fetcher, mock_client):
    mock_client.get_activity.return_value = {
        "activityId": 123,
        "activityName": "Morning Run",
        "activityTypeDTO": {"typeKey": "running"},
        "summaryDTO": {},
    }

    fetcher.get_activity_summary(123)
    fetcher.get_activity_summary(123)

    assert mock_client.get_activity.call_count == 1


def test_fetcher_activities_use_short_ttl(fetcher, mock_client):
    """get_activities and get_recent_activities must use the short (1h) cache."""
    from garmin_dashboard.cache import _cache_short

    mock_client.get_activities_by_date.return_value = []
    mock_client.get_activities.return_value = []

    fetcher.get_activities("2024-01-01", "2024-01-07")
    fetcher.get_recent_activities(10)

    # Both should land in the short cache
    assert len(_cache_short) == 2


def test_fetcher_different_dates_cached_separately(fetcher, mock_client):
    mock_client.get_rhr_day.return_value = {"restingHeartRate": 55}

    fetcher.get_rhr_day("2024-01-15")
    fetcher.get_rhr_day("2024-01-16")

    assert mock_client.get_rhr_day.call_count == 2
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_garmin_fetcher.py -v
```
Expected: FAIL — `GarminFetcher.__init__` does not accept `user_email`.

**Step 3: Update `src/garmin_dashboard/fetcher.py`**

Change the `__init__` signature and wrap every public method. Replace the entire file content:

```python
import os

from garminconnect import Garmin
from garth.exc import GarthException
from loguru import logger

from garmin_dashboard.cache import TTL_LONG, TTL_SHORT, cached_fetch


class GarminFetcher:
    """Class to fetch data from Garmin Connect using an authenticated client."""

    def __init__(self, client: Garmin, user_email: str = ""):
        self.client = client
        self.user_email = user_email

    def get_activities(self, start_date: str, end_date: str):
        """Fetch activity summaries between start_date and end_date."""
        return cached_fetch(
            self.user_email,
            ("get_activities", start_date, end_date),
            TTL_SHORT,
            lambda: self._fetch_activities(start_date, end_date),
        )

    def _fetch_activities(self, start_date: str, end_date: str):
        logger.info(f"Fetching activities between {start_date} and {end_date}")
        return self.client.get_activities_by_date(start_date, end_date)

    def get_health_stats(self, date_str: str):
        """Fetch health stats (RHR, Sleep) for a specific date."""
        return cached_fetch(
            self.user_email,
            ("get_health_stats", date_str),
            TTL_LONG,
            lambda: self._fetch_health_stats(date_str),
        )

    def _fetch_health_stats(self, date_str: str):
        logger.info(f"Fetching health stats for {date_str}")
        return self.client.get_stats(date_str)

    def get_sleep_data(self, date_str: str):
        """Fetch sleep data for a specific date."""
        return cached_fetch(
            self.user_email,
            ("get_sleep_data", date_str),
            TTL_LONG,
            lambda: self._fetch_sleep_data(date_str),
        )

    def _fetch_sleep_data(self, date_str: str):
        logger.info(f"Fetching sleep data for {date_str}")
        return self.client.get_sleep_data(date_str)

    def get_rhr_day(self, date_str: str):
        """Fetch resting heart rate for a specific date."""
        return cached_fetch(
            self.user_email,
            ("get_rhr_day", date_str),
            TTL_LONG,
            lambda: self._fetch_rhr_day(date_str),
        )

    def _fetch_rhr_day(self, date_str: str):
        logger.info(f"Fetching RHR for {date_str}")
        return self.client.get_rhr_day(date_str)

    def get_full_name(self) -> str | None:
        """Fetch the authenticated user's full name from Garmin profile."""
        return cached_fetch(
            self.user_email,
            ("get_full_name",),
            TTL_LONG,
            self._fetch_full_name,
        )

    def _fetch_full_name(self) -> str | None:
        logger.info("Fetching user full name from Garmin")
        return self.client.get_full_name()

    def get_recent_activities(self, limit: int = 25) -> list:
        """Fetch most recent activities, newest first."""
        return cached_fetch(
            self.user_email,
            ("get_recent_activities", limit),
            TTL_SHORT,
            lambda: self._fetch_recent_activities(limit),
        )

    def _fetch_recent_activities(self, limit: int) -> list:
        logger.info(f"Fetching {limit} most recent activities")
        return self.client.get_activities(0, limit)

    def get_activity_summary(self, activity_id: int) -> dict:
        """Fetch and normalize a single activity's data."""
        return cached_fetch(
            self.user_email,
            ("get_activity_summary", activity_id),
            TTL_LONG,
            lambda: self._fetch_activity_summary(activity_id),
        )

    def _fetch_activity_summary(self, activity_id: int) -> dict:
        logger.info(f"Fetching activity summary for {activity_id}")
        raw = self.client.get_activity(activity_id)
        s = raw.get("summaryDTO", {})

        def pick(*keys: str, sources: list[dict] | None = None) -> object:
            """Return the first non-None value found across the given key names and sources."""
            srcs = sources if sources is not None else [raw, s]
            for key in keys:
                for src in srcs:
                    val = src.get(key)
                    if val is not None:
                        return val
            return None

        stride_raw = pick("avgStrideLength", "strideLength", sources=[s, raw])
        stride_m = round(float(stride_raw) / 100, 2) if stride_raw else None  # Garmin stores in cm

        normalized = {
            # Identity
            "activityId":   raw.get("activityId"),
            "activityName": raw.get("activityName"),
            "activityType": raw.get("activityTypeDTO", {}).get("typeKey"),
            "startTimeLocal": raw.get("startTimeLocal") or s.get("startTimeLocal"),
            # Core performance (always in summaryDTO)
            "distance":     s.get("distance"),
            "duration":     s.get("duration") or s.get("elapsedDuration"),
            "averageSpeed": s.get("averageSpeed"),
            "averageHR":    s.get("averageHR"),
            "maxHR":        s.get("maxHR"),
            "calories":     s.get("calories"),
            "elevationGain": s.get("elevationGain"),
            "averageRunCadence": s.get("averageRunCadence") or s.get("averageRunningCadenceInStepsPerMinute"),
            "strideLength": stride_m,
            # Training metrics — try top-level first, fall back to summaryDTO
            "aerobicTrainingEffect":   pick("aerobicTrainingEffect", "trainingEffect"),
            "anaerobicTrainingEffect": pick("anaerobicTrainingEffect"),
            "trainingStressScore":     pick("trainingStressScore"),
            "recoveryTime":            pick("recoveryTime"),  # hours
            "vO2MaxValue":             pick("vO2MaxValue", "vo2MaxValue"),
        }

        missing = [k for k, v in normalized.items() if v is None and k not in ("strideLength",)]
        if missing:
            logger.debug(f"Activity {activity_id} — unmapped fields: {missing}")
            logger.debug(f"  top-level keys: {list(raw.keys())}")
            logger.debug(f"  summaryDTO keys: {list(s.keys())}")

        return normalized

    def get_activity_hr_zones(self, activity_id: int) -> list:
        """Fetch heart rate zone breakdown for an activity."""
        return cached_fetch(
            self.user_email,
            ("get_activity_hr_zones", activity_id),
            TTL_LONG,
            lambda: self._fetch_activity_hr_zones(activity_id),
        )

    def _fetch_activity_hr_zones(self, activity_id: int) -> list:
        logger.info(f"Fetching HR zones for activity {activity_id}")
        return self.client.get_activity_hr_in_timezones(activity_id)

    def get_activity_splits_data(self, activity_id: int) -> dict:
        """Fetch lap/split data for an activity."""
        return cached_fetch(
            self.user_email,
            ("get_activity_splits_data", activity_id),
            TTL_LONG,
            lambda: self._fetch_activity_splits_data(activity_id),
        )

    def _fetch_activity_splits_data(self, activity_id: int) -> dict:
        logger.info(f"Fetching splits for activity {activity_id}")
        return self.client.get_activity_splits(activity_id)


def init_garmin(email: str = "", password: str = "", token_store: str = "~/.garminconnect") -> Garmin:
    """Initialize Garmin API following the example flow.

    1. Tries login with stored tokens (no credentials needed).
    2. If fails, tries login with credentials and return_on_mfa=True.
    """
    token_store_path = os.path.expanduser(token_store)

    # 1. Try to login with stored tokens first (exactly as in example)
    try:
        logger.info(f"Attempting login using stored tokens in {token_store_path}")
        garmin = Garmin()
        garmin.login(token_store_path)
        logger.info("Successfully logged in using stored tokens")
        return garmin
    except Exception as e:
        logger.info(f"Stored token login failed or not available: {e}. Falling back to credentials.")

    if not email or not password:
        logger.error("Credentials missing and token login failed")
        msg = "Authentication required: Missing EMAIL/PASSWORD or valid tokens."
        raise ValueError(msg)

    try:
        logger.info(f"Attempting login for {email} with credentials")
        garmin = Garmin(email=email, password=password)
        garmin.login()
        garmin.garth.dump(str(token_store_path))
        logger.info("Successfully logged in with credentials and saved tokens")
        return garmin
    except GarthException:
        logger.exception("Garth authentication error")
        raise
    except Exception:
        logger.exception("Unexpected error during Garmin login")
        raise
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_garmin_fetcher.py -v
```
Expected: all 5 new tests PASS.

**Step 5: Commit**

```bash
git add src/garmin_dashboard/fetcher.py tests/test_garmin_fetcher.py
git commit -m "feat: wrap all GarminFetcher methods with user-scoped cache"
```

---

### Task 4: Update main.py — remove diskcache, add POST /sync

**Files:**
- Modify: `src/garmin_dashboard/main.py`
- Modify: `tests/test_api.py`

**Step 1: Write failing test for POST /sync**

Add to `tests/test_api.py`:

```python
def test_sync_clears_cache(client):
    """POST /sync should return cleared: true and invalidate user cache."""
    from unittest.mock import patch

    with patch("garmin_dashboard.cache.invalidate_user", return_value=5) as mock_invalidate:
        response = client.post("/sync")

    assert response.status_code == 200
    assert response.json() == {"cleared": True}
    mock_invalidate.assert_called_once_with("test@example.com")
```

**Step 2: Run the test to verify it fails**

```bash
pytest tests/test_api.py::test_sync_clears_cache -v
```
Expected: FAIL — 404 Not Found (endpoint does not exist yet).

**Step 3: Update `src/garmin_dashboard/main.py`**

Apply these changes:

**3a.** Replace the import block at the top — remove `diskcache` and `Path`, add cache import:

```python
# Remove these lines:
from pathlib import Path
from diskcache import Cache

# Add this import (alongside the other garmin_dashboard imports):
from garmin_dashboard.cache import invalidate_user
```

**3b.** Remove the cache setup block (lines 15–17):

```python
# DELETE these lines:
# Persistent cache for Garmin API results
CACHE_DIR = Path.home() / ".garmin_cache"
cache = Cache(str(CACHE_DIR))
```

**3c.** In `get_fetcher`, pass `user_email` to `GarminFetcher`:

```python
# Change:
return GarminFetcher(result)
# To:
return GarminFetcher(result, user_email=settings.email)
```

**3d.** Add `POST /sync` endpoint (after the `get_profile` endpoint is fine):

```python
@app.post("/sync")
async def sync_garmin(
    settings: Settings = Depends(get_settings),
):
    """Invalidate all cached Garmin data for the current user."""
    count = invalidate_user(settings.email)
    logger.info(f"Cache invalidated for {settings.email}: {count} entries cleared")
    return {"cleared": True}
```

**3e.** In `get_weekly_stats`, replace the manual cache blocks with direct fetcher calls.

Replace the **RHR block** (lines 244–254):

```python
# DELETE:
rhr_key = f"rhr_{day_str}"
rhr = cache.get(rhr_key)
if rhr is None:
    try:
        rhr_data = fetcher.get_rhr_day(day_str)
        rhr = rhr_data.get("restingHeartRate") if rhr_data else 0
        cache.set(rhr_key, rhr, expire=86400)
    except Exception:
        logger.warning(f"Could not fetch RHR for {day_str}")
        rhr = 0

# REPLACE WITH:
try:
    rhr_data = fetcher.get_rhr_day(day_str)
    rhr = rhr_data.get("restingHeartRate") if rhr_data else 0
except Exception:
    logger.warning(f"Could not fetch RHR for {day_str}")
    rhr = 0
```

Replace the **sleep block** (lines 256–270):

```python
# DELETE:
sleep_key = f"sleep_{day_str}"
sleep_data = cache.get(sleep_key)
if sleep_data is None:
    sleep_data = {"score": 0, "hours": 0}
    try:
        fetched_sleep = fetcher.get_sleep_data(day_str)
        if fetched_sleep:
            sleep_data = {
                "score": fetched_sleep.get("sleepScores", {}).get("overallScore") or 0,
                "hours": round(fetched_sleep.get("dailySleepDTO", {}).get("sleepTimeSeconds", 0) / 3600, 1)
            }
            cache.set(sleep_key, sleep_data, expire=86400)
    except Exception:
        logger.warning(f"Could not fetch Sleep for {day_str}")

# REPLACE WITH:
sleep_data = {"score": 0, "hours": 0}
try:
    fetched_sleep = fetcher.get_sleep_data(day_str)
    if fetched_sleep:
        sleep_data = {
            "score": fetched_sleep.get("sleepScores", {}).get("overallScore") or 0,
            "hours": round(fetched_sleep.get("dailySleepDTO", {}).get("sleepTimeSeconds", 0) / 3600, 1),
        }
except Exception:
    logger.warning(f"Could not fetch Sleep for {day_str}")
```

Replace the **HR zones block** (lines 272–287):

```python
# DELETE:
zones_key = f"zones_{act_id}"
act_zones = cache.get(zones_key)
if act_zones is None:
    try:
        act_zones = fetcher.get_activity_hr_zones(act_id)
        cache.set(zones_key, act_zones, expire=604800)
    except Exception:
        logger.warning(f"Could not fetch zones for activity {act_id}")
        act_zones = []

# REPLACE WITH:
try:
    act_zones = fetcher.get_activity_hr_zones(act_id)
except Exception:
    logger.warning(f"Could not fetch zones for activity {act_id}")
    act_zones = []
```

**Step 4: Run all tests**

```bash
pytest -v
```
Expected: all tests PASS. No references to diskcache remain.

**Step 5: Verify no diskcache references remain**

```bash
grep -r "diskcache\|Cache(" src/ tests/
```
Expected: no output.

**Step 6: Commit**

```bash
git add src/garmin_dashboard/main.py tests/test_api.py
git commit -m "feat: remove diskcache, add POST /sync endpoint"
```

---

### Task 5: Final check

**Step 1: Run full test suite with coverage**

```bash
pytest --cov=garmin_dashboard --cov-report=term-missing -v
```
Expected: all tests pass.

**Step 2: Run linter**

```bash
ruff check src/ tests/
```
Expected: no errors. Fix any that appear with `ruff check --fix src/ tests/`.

**Step 3: Commit any lint fixes, then tag the work**

```bash
git add -p
git commit -m "chore: fix lint issues after cache refactor"
```
