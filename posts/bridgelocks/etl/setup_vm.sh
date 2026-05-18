#!/bin/bash
set -e

echo "=========================================="
echo "Setting up Fremont Bridge Predictive Engine VM"
echo "=========================================="

# Ensure script is run from its directory
cd "$(dirname "$0")"
SCRIPT_DIR=$(pwd)

echo "1. Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

echo "2. Installing Python and Pip..."
sudo apt-get install -y python3 python3-pip python3-venv

echo "3. Creating Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo "4. Installing Python Dependencies..."
pip install playwright pandas numpy

echo "5. Installing Playwright Browsers & OS Dependencies..."
playwright install chromium
sudo playwright install-deps chromium

echo "6. Configuring 1-Minute Cron Job..."
# The cron job needs to activate the venv and run the scraper
CRON_CMD="* * * * * cd $SCRIPT_DIR && source venv/bin/activate && python3 scrape_with_playwright.py >> ../data/cron.log 2>&1"

# Check if the cron job already exists to avoid duplicates
(crontab -l 2>/dev/null | grep -F "$SCRIPT_DIR/scrape_with_playwright.py") || (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "=========================================="
echo "Setup Complete!"
echo "The headless Playwright scraper and Inference engine will now run every 1 minute."
echo "Logs can be viewed at: $SCRIPT_DIR/../data/cron.log"
echo "=========================================="
