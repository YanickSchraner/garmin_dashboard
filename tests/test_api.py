import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_env():
    with patch.dict(os.environ, {"EMAIL": "test@example.com", "PASSWORD": "password"}):
        yield


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

        with patch("garmin_dashboard.fetcher.GarminFetcher.login") as mock_login:
            mock_login.return_value = True
            response = client.get("/activities?start_date=2026-01-01&end_date=2026-01-02")

            assert response.status_code == 200
            assert len(response.json()) == 1
            assert response.json()[0]["activityName"] == "Run"


def test_get_health_stats_endpoint(client):
    """Test the /health-stats endpoint."""
    with patch("garmin_dashboard.fetcher.GarminFetcher.get_health_stats") as mock_get_health_stats:
        mock_get_health_stats.return_value = {"calendarDate": "2026-01-01", "restingHeartRate": 55, "sleepTime": 28800}

        with patch("garmin_dashboard.fetcher.GarminFetcher.login") as mock_login:
            mock_login.return_value = True
            response = client.get("/health-stats?date=2026-01-01")

            assert response.status_code == 200
            assert response.json()["restingHeartRate"] == 55


def test_get_goal_status_endpoint(client):
    """Test the /goal-status endpoint."""
    with patch("garmin_dashboard.fetcher.GarminFetcher.get_activities") as mock_get_activities:
        # Mocking 10 runs in January/February
        mock_get_activities.return_value = [{"activityType": {"typeKey": "running"}}] * 10

        with patch("garmin_dashboard.fetcher.GarminFetcher.login") as mock_login:
            mock_login.return_value = True
            response = client.get("/goal-status?year=2026")

            assert response.status_code == 200
            data = response.json()
            assert data["goal"] == 104
            assert data["actual"] == 10
            assert "progress_percent" in data


def test_login_failure_401(client):
    """Test that login failure returns 401."""
    with patch("garmin_dashboard.fetcher.GarminFetcher.login") as mock_login:
        mock_login.side_effect = Exception("Garmin authentication failed: Unexpected title")
        response = client.get("/activities?start_date=2026-01-01&end_date=2026-01-02")
        assert response.status_code == 401
        assert "Garmin Authentication Error" in response.json()["detail"]


def test_login_mfa_403(client):
    """Test that MFA requirement returns 403."""
    with patch("garmin_dashboard.fetcher.GarminFetcher.login") as mock_login:
        mock_login.return_value = "needs_mfa"
        response = client.get("/activities?start_date=2026-01-01&end_date=2026-01-02")
        assert response.status_code == 403
        assert "MFA Required" in response.json()["detail"]
