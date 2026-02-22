import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    from main import app
    return TestClient(app)

def test_get_activities_endpoint(client):
    """Test the /activities endpoint."""
    with patch("garmin_dashboard.fetcher.GarminFetcher.get_activities") as mock_get_activities:
        mock_get_activities.return_value = [
            {"activityId": 1, "activityName": "Run", "startTimeLocal": "2026-01-01 10:00:00"}
        ]
        
        # We need to mock login too
        with patch("garmin_dashboard.fetcher.GarminFetcher.login") as mock_login:
            response = client.get("/activities?start_date=2026-01-01&end_date=2026-01-02")
            
            assert response.status_code == 200
            assert len(response.json()) == 1
            assert response.json()[0]["activityName"] == "Run"

def test_get_health_stats_endpoint(client):
    """Test the /health-stats endpoint."""
    with patch("garmin_dashboard.fetcher.GarminFetcher.get_health_stats") as mock_get_health_stats:
        mock_get_health_stats.return_value = {
            "calendarDate": "2026-01-01",
            "restingHeartRate": 55,
            "sleepTime": 28800
        }
        
        with patch("garmin_dashboard.fetcher.GarminFetcher.login") as mock_login:
            response = client.get("/health-stats?date=2026-01-01")
            
            assert response.status_code == 200
            assert response.json()["restingHeartRate"] == 55

def test_get_goal_status_endpoint(client):
    """Test the /goal-status endpoint."""
    # Assuming 104 runs/year is the goal.
    # If it's Feb 22, it's about 7.5 weeks. Goal is 15 runs.
    # If we have 10 runs, we're at 66%
    with patch("garmin_dashboard.fetcher.GarminFetcher.get_activities") as mock_get_activities:
        # Mocking 10 runs in January/February
        mock_get_activities.return_value = [{"activityType": {"typeKey": "running"}}] * 10
        
        with patch("garmin_dashboard.fetcher.GarminFetcher.login") as mock_login:
            response = client.get("/goal-status?year=2026")
            
            assert response.status_code == 200
            data = response.json()
            assert data["goal"] == 104
            assert data["actual"] == 10
            assert "progress_percent" in data
