from garminconnect import Garmin
from loguru import logger
import os
from garth.exc import GarthException

class GarminFetcher:
    """Class to fetch data from Garmin Connect using garminconnect with session support."""
    
    def __init__(self, email: str, password: str, token_store: str = "~/.garminconnect"):
        self.email = email
        self.password = password
        self.token_store = os.path.expanduser(token_store)
        self.client = Garmin(self.email, self.password)

    def login(self):
        """Log in to Garmin Connect or resume session."""
        try:
            # Ensure the token store directory exists
            os.makedirs(self.token_store, exist_ok=True)
            
            logger.info(f"Attempting login/session resume for {self.email} using {self.token_store}")
            
            # The login method handles loading and saving tokens if tokenstore is provided
            # It returns True if logged in, or "needs_mfa" if MFA is required
            result = self.client.login(self.token_store)
            
            if result == "needs_mfa":
                logger.warning("MFA required for Garmin login")
                return "needs_mfa"
            
            logger.info("Successfully logged in to Garmin Connect")
            return True
            
        except GarthException as e:
            msg = str(e)
            if "Unexpected title" in msg:
                logger.error(f"SSO Error (likely MFA or Account Lock): {msg}")
                raise Exception(f"Garmin SSO Error: {msg}. Please check if MFA is enabled or account is locked.")
            logger.error(f"Garth authentication error: {e}")
            raise Exception(f"Garmin authentication failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during Garmin login: {e}")
            raise e

    def get_activities(self, start_date: str, end_date: str):
        """Fetch activity summaries between start_date and end_date."""
        logger.info(f"Fetching activities between {start_date} and {end_date}")
        return self.client.get_activities_by_date(start_date, end_date)

    def get_health_stats(self, date_str: str):
        """Fetch health stats (RHR, Sleep) for a specific date."""
        logger.info(f"Fetching health stats for {date_str}")
        return self.client.get_stats(date_str)
