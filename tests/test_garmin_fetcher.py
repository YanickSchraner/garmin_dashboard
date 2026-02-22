import pytest
from unittest.mock import MagicMock, patch
import os

def test_garmin_fetcher_login_success():
    """Test that GarminFetcher can successfully log in."""
    with patch("garmin_dashboard.fetcher.Garmin") as mock_garmin:
        from garmin_dashboard.fetcher import GarminFetcher
        
        mock_instance = mock_garmin.return_value
        fetcher = GarminFetcher(email="test@example.com", password="password", token_store="test_store")
        
        with patch("os.makedirs"):
            result = fetcher.login()
            
            # Check login call with token_store
            mock_instance.login.assert_called_once_with("test_store")
            assert result is True

def test_garmin_fetcher_login_mfa_required():
    """Test that GarminFetcher handles MFA requirement."""
    with patch("garmin_dashboard.fetcher.Garmin") as mock_garmin:
        from garmin_dashboard.fetcher import GarminFetcher
        
        mock_instance = mock_garmin.return_value
        mock_instance.login.return_value = "needs_mfa"
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        
        with patch("os.makedirs"):
            result = fetcher.login()
            assert result == "needs_mfa"

def test_garmin_fetcher_get_activities_summary():
    """Test that GarminFetcher can retrieve activity summaries."""
    with patch("garmin_dashboard.fetcher.Garmin") as mock_garmin:
        from garmin_dashboard.fetcher import GarminFetcher
        
        mock_instance = mock_garmin.return_value
        mock_instance.get_activities_by_date.return_value = [
            {"activityId": 1, "activityName": "Run", "startTimeLocal": "2026-01-01 10:00:00"}
        ]
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        activities = fetcher.get_activities(start_date="2026-01-01", end_date="2026-01-02")
        
        assert len(activities) == 1
        assert activities[0]["activityName"] == "Run"
        mock_instance.get_activities_by_date.assert_called_once_with("2026-01-01", "2026-01-02")

def test_garmin_fetcher_get_health_stats():
    """Test that GarminFetcher can retrieve health stats like RHR and Sleep."""
    with patch("garmin_dashboard.fetcher.Garmin") as mock_garmin:
        from garmin_dashboard.fetcher import GarminFetcher
        
        mock_instance = mock_garmin.return_value
        mock_instance.get_stats.return_value = {
            "calendarDate": "2026-01-01",
            "restingHeartRate": 55,
            "sleepTime": 28800  # 8 hours in seconds
        }
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        stats = fetcher.get_health_stats(date_str="2026-01-01")
        
        assert stats["restingHeartRate"] == 55
        assert stats["sleepTime"] == 28800
        mock_instance.get_stats.assert_called_once_with("2026-01-01")
