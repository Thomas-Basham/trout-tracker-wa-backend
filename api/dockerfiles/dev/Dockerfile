FROM python:3.13-slim

# Set workdir
WORKDIR /app

# Install dependencies
COPY ./api/requirements.txt .

# Copy app files
COPY ./api/index.py .
COPY ./data/ ./data

RUN pip install --no-cache-dir -r requirements.txt
# Run the app with Uvicorn
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8080"]