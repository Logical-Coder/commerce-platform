# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system packages required for mysqlclient and netcat
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first for Docker cache optimization
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy product-service source code into container
COPY . .

# Expose internal Django/Gunicorn port
EXPOSE 8000