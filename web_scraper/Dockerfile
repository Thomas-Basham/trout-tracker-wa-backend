# Web Scraper Dockerfile
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install build tools
RUN apk add --no-cache gcc musl-dev libffi-dev build-base

# Install Python dependencies
COPY ./web_scraper/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env . 
# Copy scraper code
COPY ./web_scraper/ .

# Also copy API code into the image so it can be imported
COPY ./data ./data

# Command to run the scraper
CMD ["python", "scraper.py"]