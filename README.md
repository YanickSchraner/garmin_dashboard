# Garmin Dashboard

A personal running command centre that pulls data from Garmin Connect and presents it in a fast, opinionated dashboard. Built to run on a Raspberry Pi with a 7" touch display, but works fine on any desktop browser too.

## Features

- **Dashboard** — annual run-goal progress, recent activities, health trends (RHR, sleep, stress)
- **Activity log** — full activity history with pace, HR, training effect
- **Activity detail** — HR zones, splits, aerobic/anaerobic training effect
- **Weekly stats** — sleep performance, running distance, training sessions, intensity distribution
- **Health trends** — resting heart rate, average sleep duration, and stress level compared against your January baseline
- Light / dark mode

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.13 · FastAPI · `garminconnect` · `uv` |
| Frontend | Nuxt 4 · Vue 3 · Nuxt UI · Bun |
| Deployment | Docker Compose |

---

## Getting Started (local development)

### Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- [Bun](https://bun.sh) — JavaScript runtime / package manager

### 1. Clone and install

```bash
git clone <repo-url>
cd garmin
make install
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env` with your Garmin Connect credentials:

```ini
EMAIL=you@example.com
PASSWORD=yourpassword
GARMIN_TOKEN_STORE=~/.garminconnect

# Optional — shown in the header if Garmin returns no display name
DISPLAY_NAME=

# Goals
ANNUAL_RUN_GOAL=104
WEEKLY_RUN_GOAL=2

# Docker / Frontend — URL the browser uses to reach the API
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

> **First run / MFA:** If your Garmin account uses two-factor authentication, the server will return a `403 MFA Required` error. Run the interactive login once to store tokens:
> ```bash
> uv run python -c "from garminconnect import Garmin; g = Garmin('<email>', '<password>'); g.login(); g.garth.dump('~/.garminconnect')"
> ```
> After that, the stored tokens are used automatically.

### 3. Run

```bash
make dev
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

### Other make targets

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies (Python + JS) |
| `make dev` | Start backend + frontend in parallel with hot-reload |
| `make test` | Run backend (pytest) and frontend (vitest) tests |
| `make lint` | Ruff + Nuxt lint |
| `make format` | Ruff format + Prettier |
| `make build` | Build the Nuxt frontend for production |

---

## Deployment on Raspberry Pi (Docker)

The recommended way to run this on a Pi is with Docker Compose. Both services are built for `linux/arm64`.

### Prerequisites

- Docker and Docker Compose installed on the Pi
- Your `.env` file configured (see above)

### 1. Set the public API URL

In `.env`, set `NUXT_PUBLIC_API_BASE` to the Pi's IP address so the browser can reach the backend (important if you access the dashboard from other devices):

```ini
NUXT_PUBLIC_API_BASE=http://192.168.1.42:8000
```

If you only ever use the dashboard directly on the Pi, `http://localhost:8000` is fine.

### 2. Build and start

```bash
docker compose up -d --build
```

Docker Compose automatically reads `.env` from the project root — no extra flags needed.

The dashboard is then available at `http://<pi-ip>:3000`.

### 3. Garmin authentication tokens

The backend mounts a named volume (`garmin-tokens`) at `/root/.garminconnect` so tokens survive container restarts. If you need to seed tokens from an existing installation, copy them into the volume before starting:

```bash
docker run --rm -v garmin-tokens:/dst -v ~/.garminconnect:/src alpine \
  cp -r /src/. /dst/
```

### Useful compose commands

```bash
# Start in background
docker compose up -d

# View logs
docker compose logs -f

# Rebuild after a code change
docker compose up -d --build

# Stop everything
docker compose down

# Wipe tokens volume (forces re-authentication)
docker compose down -v
```

### Port overview

| Service | Host port | Purpose |
|---------|-----------|---------|
| `backend` | `8000` | FastAPI REST API |
| `frontend` | `3000` | Nuxt SSR dashboard |

Add a reverse proxy (nginx, Caddy, Traefik) in front to expose a single port or serve over HTTPS.

---

## API Reference

The backend exposes these endpoints (also available at `/docs`):

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/me` | Display name |
| `GET` | `/config` | Dashboard config (goals) |
| `GET` | `/goal-status` | Annual run-goal progress |
| `GET` | `/activities` | Activities for a date range |
| `GET` | `/activities/recent` | Most recent N activities |
| `GET` | `/activities/{id}` | Activity detail + HR zones + splits |
| `GET` | `/health-stats` | Daily health stats for a date |
| `GET` | `/health-snapshot` | YTD RHR, sleep, and stress trends |
| `GET` | `/stats/weekly` | Current + previous week breakdown |
| `POST` | `/sync` | Invalidate cache (force re-fetch) |

---

## Project Structure

```
.
├── src/garmin_dashboard/
│   ├── main.py        # FastAPI routes
│   ├── fetcher.py     # Garmin Connect API wrapper + caching
│   └── cache.py       # In-memory TTL cache
├── frontend/
│   ├── app/
│   │   ├── pages/     # index, activities, stats/*
│   │   ├── components/
│   │   └── composables/
│   └── nuxt.config.ts
├── Dockerfile          # Backend image
├── frontend/Dockerfile # Frontend image
├── docker-compose.yml
├── .env.example
└── Makefile
```

---

## Configuration Reference

All configuration is via environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `EMAIL` | — | Garmin Connect email |
| `PASSWORD` | — | Garmin Connect password |
| `GARMIN_TOKEN_STORE` | `~/.garminconnect` | Path to stored auth tokens |
| `DISPLAY_NAME` | `""` | Fallback display name if Garmin returns none |
| `ANNUAL_RUN_GOAL` | `104` | Target number of runs per year |
| `WEEKLY_RUN_GOAL` | `2` | Target runs per week (used in sessions stats) |
| `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` | API URL visible to the browser |
| `NUXT_API_BASE_INTERNAL` | `http://localhost:8000` | API URL used by SSR (set automatically in Docker) |
