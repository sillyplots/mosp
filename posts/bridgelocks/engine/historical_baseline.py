import pandas as pd
import numpy as np
import json
import os
from datetime import timedelta

INPUT_CSV = '../data/processed_bridge_openings.csv'
OUTPUT_JSON = '../data/model_priors.json'

def compute_baselines():
    print(f"Loading data from {INPUT_CSV}")
    if not os.path.exists(INPUT_CSV):
        print(f"File not found: {INPUT_CSV}")
        return
        
    df = pd.read_csv(INPUT_CSV)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    
    bridges = df['bridge'].unique()
    models = {}
    
    # Filter to Weekdays only (Monday=0 ... Sunday=6) since this is a commute tool
    df = df[df['start_time'].dt.dayofweek < 5]
    
    # Only count days where the scraper successfully recorded at least one event
    active_dates = set(df['start_time'].dt.date)
    total_days = len(active_dates)
    
    # 96 bins of 15 minutes each
    times = pd.date_range("00:00", "23:45", freq="15min").time
    
    for b in bridges:
        print(f"Processing baseline for {b} Bridge...")
        b_df = df[df['bridge'] == b].sort_values('start_time')
        
        # 1. Historical Priors (15-min intervals)
        counts = {t.strftime("%H:%M"): set() for t in times}
        
        # Also build a minute-by-minute time series to compute Markov and Hazard rates
        # We'll just sample a few days or use the full series mathematically
        # To avoid massive arrays, we'll calculate transitions and hazards directly from events
        
        # Array of durations
        durations = b_df['duration_minutes'].values
        
        # Time since last close (Delta T)
        # Calculate time between the end of one event and the start of the next
        delta_ts = []
        for i in range(1, len(b_df)):
            prev_end = b_df.iloc[i-1]['end_time']
            curr_start = b_df.iloc[i]['start_time']
            dt = (curr_start - prev_end).total_seconds() / 60
            if dt > 0:
                delta_ts.append(dt)
                
        # Hazard rate (Empirical distribution of time between closures)
        # We can store the 10th, 25th, 50th, 75th, 90th percentiles
        if len(delta_ts) > 0:
            hazard_percentiles = np.percentile(delta_ts, [10, 25, 50, 75, 90]).tolist()
        else:
            hazard_percentiles = [60, 120, 240, 480, 1440]
            
        # P(S_{t+15}=1 | S_t=1) -> if it's closed now, what's the chance it's still closed in 15 mins?
        # This is simply the probability that a closure duration > 15 mins.
        prob_stay_closed = len([d for d in durations if d > 15]) / len(durations) if len(durations) > 0 else 0
        
        for _, row in b_df.iterrows():
            event_start_min = row['start_time'].hour * 60 + row['start_time'].minute
            event_end_min = row['end_time'].hour * 60 + row['end_time'].minute
            
            if event_end_min < event_start_min:
                segments = [(event_start_min, 1440), (0, event_end_min)]
            else:
                segments = [(event_start_min, event_end_min)]
                
            for t in times:
                bin_start_min = t.hour * 60 + t.minute
                bin_end_min = bin_start_min + 15
                
                overlap = False
                for seg_start, seg_end in segments:
                    if seg_start < bin_end_min and seg_end > bin_start_min:
                        overlap = True
                        break
                
                if overlap:
                    counts[t.strftime("%H:%M")].add(row['start_time'].date())
        
        # P(delay) = total days with an overlap / total days
        priors = {k: min(1.0, len(v) / total_days) for k, v in counts.items()}
        
        # Mean events per day (Volume)
        mean_volume = len(b_df) / total_days
        
        models[b] = {
            "priors_15min": priors,
            "markov_p_stay_closed": prob_stay_closed,
            "hazard_delta_t_percentiles": hazard_percentiles,
            "mean_daily_volume": mean_volume
        }
        
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(models, f, indent=2)
        
    print(f"Exported models to {OUTPUT_JSON}")

if __name__ == "__main__":
    compute_baselines()
