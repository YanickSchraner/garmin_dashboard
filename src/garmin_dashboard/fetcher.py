import os

from garminconnect import Garmin
from garth.exc import GarthException
from loguru import logger


class GarminFetcher:
    """Class to fetch data from Garmin Connect using an authenticated client."""

    def __init__(self, client: Garmin):
        self.client = client

    def get_activities(self, start_date: str, end_date: str):
        """Fetch activity summaries between start_date and end_date."""
        logger.info(f"Fetching activities between {start_date} and {end_date}")
        return self.client.get_activities_by_date(start_date, end_date)

    def get_health_stats(self, date_str: str):
        """Fetch health stats (RHR, Sleep) for a specific date."""
        logger.info(f"Fetching health stats for {date_str}")
        return self.client.get_stats(date_str)

    def get_full_name(self) -> str | None:
        """Fetch the authenticated user's full name from Garmin profile."""
        logger.info("Fetching user full name from Garmin")
        return self.client.get_full_name()

    def get_recent_activities(self, limit: int = 25) -> list:
        """Fetch most recent activities, newest first."""
        logger.info(f"Fetching {limit} most recent activities")
        return self.client.get_activities(0, limit)

    def get_activity_summary(self, activity_id: int) -> dict:
        """Fetch a single activity's summary data."""
        logger.info(f"Fetching activity summary for {activity_id}")
        return self.client.get_activity(activity_id)

    def get_activity_hr_zones(self, activity_id: int) -> list:
        """Fetch heart rate zone breakdown for an activity."""
        logger.info(f"Fetching HR zones for activity {activity_id}")
        return self.client.get_activity_hr_in_timezones(activity_id)

    def get_activity_splits_data(self, activity_id: int) -> dict:
        """Fetch lap/split data for an activity."""
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
        raise Exception("Authentication required: Missing EMAIL/PASSWORD or valid tokens.")

    try:
        logger.info(f"Attempting login for {email} with credentials")
        # return_on_mfa=True is recommended for non-interactive handling
        garmin = Garmin(email=email, password=password)
        garmin.login()
        garmin.garth.dump(str(token_store_path))
        logger.info("Successfully logged in with credentials and saved tokens")
        return garmin
    except GarthException as e:
        logger.error(f"Garth authentication error: {e}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during Garmin login: {e}")
        raise e
