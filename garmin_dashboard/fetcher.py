import garth
from loguru import logger

class GarminFetcher:
    """Class to fetch data from Garmin Connect using garth."""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.client = garth.client

    def login(self):
        """Log in to Garmin Connect."""
        logger.info(f"Logging in to Garmin Connect for {self.email}")
        self.client.login(self.email, self.password)

    def get_activities(self, start_date: str, end_date: str):
        """Fetch activity summaries between start_date and end_date."""
        logger.info(f"Fetching activities between {start_date} and {end_date}")
        # Garmin API endpoint for activity summaries
        url = "/activitylist-service/activities/search/activities"
        params = {
            "startDate": start_date,
            "endDate": end_date
        }
        response = self.client.get("connectapi", url, params=params)
        return response.json()

    def get_health_stats(self, date: str):
        """Fetch health stats (RHR, Sleep) for a specific date."""
        logger.info(f"Fetching health stats for {date}")
        # Using connectapi for health summary
        url = f"/usersummary-service/usersummary/daily/{date}"
        response = self.client.get("connectapi", url)
        return response.json()
