# Bridgelocks: Seattle Bridge Probability calculator

**What are the odds I get stuck at the Ballard Bridge right now?**

This project calculates the probability of getting stopped at various Seattle bridges (Ballard, Fremont, Spokane St, University, etc.) based on historical opening/closing data.

## Project Goal
We want to answer questions like:
- "It is 5:30 PM on a Tuesday. What is the probability the Ballard Bridge is up?"
- "Which bridge has the worst impact on commute times?"

## Data Source
Data is scraped from the official SDOT Bridges Twitter account: [https://x.com/SDOTbridges](https://x.com/SDOTbridges).

## Quick Start (Automated Scraper)

We use a Python script with Playwright to scrape data automatically. This avoids expensive API costs and supports continuous data collection.

### 1. Setup (First Time Only)
Install dependencies and run the scraper manually to log in.
```bash
cd bridgelocks/etl
python3 scrape_with_playwright.py
```
*A browser window will open. **Log in to X.com manually.** Once logged in, the script will save your session cookies for future use.*

### 2. Daily Data Collection
You can run the same command anytime to collect new tweets. It will skip duplicates.
```bash
python3 bridgelocks/etl/scrape_with_playwright.py
```
*It runs headlessly (no window) by default unless configured otherwise.*

### 3. Deploy to Cloud (Optional)
To run this 24/7 on a server (e.g., Google Cloud Run):
See **[DEPLOY.md](etl/DEPLOY.md)** for instructions on how to package your session and deploy it.

## Analysis & Visualization
Once data is collected in `data/sdot_bridges_tweets.json`:

1.  **Process Data**:
    ```bash
    python3 bridgelocks/analysis/process_data.py
    ```
    This creates `data/processed_bridge_openings.csv`.

2.  **Visualize**:
    ```bash
    python3 bridgelocks/visualization/plot_heatmap.py
    ```
    Examples will be saved to `visualizations/`.

## Directory Structure
-   `data/`: Raw JSON and processed CSVs.
-   `etl/`: Scraper scripts (`scrape_with_playwright.py`, `run_cloud_scrape.py`).
-   `analysis/`: Data cleaning logic.
-   `visualization/`: Plotting scripts.
