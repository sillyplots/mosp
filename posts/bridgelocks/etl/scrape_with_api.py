import os
import json
import urllib.request
import ssl
from datetime import datetime

# Configuration
OUTPUT_FILE = '../data/sdot_bridges_tweets.json'
USERNAME = 'SDOTbridges'

def get_x_token():
    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        # Fallback for local testing if needed
        token_file = os.path.join(os.path.dirname(__file__), '..', 'shhhhh', 'x_token')
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token = f.read().strip()
    return token

def make_request(url, token):
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode('utf-8'))
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise

def save_data(new_tweets):
    # Same deduplication logic as before
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), OUTPUT_FILE))
    
    if not os.path.exists(output_path):
        existing_data = []
    else:
        try:
            with open(output_path, 'r') as f:
                existing_data = json.load(f)
        except:
            existing_data = []

    seen = set()
    for t in existing_data:
        sig = f"{t.get('timestamp')}|{t.get('text')}"
        seen.add(sig)
        
    count = 0
    for t in new_tweets:
        sig = f"{t.get('timestamp')}|{t.get('text')}"
        if sig not in seen:
            existing_data.append(t)
            seen.add(sig)
            count += 1
            
    # Sort by timestamp descending
    try:
        existing_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    except:
        pass
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(existing_data, f, indent=2)
        
    print(f"Saved {count} new tweets. Total: {len(existing_data)}")

def scrape():
    token = get_x_token()
    if not token:
        print("Error: X_BEARER_TOKEN not found in env or shhhhh/x_token")
        return

    print(f"Looking up user ID for @{USERNAME}...")
    user_url = f"https://api.twitter.com/2/users/by/username/{USERNAME}"
    user_data = make_request(user_url, token)
    
    user_id = user_data.get('data', {}).get('id')
    if not user_id:
        print("Could not find user ID.")
        return
        
    print(f"Found User ID: {user_id}. Fetching tweets...")
    
    # We fetch the last 20 tweets.
    tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=20&tweet.fields=created_at"
    tweets_data = make_request(tweets_url, token)
    
    raw_tweets = tweets_data.get('data', [])
    print(f"Fetched {len(raw_tweets)} tweets from API.")
    
    formatted_tweets = []
    for rt in raw_tweets:
        # Convert API format to match existing data schema
        # API format: {"id": "123", "text": "...", "created_at": "2024-05-20T10:00:00.000Z"}
        # Expected by analysis: timestamp, text, created_at
        formatted_tweets.append({
            "timestamp": rt.get("created_at"),
            "text": rt.get("text"),
            "created_at": rt.get("created_at")
        })
        
    save_data(formatted_tweets)

if __name__ == "__main__":
    scrape()
