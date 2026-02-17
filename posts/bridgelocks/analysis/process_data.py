import json
import pandas as pd
import re
import os
from datetime import datetime

# Input/Output paths
INPUT_FILE_SCRAPER = '../data/sdot_bridges_tweets.json'
INPUT_FILE_API = '../data/api_tweets_raw.json'
OUTPUT_FILE = '../data/processed_bridge_openings.csv'

def parse_tweet(tweet):
    """
    Parses a single tweet object to extract bridge name, event type, and timestamp.
    Example text: "The South Park Bridge has reopened to traffic at  09:43 PM on 02/04/2026"
    """
    text = tweet.get('text', '')
    original_timestamp = tweet.get('timestamp') # Normalized key from both sources
    if not original_timestamp:
         original_timestamp = tweet.get('created_at') # Fallback for raw API data if not normalized

    # Check for bridge name
    bridge_match = re.search(r"The (.*?) Bridge has", text)
    if not bridge_match:
        return None
    bridge_name = bridge_match.group(1)
    
    # Determine Status
    if "closed to traffic" in text.lower():
        status = "closed" # Bridge is UP (Open to marine, Closed to cars)
    elif "reopened to traffic" in text.lower():
        status = "open" # Bridge is DOWN (Closed to marine, Open to cars)
    else:
        return None

    # Parse timestamp
    # 1. Try ISO timestamp first (API or consistent scraper data)
    final_dt = None
    if original_timestamp:
        try:
            final_dt = pd.to_datetime(original_timestamp).to_pydatetime()
        except:
            pass
            
    # 2. If ISO failed or missing, try parsing from text (Scraper fallback)
    if not final_dt:
        time_match = re.search(r"at\s+(.*?) on (\d{2}/\d{2}/\d{4})", text)
        if time_match:
            try:
                full_str = f"{time_match.group(2)} {time_match.group(1)}"
                final_dt = datetime.strptime(full_str, "%m/%d/%Y %I:%M %p")
            except ValueError:
                pass

    if not final_dt:
        return None

    # Normalizing timestamp to minutes to help deduplication (tweet vs scraper might differ by seconds)
    # Actually, keep precision but dedupe carefully
    
    return {
        'bridge': bridge_name,
        'status': status,
        'timestamp': final_dt,
        'original_text': text
    }

def load_json_safe(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}, skipping.")
        return []
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def main():
    print(f"Loading data...")
    scraper_data = load_json_safe(INPUT_FILE_SCRAPER)
    api_data = load_json_safe(INPUT_FILE_API)
    
    print(f"Loaded {len(scraper_data)} scraped tweets and {len(api_data)} API tweets.")
    combined_data = scraper_data + api_data
    
    parsed_events = []
    for tweet in combined_data:
        event = parse_tweet(tweet)
        if event:
            parsed_events.append(event)
            
    df = pd.DataFrame(parsed_events)
    print(f"Parsed {len(df)} total events.")
    
    # Deduplicate
    # Tweets might separate by seconds or just duplicate content
    # We drop duplicates based on Bridge, Status, and Timestamp (rounded to minute to be safe? or exact?)
    # Let's try exact first.
    before_dedupe = len(df)
    df = df.drop_duplicates(subset=['bridge', 'status', 'timestamp'])
    print(f"Deduplicated: {before_dedupe} -> {len(df)} events.")
    
    # Sort by Bridge and Time
    df = df.sort_values(by=['bridge', 'timestamp'])
    
    # Calculate Durations
    # We want to pair a 'closed' event (start of blockage) with the next 'open' event (end of blockage).
    
    results = []
    
    for bridge, group in df.groupby('bridge'):
        group = group.sort_values('timestamp')
        events = group.to_dict('records')
        
        i = 0
        while i < len(events):
            current_event = events[i]
            
            # We are looking for a 'closed' event to start a duration
            if current_event['status'] == 'closed':
                # improved logic: look ahead for the next 'open' status
                next_event = None
                for j in range(i + 1, len(events)):
                    if events[j]['status'] == 'open':
                        next_event = events[j]
                        # We found the closing pair, advance i to this index so we don't process it again as a start?
                        # ACTUALLY: A 'reopen' is never a start.
                        break
                    elif events[j]['status'] == 'closed':
                        # Two closes in a row? The first one might be valid but missing a close, or duplicate.
                        # For now, let's treat the first one as an anomaly or just take the pair if we can.
                        # Simple approach: adjacent pair.
                        break
                
                if next_event:
                    duration = (next_event['timestamp'] - current_event['timestamp']).total_seconds() / 60
                    
                    # Sanity check: Duration < 60 minutes? (Bridges rarely stay up that long except for maintenance)
                    # And > 0
                    if 0 < duration < 120:
                        results.append({
                            'bridge': bridge,
                            'start_time': current_event['timestamp'],
                            'end_time': next_event['timestamp'],
                            'duration_minutes': round(duration, 2),
                            'day_of_week': current_event['timestamp'].strftime('%A'),
                            'hour_of_day': current_event['timestamp'].hour
                        })
            
            i += 1

    results_df = pd.DataFrame(results)
    print(f"Found {len(results_df)} valid bridge openings.")
    print(results_df.head())
    print(results_df.groupby('bridge')['duration_minutes'].describe())

    results_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved processed data to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
