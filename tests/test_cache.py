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
