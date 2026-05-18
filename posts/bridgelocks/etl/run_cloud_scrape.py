import os
import subprocess
from google.cloud import storage

BUCKET_NAME = "bridgelocks-data"
DATA_FILE = "sdot_bridges_tweets.json"

def download_data():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(DATA_FILE)
    
    # We download the file into data directory relative to the scraper script
    os.makedirs("../data", exist_ok=True)
    local_path = f"../data/{DATA_FILE}"
    
    if blob.exists():
        print(f"Downloading {DATA_FILE} from GCS...")
        blob.download_to_filename(local_path)
    else:
        print("No existing data found in GCS. Starting fresh.")

def upload_data():
    local_path = f"../data/{DATA_FILE}"
    if os.path.exists(local_path):
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(DATA_FILE)
        
        print(f"Uploading {DATA_FILE} to GCS...")
        blob.upload_from_filename(local_path)

def main():
    # 1. Get existing data
    download_data()
    
    # 2. Run API Scraper
    print("Running scraper...")
    subprocess.run(["python3", "scrape_with_api.py"], check=False)
    
    # 3. Save updated data
    upload_data()

if __name__ == "__main__":
    main()
