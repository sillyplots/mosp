# Bridgelocks Project Walkthrough

## Overview
This project collects Seattle bridge opening data by scraping the [@SDOTbridges](https://x.com/SDOTbridges) X account.

## Directory Structure
-   `bridgelocks/data/` - Contains the collected JSON and processed CSV data.
-   `bridgelocks/etl/` - Scripts for collecting data.
    -   `scrape_with_playwright.py`: **Main scraper**. Requires local login once.
    -   `run_cloud_scrape.py`: Helper to run the scraper in Google Cloud (Cloud Run).
    -   `Dockerfile`: Container definition for cloud deployment.
    -   `DEPLOY.md`: Instructions for deploying to GCP.
-   `bridgelocks/analysis/` - (Any analysis scripts you have).

## How to Run Locally
1.  **First time setup**:
    ```bash
    cd bridgelocks/etl
    python3 scrape_with_playwright.py
    ```
    *Log in manually when the browser opens.*

2.  **Daily Run**:
    Just run the same command. It runs headlessly (or headed) and appends new tweets to `data/sdot_bridges_tweets.json`.

## Cloud Deployment
See `bridgelocks/etl/DEPLOY.md` for full instructions on how to push this to Google Cloud Run so it runs 24/7 without your laptop.

## Data Schema
`data/sdot_bridges_tweets.json`:
```json
[
  {
    "timestamp": "2024-05-20T10:00:00.000Z",
    "text": "The Fremont Bridge opened to traffic...",
    "created_at": "..."
  }
]
```
