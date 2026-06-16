FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and chromium browser dependencies
RUN pip install playwright && playwright install chromium --with-deps

# Copy app code
COPY . .

# Expose port (FastAPI defaults to 8000 in dev config or $PORT in prod)
EXPOSE 8000

# Default command to run FastAPI web app (can be overridden in compose for worker)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
