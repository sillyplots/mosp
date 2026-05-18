import os
import json
import urllib.request
import ssl
from datetime import datetime

OUTPUT_FILE = '../data/sdot_bridges_tweets.json'
USERNAME = 'SDOTbridges'

def get_x_token():
    token_file = os.path.join(os.path.dirname(__file__), '..', 'shhhhh', 'x_token')
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return f.read().strip()
    return os.environ.get("X_BEARER_TOKEN")

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

def save_data(new_tweets):
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
            
    try:
        existing_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    except:
        pass
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(existing_data, f, indent=2)
        
    print(f"Saved {count} new tweets. Total: {len(existing_data)}")

def run_backfill():
    token = get_x_token()
    if not token:
        print("Error: Token not found.")
        return

    print(f"Looking up user ID for @{USERNAME}...")
    user_url = f"https://api.twitter.com/2/users/by/username/{USERNAME}"
    user_data = make_request(user_url, token)
    user_id = user_data.get('data', {}).get('id')
    
    if not user_id:
        print("Could not find user ID.")
        return

    print(f"Starting backfill for User ID: {user_id}")
    
    all_tweets = []
    pagination_token = None
    
    # API allows 100 per request, max 3200 total
    for i in range(32): # 32 * 100 = 3200
        url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=100&tweet.fields=created_at"
        if pagination_token:
            url += f"&pagination_token={pagination_token}"
            
        print(f"Fetching page {i+1}...")
        data = make_request(url, token)
        
        raw_tweets = data.get('data', [])
        all_tweets.extend(raw_tweets)
        
        pagination_token = data.get('meta', {}).get('next_token')
        if not pagination_token:
            print("No more pages available.")
            break

    formatted_tweets = []
    for rt in all_tweets:
        formatted_tweets.append({
            "timestamp": rt.get("created_at"),
            "text": rt.get("text"),
            "created_at": rt.get("created_at")
        })
        
    print(f"Total tweets fetched: {len(formatted_tweets)}")
    save_data(formatted_tweets)

if __name__ == "__main__":
    run_backfill()
