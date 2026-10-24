FROM python:3.12-slim

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src:/app

# Install dependencies using pre-built wheels (no build-essential required)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Ensure persistent directories exist
RUN mkdir -p /app/data /app/logs

# Copy application source code
COPY main.py .
COPY src/ ./src/

# Expose Telegram Mini App port
EXPOSE 8080

# Health check to ensure Mini App server responds
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request, sys; port = os.getenv('WEB_APP_PORT', '8080'); sys.exit(0 if urllib.request.urlopen(f'http://localhost:{port}/api/health', timeout=3).getcode() == 200 else 1)"

CMD ["python", "main.py"]
