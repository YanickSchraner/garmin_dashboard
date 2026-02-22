from datetime import datetime, timedelta
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

from garmin_dashboard.fetcher import GarminFetcher, init_garmin

app = FastAPI(title="Garmin Custom Dashboard API")

# Configure loguru to write to a file
LOG_FILE = "garmin.log"
logger.add(LOG_FILE, rotation="10 MB", level="INFO")

# Configure CORS for Nuxt 4 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Settings(BaseSettings):
    """Typed, validated application config — reads from env and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    email: str = ""
    password: str = ""
    garmin_token_store: str = "~/.garminconnect"

    # Personalisation — used as fallback when Garmin API returns no name
    display_name: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_fetcher(settings: Settings = Depends(get_settings)):
    """Dependency to get a logged-in GarminFetcher."""
    try:
        result = init_garmin(settings.email, settings.password, settings.garmin_token_store)

        if isinstance(result, tuple) and result[0] == "needs_mfa":
            logger.warning("MFA required for Garmin login")
            raise HTTPException(
                status_code=403, detail="MFA Required. Please run the CLI login first to generate tokens."
            )

        return GarminFetcher(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        if (
            "authentication failed" in str(e).lower()
            or "sso error" in str(e).lower()
            or "authentication required" in str(e).lower()
        ):
            raise HTTPException(status_code=401, detail=f"Garmin Authentication Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error during Garmin Login: {e}")


@app.get("/me")
async def get_profile(
    settings: Settings = Depends(get_settings),
    fetcher: GarminFetcher = Depends(get_fetcher),
):
    """Return the user's display name.

    Resolution order:
    1. Garmin Connect profile full name
    2. DISPLAY_NAME env / .env fallback
    3. Generic 'Athlete' default
    """
    name: str | None = None
    try:
        name = fetcher.get_full_name()
        logger.info(f"Resolved display name from Garmin: {name!r}")
    except Exception as e:
        logger.warning(f"Could not fetch name from Garmin: {e}")

    if not name:
        name = settings.display_name or "Athlete"
        logger.info(f"Using fallback display name: {name!r}")

    return {"display_name": name}


@app.get("/activities/recent")
async def get_recent_activities(
    limit: int = Query(25, ge=1, le=100, description="Number of most recent activities to return"),
    fetcher: GarminFetcher = Depends(get_fetcher),
):
    """Get most recent activities, newest first."""
    try:
        return fetcher.get_recent_activities(limit)
    except Exception as e:
        logger.error(f"Error fetching recent activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/activities/{activity_id}")
async def get_activity_detail(
    activity_id: int,
    fetcher: GarminFetcher = Depends(get_fetcher),
):
    """Get detailed stats for a single activity.

    Aggregates summary, HR zones, and splits into one response.
    Optional sub-calls (hr_zones, splits) fail gracefully — their key will be null.
    """
    try:
        summary = fetcher.get_activity_summary(activity_id)
    except Exception as e:
        logger.error(f"Error fetching activity {activity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    hr_zones = None
    try:
        hr_zones = fetcher.get_activity_hr_zones(activity_id)
    except Exception as e:
        logger.warning(f"Could not fetch HR zones for {activity_id}: {e}")

    splits = None
    try:
        splits = fetcher.get_activity_splits_data(activity_id)
    except Exception as e:
        logger.warning(f"Could not fetch splits for {activity_id}: {e}")

    return {"summary": summary, "hr_zones": hr_zones, "splits": splits}


@app.get("/activities")
async def get_activities(
    start_date: str = Query(..., description="ISO 8601 date YYYY-MM-DD"),
    end_date: str = Query(..., description="ISO 8601 date YYYY-MM-DD"),
    fetcher: GarminFetcher = Depends(get_fetcher),
):
    """Get activity summaries for a date range."""
    try:
        return fetcher.get_activities(start_date, end_date)
    except Exception as e:
        logger.error(f"Error fetching activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health-stats")
async def get_health_stats(
    date: str = Query(..., description="ISO 8601 date YYYY-MM-DD"), fetcher: GarminFetcher = Depends(get_fetcher)
):
    """Get health stats for a specific date."""
    try:
        return fetcher.get_health_stats(date)
    except Exception as e:
        logger.error(f"Error fetching health stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/goal-status")
async def get_goal_status(
    year: int = Query(datetime.now().year, description="The year to check"),
    fetcher: GarminFetcher = Depends(get_fetcher),
):
    """Calculate progress toward the 104-run annual goal."""
    try:
        start_date = f"{year}-01-01"
        end_date = datetime.now().strftime("%Y-%m-%d") if year == datetime.now().year else f"{year}-12-31"

        activities = fetcher.get_activities(start_date, end_date)

        # Filter for runs
        runs = [a for a in activities if a.get("activityType", {}).get("typeKey") == "running"]
        actual_runs = len(runs)
        goal_runs = 104

        # Calculate expected runs to date
        total_days = 366 if year % 4 == 0 else 365
        days_passed = (datetime.now() - datetime(year, 1, 1)).days + 1 if year == datetime.now().year else total_days

        expected_runs_to_date = (goal_runs / total_days) * days_passed

        return {
            "year": year,
            "goal": goal_runs,
            "actual": actual_runs,
            "expected_to_date": round(expected_runs_to_date, 1),
            "progress_percent": round((actual_runs / goal_runs) * 100, 1),
            "status": "ahead" if actual_runs >= expected_runs_to_date else "behind",
        }
    except Exception as e:
        logger.error(f"Error calculating goal status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/weekly")
async def get_weekly_stats(
    date: str = Query(None, description="Reference date (YYYY-MM-DD). Defaults to today."),
    fetcher: GarminFetcher = Depends(get_fetcher),
):
    """Get aggregated weekly stats for current and previous week."""
    try:
        ref_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()

        # Find Monday of current week
        days_to_monday = ref_date.weekday()  # Mon=0, Sun=6
        curr_monday = (ref_date - timedelta(days=days_to_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        prev_monday = curr_monday - timedelta(days=7)

        # Ranges
        curr_end = (curr_monday + timedelta(days=6)).strftime("%Y-%m-%d")
        prev_start = prev_monday.strftime("%Y-%m-%d")

        # Fetch activities for both weeks in one call
        all_activities = fetcher.get_activities(prev_start, curr_end)

        weeks = {"current": [], "previous": []}
        for week_name, start_day in [("current", curr_monday), ("previous", prev_monday)]:
            for i in range(7):
                day_date = start_day + timedelta(days=i)
                day_str = day_date.strftime("%Y-%m-%d")

                # Filter activities for this day
                day_activities = [a for a in all_activities if a.get("startTimeLocal", "").startswith(day_str)]

                rhr = None
                try:
                    rhr_data = fetcher.get_rhr_day(day_str)
                    rhr = rhr_data.get("restingHeartRate") if rhr_data else None
                except Exception:
                    logger.warning(f"Could not fetch RHR for {day_str}")

                sleep_score = None
                sleep_hours = None
                try:
                    sleep_data = fetcher.get_sleep_data(day_str)
                    if sleep_data:
                        sleep_score = sleep_data.get("sleepScores", {}).get("overallScore")
                        duration_sec = sleep_data.get("dailySleepDTO", {}).get("sleepTimeSeconds")
                        if duration_sec:
                            sleep_hours = round(duration_sec / 3600, 1)
                except Exception:
                    logger.warning(f"Could not fetch Sleep for {day_str}")

                aerobic_te = max([a.get("aerobicTrainingEffect", 0) for a in day_activities] + [0])
                intensity = None
                if aerobic_te >= 4:
                    intensity = "high"
                elif aerobic_te >= 3:
                    intensity = "medium"
                elif aerobic_te > 0:
                    intensity = "low"

                weeks[week_name].append({
                    "date": day_str,
                    "day_label": day_date.strftime("%a").upper(),
                    "full_day": day_date.strftime("%A"),
                    "distance": sum(a.get("distance", 0) for a in day_activities) / 1000.0,
                    "count": len(day_activities),
                    "rhr": rhr,
                    "sleep_hours": sleep_hours,
                    "sleep_score": sleep_score,
                    "training_intensity": intensity,
                    "aerobic_te": aerobic_te,
                })

        return weeks

    except Exception as e:
        logger.error(f"Error in get_weekly_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
