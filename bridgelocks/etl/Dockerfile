FROM mcr.microsoft.com/playwright/python:v1.39.0-jammy

# Install Xvfb for headless "headed" mode
RUN apt-get update && apt-get install -y xvfb zip && rm -rf /var/lib/apt/lists/*

# Install python deps
RUN pip install google-cloud-storage

WORKDIR /app

# Copy scripts
COPY scrape_with_playwright.py .
COPY run_cloud_scrape.py .

# Entrypoint
CMD ["python3", "run_cloud_scrape.py"]
