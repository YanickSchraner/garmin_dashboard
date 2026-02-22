from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from garmin_dashboard.fetcher import GarminFetcher
from datetime import datetime
import os
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Garmin Custom Dashboard API")

# Configure loguru to write to a file
LOG_FILE = "garmin.log"
logger.add(LOG_FILE, rotation="10 MB", level="INFO")

# Configure CORS for Nuxt 3 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In a real app, use a secure way to handle credentials.
GARMIN_EMAIL = os.getenv("GARMIN_EMAIL", "test@example.com")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD", "password")
# Path where we store the session tokens
GARMIN_TOKEN_STORE = os.getenv("GARMIN_TOKEN_STORE", "conductor/garmin_tokens")

def get_fetcher():
    """Dependency to get a logged-in GarminFetcher with session support."""
    fetcher = GarminFetcher(GARMIN_EMAIL, GARMIN_PASSWORD, token_store=GARMIN_TOKEN_STORE)
    try:
        fetcher.login()
        return fetcher
    except Exception as e:
        logger.error(f"Login failed: {e}")
        # Return 401 if it's an authentication error
        if "authentication failed" in str(e).lower() or "unexpected title" in str(e).lower():
            raise HTTPException(status_code=401, detail=f"Garmin Authentication Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during Garmin Login")

@app.get("/activities")
async def get_activities(
    start_date: str = Query(..., description="ISO 8601 date YYYY-MM-DD"),
    end_date: str = Query(..., description="ISO 8601 date YYYY-MM-DD"),
    fetcher: GarminFetcher = Depends(get_fetcher)
):
    """Get activity summaries for a date range."""
    try:
        return fetcher.get_activities(start_date, end_date)
    except Exception as e:
        logger.error(f"Error fetching activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health-stats")
async def get_health_stats(
    date: str = Query(..., description="ISO 8601 date YYYY-MM-DD"),
    fetcher: GarminFetcher = Depends(get_fetcher)
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
    fetcher: GarminFetcher = Depends(get_fetcher)
):
    """Calculate progress toward the 104-run annual goal."""
    try:
        start_date = f"{year}-01-01"
        if year == datetime.now().year:
            end_date = datetime.now().strftime("%Y-%m-%d")
        else:
            end_date = f"{year}-12-31"
        
        activities = fetcher.get_activities(start_date, end_date)
        
        # Filter for runs
        runs = [a for a in activities if a.get("activityType", {}).get("typeKey") == "running"]
        actual_runs = len(runs)
        goal_runs = 104
        
        # Calculate expected runs to date
        total_days = 366 if year % 4 == 0 else 365
        
        if year == datetime.now().year:
            days_passed = (datetime.now() - datetime(year, 1, 1)).days + 1
        else:
            days_passed = total_days
            
        expected_runs_to_date = (goal_runs / total_days) * days_passed
        
        return {
            "year": year,
            "goal": goal_runs,
            "actual": actual_runs,
            "expected_to_date": round(expected_runs_to_date, 1),
            "progress_percent": round((actual_runs / goal_runs) * 100, 1),
            "status": "ahead" if actual_runs >= expected_runs_to_date else "behind"
        }
    except Exception as e:
        logger.error(f"Error calculating goal status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
