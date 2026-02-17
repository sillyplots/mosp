import os
import zipfile
import subprocess
from google.cloud import storage

BUCKET_NAME = "bridgelocks-data"
ZIP_FILE = "chrome_data.zip"
DATA_FILE = "sdot_bridges_tweets.json"

def download_session():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(ZIP_FILE)
    
    if blob.exists():
        print(f"Downloading {ZIP_FILE} from GCS...")
        blob.download_to_filename(ZIP_FILE)
        
        print("Unzipping session...")
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(".")
    else:
        print("No session found in GCS. Starting fresh (might require login).")

def upload_session():
    print("Zipping session...")
    with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Zip the chrome_data directory
        for root, dirs, files in os.walk("chrome_data"):
            for file in files:
                zipf.write(os.path.join(root, file))
    
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(ZIP_FILE)
    
    print(f"Uploading {ZIP_FILE} to GCS...")
    blob.upload_from_filename(ZIP_FILE)

def upload_data():
    if os.path.exists(DATA_FILE):
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(DATA_FILE)
        
        print(f"Uploading {DATA_FILE} to GCS...")
        blob.upload_from_filename(DATA_FILE)

def main():
    # 1. Get session
    download_session()
    
    # 2. Run Scraper (using xvfb for display)
    # Ensure xvfb is installed in Docker
    print("Running scraper...")
    # This assumes we are in the same dir as the script
    subprocess.run(["xvfb-run", "--auto-servernum", "python3", "scrape_with_playwright.py"], check=False)
    
    # 3. Save state
    upload_session()
    upload_data()

if __name__ == "__main__":
    main()
