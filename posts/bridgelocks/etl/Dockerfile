FROM python:3.11-slim

# Install python deps
RUN pip install google-cloud-storage

WORKDIR /app

# Copy scripts
COPY scrape_with_api.py .
COPY run_cloud_scrape.py .

# Entrypoint
CMD ["python3", "run_cloud_scrape.py"]
