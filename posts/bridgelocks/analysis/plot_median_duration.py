import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def compute_mean_duration(df, bridge_name, times):
    b_df = df[df['bridge'] == bridge_name]
    
    medians = []
    
    for t in times:
        bin_start = t.hour * 60 + t.minute
        bin_end = bin_start + 5.0
        
        durations = []
        for _, row in b_df.iterrows():
            start_min = row['start_time'].hour * 60 + row['start_time'].minute + row['start_time'].second / 60.0
            end_min = row['end_time'].hour * 60 + row['end_time'].minute + row['end_time'].second / 60.0
            
            # Handle midnight wrap-around
            if end_min < start_min:
                duration = (1440 - start_min) + end_min
            else:
                duration = end_min - start_min
                
            # Check if closure starts within this 5-minute bucket
            if bin_start <= start_min < bin_end:
                durations.append(duration)
                
        if len(durations) > 0:
            medians.append(np.mean(durations))
        else:
            medians.append(np.nan)
            
    return np.array(medians)

def plot_mean_duration():
    sns.set_theme(style="whitegrid")
    
    file_path = '/Users/charliethompson/Documents/mosp/posts/bridgelocks/data/processed_bridge_openings.csv'
    if not os.path.exists(file_path):
        file_path = '../data/processed_bridge_openings.csv'

    df = pd.read_csv(file_path)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])

    # Filter for Weekdays
    df = df[df['start_time'].dt.dayofweek < 5]

    # Clip durations at 95th percentile to prevent outliers from distorting results
    df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60.0
    cap = df['duration'].quantile(0.95)
    df['end_time'] = df.apply(
        lambda r: min(r['end_time'], r['start_time'] + pd.Timedelta(minutes=cap)), axis=1
    )
    print(f"Duration cap (P95): {cap:.1f} minutes")

    # 09:00 to 11:55 (36 bins)
    times = pd.date_range("09:00", "11:55", freq="5min").time

    medians_fremont = compute_mean_duration(df, 'Fremont', times)
    medians_ballard = compute_mean_duration(df, 'Ballard', times)

    x = np.arange(len(times))

    fig, ax = plt.subplots(figsize=(16, 7))
    
    # Line plots (ignoring NaNs)
    ax.plot(x, medians_fremont, marker='o', label='Fremont Bridge', color='#1f77b4', markersize=6, linewidth=2)
    ax.plot(x, medians_ballard, marker='o', label='Ballard Bridge', color='#ff7f0e', markersize=6, linewidth=2)

    ax.set_ylabel('Average Closure Duration (Minutes)', fontsize=14)
    ax.set_title('Morning Commute Average Closure Duration (By Start Time Bucket)', fontsize=18, pad=20, fontweight='bold')
    
    # Format x-ticks
    x_labels = [t.strftime("%H:%M") for t in times]
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=14, loc='upper right')

    plt.tight_layout()
    
    output_path = '../assets/median_duration_morning.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    plot_mean_duration()
