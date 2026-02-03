# Multi-stage build for backend
FROM python:3.11-alpine as builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv (prod only)
ENV UV_CACHE_DIR=/tmp/uv-cache
RUN uv sync --no-dev --frozen || uv sync --no-dev
RUN rm -rf /tmp/uv-cache /root/.cache

# Production stage
FROM python:3.11-alpine

# Install runtime dependencies
RUN apk add --no-cache \
    postgresql-libs

# Create non-root user
RUN adduser -D -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Remove cached bytecode to keep the image small
RUN find /app/.venv -type d -name "__pycache__" -prune -exec rm -rf {} + && \
    find /app/.venv -type f -name "*.pyc" -delete

# Change ownership after copying
RUN chown -R appuser:appuser /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Make sure we use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8000

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://localhost:{os.getenv(\"PORT\", \"8000\")}/health').read()" || exit 1

# Start server (migrations handled via Railway Pre-Deploy)
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
