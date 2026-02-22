# Specification: Core Garmin Data Fetcher and Dashboard Shell

## Overview
This track focuses on the foundational components of the Garmin Custom Dashboard: a backend service to authenticate and fetch data from Garmin Connect, and a basic Nuxt 3 frontend shell with Nuxt UI to display the information.

## Functional Requirements
- **Garmin API Authentication**: Securely handle user credentials to authenticate with Garmin Connect.
- **Data Fetcher Service**: A FastAPI-based service that retrieves activity summaries, sleep data, and resting heart rate (RHR).
- **Nuxt UI Shell**: A basic web layout using Nuxt 3 and Nuxt UI components.
- **Glanceable Dashboard View**: Initial implementation of the single-page view showing current progress toward the 104-run goal.

## Non-Functional Requirements
- **TDD (Test-Driven Development)**: Ensure backend logic is verified with `pytest`.
- **Nuxt UI Integration**: Follow Nuxt UI's patterns for accessibility and responsive design.

## Acceptance Criteria
- [ ] Backend can successfully retrieve at least one activity from the Garmin API.
- [ ] Frontend displays a summary of the 104-run goal based on retrieved data.
- [ ] The dashboard is accessible via a browser.
