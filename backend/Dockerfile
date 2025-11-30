FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN uv lock && uv sync --frozen --no-install-project

# Copy application code
COPY . .

# Build the application (if needed, or just prepare environment)
# For this setup, we just need the environment

FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy the environment from the builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check (using Python instead of curl which isn't in slim image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
