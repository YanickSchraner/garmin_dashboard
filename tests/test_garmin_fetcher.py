from unittest.mock import MagicMock

import pytest


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
