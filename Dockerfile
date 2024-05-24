# Use an official Python runtime as a parent image on a minimal Linux base
FROM python:3.11-slim-bullseye

# Set environment variables to make Chrome run headlessly
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install Chromium and chromedriver
RUN apt-get update \
    && apt-get install -y wget gnupg2 ca-certificates \
    && apt-get install -y git \
    && apt-get install -y chromium chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add fass repo
ADD . /fass
WORKDIR /fass

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip && pip install --no-cache-dir hatch 
RUN hatch version
RUN pip install --no-cache-dir .
# RUN pip install uvicorn
# Inform Docker the container listens on port 8000
EXPOSE 8000

# Command to run the uvicorn server
CMD ["uvicorn", "fass.main:app", "--host", "0.0.0.0", "--port", "8000"]
