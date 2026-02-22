import pytest
from unittest.mock import MagicMock, patch

# We'll assume the implementation will be in garmin_dashboard.fetcher
# But for now, we define the tests based on the desired interface.

def test_garmin_fetcher_login_success():
    """Test that GarminFetcher can successfully log in."""
    with patch("garth.client.login") as mock_login:
        from garmin_dashboard.fetcher import GarminFetcher
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        fetcher.login()
        
        mock_login.assert_called_once_with("test@example.com", "password")

def test_garmin_fetcher_get_activities_summary():
    """Test that GarminFetcher can retrieve activity summaries."""
    with patch("garth.client.get") as mock_get:
        # Mocking the response from Garmin Connect
        mock_get.return_value.json.return_value = [
            {"activityId": 1, "activityName": "Run", "startTimeLocal": "2026-01-01 10:00:00"}
        ]
        
        from garmin_dashboard.fetcher import GarminFetcher
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        activities = fetcher.get_activities(start_date="2026-01-01", end_date="2026-01-02")
        
        assert len(activities) == 1
        assert activities[0]["activityName"] == "Run"

def test_garmin_fetcher_get_health_stats():
    """Test that GarminFetcher can retrieve health stats like RHR and Sleep."""
    with patch("garth.client.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "calendarDate": "2026-01-01",
            "restingHeartRate": 55,
            "sleepTime": 28800  # 8 hours in seconds
        }
        
        from garmin_dashboard.fetcher import GarminFetcher
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        stats = fetcher.get_health_stats(date="2026-01-01")
        
        assert stats["restingHeartRate"] == 55
        assert stats["sleepTime"] == 28800
