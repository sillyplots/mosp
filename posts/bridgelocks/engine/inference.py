import json
import os
import re
from datetime import datetime, timezone
import pandas as pd

TWEETS_FILE = '../data/sdot_bridges_tweets.json'
PRIORS_FILE = '../data/model_priors.json'
OUTPUT_FILE = '../data/live_predictions.json'

def parse_tweet(tweet):
    text = tweet.get('text', '')
    original_timestamp = tweet.get('timestamp') or tweet.get('created_at')

    bridge_match = re.search(r"The (.*?) Bridge has", text)
    if not bridge_match:
        return None
    bridge_name = bridge_match.group(1)
    
    if "closed to traffic" in text.lower():
        status = "closed"
    elif "reopened to traffic" in text.lower():
        status = "open"
    else:
        return None

    final_dt = None
    if original_timestamp:
        try:
            # We standardize everything to US/Pacific to match historical baselines
            final_dt = pd.to_datetime(original_timestamp).tz_localize('UTC').tz_convert('US/Pacific').to_pydatetime()
        except:
            pass
            
    if not final_dt:
        time_match = re.search(r"at\s+(.*?) on (\d{2}/\d{2}/\d{4})", text)
        if time_match:
            try:
                full_str = f"{time_match.group(2)} {time_match.group(1)}"
                final_dt = datetime.strptime(full_str, "%m/%d/%Y %I:%M %p")
                # Assume parsed strings from X are local Seattle time
                final_dt = pd.Timestamp(final_dt).tz_localize('US/Pacific').to_pydatetime()
            except ValueError:
                pass

    if not final_dt:
        return None

    return {
        'bridge': bridge_name,
        'status': status,
        'timestamp': final_dt
    }

def run_inference():
    if not os.path.exists(PRIORS_FILE):
        print(f"Priors file not found: {PRIORS_FILE}")
        return
        
    with open(PRIORS_FILE, 'r') as f:
        models = json.load(f)
        
    if not os.path.exists(TWEETS_FILE):
        tweets = []
    else:
        with open(TWEETS_FILE, 'r') as f:
            tweets = json.load(f)
            
    # Parse all tweets
    events = []
    for t in tweets:
        parsed = parse_tweet(t)
        if parsed:
            events.append(parsed)
            
    # Sort chronological
    events.sort(key=lambda x: x['timestamp'])
    
    # Current time in Pacific Time
    now = pd.Timestamp.now(tz='US/Pacific')
    current_time_bin = now.floor('15min').strftime('%H:%M')
    
    predictions = {}
    
    # Process for each bridge
    for bridge, model in models.items():
        bridge_events = [e for e in events if e['bridge'] == bridge]
        
        # Current state determination
        current_state = "open" # Default
        last_close_time = None
        today_openings = 0
        
        # Filter to today's events for daily volume
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for e in bridge_events:
            if e['timestamp'] >= start_of_day and e['status'] == 'closed':
                today_openings += 1
                
            # Keep tracking state
            current_state = e['status']
            if e['status'] == 'closed':
                last_close_time = e['timestamp']
                
        # Base prior for the current 15-min bin
        prior = model['priors_15min'].get(current_time_bin, 0.0)
        
        prob_delay = prior
        
        if current_state == "closed":
            # Markov chain: if closed now, prob of staying closed
            prob_delay = model['markov_p_stay_closed']
        else:
            # Hazard Rate modifier based on Delta T (minutes since last close)
            if last_close_time:
                delta_t_mins = (now - last_close_time).total_seconds() / 60
                
                # Check percentiles [10, 25, 50, 75, 90]
                p_tiers = model['hazard_delta_t_percentiles']
                hazard_multiplier = 1.0
                
                if delta_t_mins < p_tiers[0]:
                    hazard_multiplier = 0.1
                elif delta_t_mins < p_tiers[1]:
                    hazard_multiplier = 0.25
                elif delta_t_mins < p_tiers[2]:
                    hazard_multiplier = 0.5
                elif delta_t_mins < p_tiers[3]:
                    hazard_multiplier = 0.75
                # else 1.0 (normal probability returns)
                
                prob_delay *= hazard_multiplier
                
            # Bayesian Updating based on daily volume
            # Expected openings by this time of day
            daily_mean = model['mean_daily_volume']
            expected_so_far = daily_mean * (now.hour / 24.0)
            
            # Prevent div by zero or extreme scaling
            expected_so_far = max(1.0, expected_so_far)
            
            # "If current day's total openings exceed expected baseline, scale probability up"
            volume_multiplier = max(0.5, min(2.0, today_openings / expected_so_far))
            prob_delay *= volume_multiplier
            
        # Bound probability [0, 1]
        prob_delay = max(0.0, min(1.0, prob_delay))
        
        predictions[bridge] = {
            "current_state": current_state,
            "today_openings": today_openings,
            "prob_delay_next_15_min": round(prob_delay, 4),
            "last_updated": now.isoformat()
        }
        
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(predictions, f, indent=2)
        
    print(f"Generated predictions for {len(predictions)} bridges. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_inference()
