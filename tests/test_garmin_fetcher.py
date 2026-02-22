import pytest
from unittest.mock import MagicMock, patch
import os

def test_garmin_fetcher_login_success():
    """Test that GarminFetcher can successfully log in and save session."""
    with patch("garmin_dashboard.fetcher.Garmin") as mock_garmin:
        from garmin_dashboard.fetcher import GarminFetcher
        
        # Mocking the garth object
        mock_instance = mock_garmin.return_value
        mock_instance.garth = MagicMock()
        
        fetcher = GarminFetcher(email="test@example.com", password="password", token_store="test_store")
        
        # Scenario 1: No previous session
        with patch("os.path.exists", return_value=False):
            with patch("os.makedirs"):
                fetcher.login()
                
                # Check login call
                mock_instance.login.assert_called_once()
                # Check session dump
                mock_instance.garth.dump.assert_called_once_with("test_store")
                # Check session load NOT called
                mock_instance.garth.load.assert_not_called()

def test_garmin_fetcher_login_resume():
    """Test that GarminFetcher can resume a session."""
    with patch("garmin_dashboard.fetcher.Garmin") as mock_garmin:
        from garmin_dashboard.fetcher import GarminFetcher
        
        mock_instance = mock_garmin.return_value
        mock_instance.garth = MagicMock()
        
        fetcher = GarminFetcher(email="test@example.com", password="password", token_store="test_store")
        
        # Scenario 2: Previous session exists
        def side_effect(path):
            if "oauth2_token.json" in path:
                return True
            return False

        with patch("os.path.exists", side_effect=side_effect):
            with patch("os.makedirs"):
                fetcher.login()
                
                # Check session load called
                mock_instance.garth.load.assert_called_once_with("test_store")
                # Check login call
                mock_instance.login.assert_called_once()
                # Check session dump
                mock_instance.garth.dump.assert_called_once_with("test_store")

def test_garmin_fetcher_login_generic_failure():
    """Test that a generic failure during login is handled."""
    with patch("garmin_dashboard.fetcher.Garmin") as mock_garmin:
        from garmin_dashboard.fetcher import GarminFetcher
        mock_instance = mock_garmin.return_value
        mock_instance.login.side_effect = Exception("General Error")
        
        fetcher = GarminFetcher(email="test@example.com", password="password")
        with pytest.raises(Exception, match="General Error"):
            fetcher.login()

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
