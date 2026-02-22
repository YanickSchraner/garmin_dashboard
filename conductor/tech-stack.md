# Tech Stack: Garmin Custom Dashboard

## Core Platform
- **Frontend Framework**: Nuxt 3 (Vue.js)
- **UI Library**: Nuxt UI (TailwindCSS-based, accessible components)
- **Backend Framework**: FastAPI (Python >= 3.14)
- **API Integration**: [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) (Robust Python wrapper for Garmin Connect)
- **Previous Integration (2026-02-22)**: Initially used `garth` (custom), but switched to `python-garminconnect` for improved stability and reduced maintenance overhead.

## Tools & Libraries
- **Asynchronous Task Handler**: `cron`-like scheduling (e.g., `apscheduler` or `celery`)
- **Logging**: `loguru`
- **Testing**: `pytest` (Backend), `vitest` (Frontend)
- **Linting & Formatting**: `ruff` (Python), `eslint`/`prettier` (JS/Vue)

## Infrastructure
- **Dependency Management**: `uv` (Python), `npm` or `pnpm` (JS)
- **Deployment**: Likely Dockerized or hosted on a platform supporting Python/Node.js.
- **State Management**: Pinia (if needed for the frontend).
