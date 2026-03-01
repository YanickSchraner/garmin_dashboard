FROM python:3.13-slim

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project metadata first (layer caching)
COPY pyproject.toml .
COPY src/ src/

# Install production dependencies
RUN uv pip install --system --no-cache -e .

# Token store directory (mount a volume here for persistence)
RUN mkdir -p /root/.garminconnect

EXPOSE 8000

CMD ["uvicorn", "garmin_dashboard.main:app", "--host", "0.0.0.0", "--port", "8000"]
