# backend/Dockerfile
FROM python:3.11-slim

# Set a working directory inside the container
WORKDIR /app

# Install system deps needed for eventlet and any builds (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (cache layer)
COPY requirements.txt .

RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app

# Expose the port the app listens on
EXPOSE 5000

# Run the app using the module (eventlet will be used if installed)
CMD ["python", "-m", "app.api"]
