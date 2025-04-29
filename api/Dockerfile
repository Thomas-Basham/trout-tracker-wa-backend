# API Dockerfile
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies needed for numpy and scientific libraries
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    openblas-dev \
    lapack-dev \
    build-base \
    linux-headers \
    python3-dev \
    py3-pip

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Command to run API server
# CMD ["python", "main.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]