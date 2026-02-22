from garminconnect import Garmin
from loguru import logger
from datetime import date

class GarminFetcher:
    """Class to fetch data from Garmin Connect using garminconnect."""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.client = Garmin(email, password)

    def login(self):
        """Log in to Garmin Connect."""
        logger.info(f"Logging in to Garmin Connect for {self.email}")
        self.client.login()

    def get_activities(self, start_date: str, end_date: str):
        """Fetch activity summaries between start_date and end_date."""
        logger.info(f"Fetching activities between {start_date} and {end_date}")
        # get_activities_by_date expects datetime objects or date objects?
        # Actually it takes start_date, end_date.
        return self.client.get_activities_by_date(start_date, end_date)

    def get_health_stats(self, date_str: str):
        """Fetch health stats (RHR, Sleep) for a specific date."""
        logger.info(f"Fetching health stats for {date_str}")
        # get_stats returns daily summary
        return self.client.get_stats(date_str)
