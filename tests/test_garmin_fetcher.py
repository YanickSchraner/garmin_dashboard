import pytest
from unittest.mock import MagicMock, patch

def test_garmin_fetcher_login_success():
    """Test that GarminFetcher can successfully log in."""
    with patch("garminconnect.Garmin.login") as mock_login:
        from garmin_dashboard.fetcher import GarminFetcher
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        fetcher.login()
        
        mock_login.assert_called_once()

def test_garmin_fetcher_get_activities_summary():
    """Test that GarminFetcher can retrieve activity summaries."""
    with patch("garminconnect.Garmin.get_activities_by_date") as mock_get:
        # Mocking the response from Garmin Connect
        mock_get.return_value = [
            {"activityId": 1, "activityName": "Run", "startTimeLocal": "2026-01-01 10:00:00"}
        ]
        
        from garmin_dashboard.fetcher import GarminFetcher
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        activities = fetcher.get_activities(start_date="2026-01-01", end_date="2026-01-02")
        
        assert len(activities) == 1
        assert activities[0]["activityName"] == "Run"
        mock_get.assert_called_once_with("2026-01-01", "2026-01-02")

def test_garmin_fetcher_get_health_stats():
    """Test that GarminFetcher can retrieve health stats like RHR and Sleep."""
    with patch("garminconnect.Garmin.get_stats") as mock_get:
        mock_get.return_value = {
            "calendarDate": "2026-01-01",
            "restingHeartRate": 55,
            "sleepTime": 28800  # 8 hours in seconds
        }
        
        from garmin_dashboard.fetcher import GarminFetcher
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        stats = fetcher.get_health_stats(date_str="2026-01-01")
        
        assert stats["restingHeartRate"] == 55
        assert stats["sleepTime"] == 28800
        mock_get.assert_called_once_with("2026-01-01")
