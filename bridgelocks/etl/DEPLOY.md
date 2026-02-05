# Deployment Instructions

1.  **Create GCS Bucket**:
    Create a bucket named `bridgelocks-data` (or change the name in `etl/run_cloud_scrape.py`).

2.  **Zip Local Session**:
    ```bash
    cd bridgelocks/etl
    # We need to zip the chrome_data folder which should be in ../chrome_data relative to scripts? 
    # Wait, the script expects it in current dir. Let's adjust.
    cp -r ../chrome_data .
    zip -r chrome_data.zip chrome_data
    ```

3.  **Upload Initial Session**:
    Upload `chrome_data.zip` to the `bridgelocks-data` bucket.

4.  **Deploy to Cloud Run**:
    Run this in Cloud Shell or where `gcloud` is installed:
    ```bash
    gcloud run jobs deploy bridgelocks-scraper \
      --source . \
      --tasks 1 \
      --max-retries 0 \
      --region us-central1 \
      --execute-now
    ```
    
5.  **Schedule**:
    ```bash
    gcloud scheduler jobs create http bridgelocks-scraper-daily \
      --schedule "0 9 * * *" \
      --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT-ID/jobs/bridgelocks-scraper:run" \
      --http-method POST \
      --oauth-service-account-email PROJECT-ID-compute@developer.gserviceaccount.com
    ```
