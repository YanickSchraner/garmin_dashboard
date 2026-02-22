from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from garmin_dashboard.fetcher import GarminFetcher
from datetime import datetime, date
import os
from typing import List, Optional
from loguru import logger

app = FastAPI(title="Garmin Custom Dashboard API")

# Configure CORS for Nuxt 3 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In a real app, you would use a secure way to handle credentials.
# Here we'll assume they are provided via environment variables.
GARMIN_EMAIL = os.getenv("GARMIN_EMAIL", "test@example.com")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD", "password")

def get_fetcher():
    """Dependency to get a logged-in GarminFetcher."""
    fetcher = GarminFetcher(GARMIN_EMAIL, GARMIN_PASSWORD)
    fetcher.login()
    return fetcher

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
        raise HTTPException(status_code=500, detail="Failed to fetch activities")

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
        raise HTTPException(status_code=500, detail="Failed to fetch health stats")

@app.get("/goal-status")
async def get_goal_status(
    year: int = Query(datetime.now().year, description="The year to check"),
    fetcher: GarminFetcher = Depends(get_fetcher)
):
    """Calculate progress toward the 104-run annual goal."""
    try:
        start_date = f"{year}-01-01"
        # If it's the current year, check until today.
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
        total_days = 365
        if year % 4 == 0: total_days = 366
        
        # How many days have passed in the year
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
        raise HTTPException(status_code=500, detail="Failed to calculate goal status")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
