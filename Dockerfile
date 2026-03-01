# ---- Build Stage ----
FROM python:3.13-slim AS builder

# Pin uv version
COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /usr/local/bin/uv

# Set UV configuration
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# Copy project metadata first (for layer caching)
COPY pyproject.toml uv.lock README.md ./

# Install dependencies into a virtual environment
# We omit the project itself first to cache dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project --frozen

# Copy source code and install the project
COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen


# ---- Runtime Stage ----
FROM python:3.13-slim AS runtime

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create and set ownership for the app directory
RUN mkdir /app && chown appuser:appuser /app
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy source code to the runtime stage
COPY --chown=appuser:appuser src/ src/

# Token store directory (mount a volume here for persistence)
# We set it in a location accessible to the non-root user
RUN mkdir -p /home/appuser/.garminconnect && \
    chown -R appuser:appuser /home/appuser/.garminconnect

# Switch to non-root user
USER appuser

EXPOSE 8000

# Healthcheck for backend
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost', 8000); conn.request('GET', '/health'); r = conn.getresponse(); exit(0 if r.status == 200 else 1)"

CMD ["uvicorn", "garmin_dashboard.main:app", "--host", "0.0.0.0", "--port", "8000"]
