# Use official Python slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/scraper.py ./src/

# Command to run the scraper
CMD ["python", "-m", "src.scraper"]
