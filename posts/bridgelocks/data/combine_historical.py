import pandas as pd
import json
import re
import os
import sys

# Import the parsing logic from process_data
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'analysis'))
from process_data import parse_tweet

def combine():
    print("Loading historical_sheet.csv...")
    try:
        new_raw_df = pd.read_csv('historical_sheet.csv')
    except Exception as e:
        print(f"Failed to load historical_sheet.csv: {e}")
        return

    # Convert the 'data.text' column into a list of dictionaries that parse_tweet can handle
    if 'data.text' not in new_raw_df.columns:
        print("Column 'data.text' not found in historical_sheet.csv")
        return
        
    raw_tweets = [{'text': str(text)} for text in new_raw_df['data.text'].dropna()]
    print(f"Found {len(raw_tweets)} raw tweets in the new sheet.")

    parsed_events = []
    for tweet in raw_tweets:
        event = parse_tweet(tweet)
        if event:
            parsed_events.append(event)
            
    new_df = pd.DataFrame(parsed_events)
    print(f"Successfully parsed {len(new_df)} events from the new data.")
    
    if len(new_df) == 0:
        return

    # Drop duplicates in new_df
    new_df = new_df.drop_duplicates(subset=['bridge', 'status', 'timestamp'])
    
    # Calculate Durations for the new data
    new_df = new_df.sort_values(by=['bridge', 'timestamp'])
    results = []
    for bridge, group in new_df.groupby('bridge'):
        group = group.sort_values('timestamp')
        events = group.to_dict('records')
        
        i = 0
        while i < len(events):
            current_event = events[i]
            if current_event['status'] == 'closed':
                next_event = None
                for j in range(i + 1, len(events)):
                    if events[j]['status'] == 'open':
                        next_event = events[j]
                        break
                    elif events[j]['status'] == 'closed':
                        break
                
                if next_event:
                    duration = (next_event['timestamp'] - current_event['timestamp']).total_seconds() / 60
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

    new_results_df = pd.DataFrame(results)
    print(f"Calculated {len(new_results_df)} full closures from the new data.")
    
    if len(new_results_df) == 0:
        return

    # Load existing processed_bridge_openings.csv
    existing_file = 'processed_bridge_openings.csv'
    if os.path.exists(existing_file):
        existing_df = pd.read_csv(existing_file)
        existing_df['start_time'] = pd.to_datetime(existing_df['start_time'])
        existing_df['end_time'] = pd.to_datetime(existing_df['end_time'])
        print(f"Loaded existing dataset with {len(existing_df)} closures.")
    else:
        existing_df = pd.DataFrame()
        print("No existing processed_bridge_openings.csv found. Creating new.")

    # Combine
    combined_df = pd.concat([existing_df, new_results_df])
    
    # Sort and Deduplicate the final combined dataset
    before_len = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['bridge', 'start_time', 'end_time'])
    combined_df = combined_df.sort_values(by=['bridge', 'start_time'])
    print(f"Deduplicated combined dataset: {before_len} -> {len(combined_df)} closures.")

    # Save
    combined_df.to_csv(existing_file, index=False)
    print(f"Saved combined data to {existing_file}")

if __name__ == "__main__":
    combine()
