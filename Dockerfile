# Use official Playwright Python image which comes pre-installed with all necessary system libraries
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy Python dependency declarations
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
COPY . .

# Expose standard port for FastAPI
EXPOSE 8000

# Launch uvicorn ASGI server hosting the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
