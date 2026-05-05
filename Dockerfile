# --- builder stage -----------------------------------------------------------
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency manifests first for layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies into a virtual environment inside the image
RUN uv sync --frozen --no-dev

# --- runtime stage -----------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy the virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy project source
COPY scrapy.cfg ./
COPY notimaps_scraper/ ./notimaps_scraper/
COPY lambda_handler.py ./

# Make uv-managed venv the active Python environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Default command: run the news spider.
# Override DATABASE_URL and other settings via environment variables.
CMD ["scrapy", "crawl", "news"]
