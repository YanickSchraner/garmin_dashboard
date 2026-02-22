from garminconnect import Garmin
from loguru import logger
import os
from garth.exc import GarthException

class GarminFetcher:
    """Class to fetch data from Garmin Connect using garminconnect with session support."""
    
    def __init__(self, email: str, password: str, token_store: str = "conductor/garmin_tokens"):
        self.email = email
        self.password = password
        self.token_store = os.path.expanduser(token_store)
        self.client = Garmin(self.email, self.password)

    def login(self, prompt_mfa=None):
        """Log in to Garmin Connect or resume session."""
        try:
            # Ensure the token store directory exists
            os.makedirs(self.token_store, exist_ok=True)
            
            # Use is_cn=False for global accounts
            self.client = Garmin(self.email, self.password, is_cn=False, prompt_mfa=prompt_mfa)
            
            # Try to load session
            if os.path.exists(os.path.join(self.token_store, "oauth2_token.json")):
                logger.info(f"Loading session from {self.token_store}")
                self.client.garth.load(self.token_store)
            
            # Login/Resume
            logger.info(f"Attempting login/session resume for {self.email}")
            self.client.login()
            
            # Save session
            self.client.garth.dump(self.token_store)
            logger.info("Successfully logged in to Garmin Connect and saved session")
            
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
