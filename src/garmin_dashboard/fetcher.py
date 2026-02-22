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
        """Fetch and normalize a single activity's data.

        get_activity() returns a nested structure where performance metrics live in
        summaryDTO and some training metrics (TE, TSS, recovery, VO2) can be at the
        top level or inside summaryDTO depending on activity type / Garmin firmware.
        We normalize everything into a single flat dict the frontend can rely on.
        """
        logger.info(f"Fetching activity summary for {activity_id}")
        raw = self.client.get_activity(activity_id)
        s = raw.get("summaryDTO", {})

        def pick(*keys: str, sources: list[dict] | None = None) -> object:
            """Return the first non-None value found across the given key names and sources."""
            srcs = sources if sources is not None else [raw, s]
            for key in keys:
                for src in srcs:
                    val = src.get(key)
                    if val is not None:
                        return val
            return None

        stride_raw = pick("avgStrideLength", "strideLength", sources=[s, raw])
        stride_m = round(float(stride_raw) / 100, 2) if stride_raw else None  # Garmin stores in cm

        normalized = {
            # Identity
            "activityId":   raw.get("activityId"),
            "activityName": raw.get("activityName"),
            "activityType": raw.get("activityTypeDTO", {}).get("typeKey"),
            "startTimeLocal": raw.get("startTimeLocal") or s.get("startTimeLocal"),
            # Core performance (always in summaryDTO)
            "distance":     s.get("distance"),
            "duration":     s.get("duration") or s.get("elapsedDuration"),
            "averageSpeed": s.get("averageSpeed"),
            "averageHR":    s.get("averageHR"),
            "maxHR":        s.get("maxHR"),
            "calories":     s.get("calories"),
            "elevationGain": s.get("elevationGain"),
            "averageRunCadence": s.get("averageRunCadence") or s.get("averageRunningCadenceInStepsPerMinute"),
            "strideLength": stride_m,
            # Training metrics — try top-level first, fall back to summaryDTO
            # aerobicTrainingEffect can also appear as "trainingEffect" in summaryDTO
            "aerobicTrainingEffect":   pick("aerobicTrainingEffect", "trainingEffect"),
            "anaerobicTrainingEffect": pick("anaerobicTrainingEffect"),
            "trainingStressScore":     pick("trainingStressScore"),
            "recoveryTime":            pick("recoveryTime"),  # hours
            "vO2MaxValue":             pick("vO2MaxValue", "vo2MaxValue"),
        }

        # Log any keys we couldn't map so we can see what Garmin actually returns
        missing = [k for k, v in normalized.items() if v is None and k not in ("strideLength",)]
        if missing:
            top_keys = list(raw.keys())
            sum_keys = list(s.keys())
            logger.debug(f"Activity {activity_id} — unmapped fields: {missing}")
            logger.debug(f"  top-level keys: {top_keys}")
            logger.debug(f"  summaryDTO keys: {sum_keys}")

        return normalized

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
