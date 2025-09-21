# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build-time dependencies (adjust if you don't need gcc/g++ or libpq-dev)
# Note: keep the list minimal to reduce image size. Add libpq-dev, build-essential, etc. only if required.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment in /opt/venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

# Upgrade pip and install dependencies
# Ensure you have a requirements.txt file; if you use pyproject.toml/poetry, adapt the install step.
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create necessary directories (if your app expects these)
RUN mkdir -p data master-data logs \
    && groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app /opt/venv

# Switch to non-root user
USER appuser

# Expose port that your app listens on
EXPOSE 8000

# Health check (optional; curl may not be available for non-root user)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run your app
# Keep this as how you normally start the app locally. If you use uvicorn: replace with uvicorn command.
CMD ["python", "run_api.py"]