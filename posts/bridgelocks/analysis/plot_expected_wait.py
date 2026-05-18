import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def compute_expected_wait(df, bridge_name, times, active_dates):
    b_df = df[df['bridge'] == bridge_name]
    
    means = []
    cis = []
    
    for t in times:
        bin_start = t.hour * 60 + t.minute
        bin_end = bin_start + 5.0
        
        # Track expected wait time per active date (N total days)
        date_to_wait = {d: 0.0 for d in active_dates}
        
        for _, row in b_df.iterrows():
            d = row['start_time'].date()
            if d not in active_dates:
                continue
                
            start_min = row['start_time'].hour * 60 + row['start_time'].minute + row['start_time'].second / 60.0
            end_min = row['end_time'].hour * 60 + row['end_time'].minute + row['end_time'].second / 60.0
            
            # Create segments with their effective end times for the wait calculation
            segments = []
            if end_min < start_min:
                segments.append((start_min, 1440, 1440 + end_min))
                segments.append((0, end_min, end_min))
            else:
                segments.append((start_min, end_min, end_min))
                
            for seg_start, seg_end, effective_end in segments:
                # Find overlap between the closure segment and our 5-minute bin
                A = max(seg_start, bin_start)
                B = min(seg_end, bin_end)
                
                if A < B:
                    # Calculate continuous integral area of wait time (trapezoid rule)
                    # Area = base * average height
                    area = (B - A) * (effective_end - (A + B) / 2.0)
                    
                    # Average wait time over the 5-min bin is area / width
                    avg_wait = area / 5.0
                    date_to_wait[d] += avg_wait
                    
        # Extract the array of wait times across all N active days
        wait_array = list(date_to_wait.values())
        
        mean_wait = np.mean(wait_array)
        std_wait = np.std(wait_array, ddof=1) if len(wait_array) > 1 else 0
        se = std_wait / np.sqrt(len(wait_array))
        
        means.append(mean_wait)
        cis.append(1.96 * se)
        
    return np.array(means), np.array(cis)

def plot_expected_wait():
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

    # Active dates
    active_dates = set(df['start_time'].dt.date)

    # 09:00 to 11:55 (36 bins)
    times = pd.date_range("09:00", "11:55", freq="5min").time

    means_fremont, cis_fremont = compute_expected_wait(df, 'Fremont', times, active_dates)
    means_ballard, cis_ballard = compute_expected_wait(df, 'Ballard', times, active_dates)

    x = np.arange(len(times))

    fig, ax = plt.subplots(figsize=(16, 7))
    
    # Line plots without error bars
    ax.plot(x, means_fremont, marker='o', label='Fremont Bridge', color='#1f77b4', markersize=6, linewidth=2)
    ax.plot(x, means_ballard, marker='o', label='Ballard Bridge', color='#ff7f0e', markersize=6, linewidth=2)

    ax.set_ylabel('Expected Wait Time (Minutes)', fontsize=14)
    ax.set_title('Morning Commute Expected Wait Times', fontsize=18, pad=20, fontweight='bold')
    
    # Format x-ticks
    x_labels = [t.strftime("%H:%M") for t in times]
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=14, loc='upper right')

    plt.tight_layout()
    
    output_path = '../assets/expected_wait_morning.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to {output_path}")
    plt.close()

    # --- Version with 95% CI bands ---
    fig, ax = plt.subplots(figsize=(16, 7))

    ax.plot(x, means_fremont, marker='o', label='Fremont Bridge', color='#1f77b4', markersize=6, linewidth=2)
    ax.fill_between(x, np.maximum(means_fremont - cis_fremont, 0), means_fremont + cis_fremont, color='#1f77b4', alpha=0.2)

    ax.plot(x, means_ballard, marker='o', label='Ballard Bridge', color='#ff7f0e', markersize=6, linewidth=2)
    ax.fill_between(x, np.maximum(means_ballard - cis_ballard, 0), means_ballard + cis_ballard, color='#ff7f0e', alpha=0.2)

    ax.set_ylabel('Expected Wait Time (Minutes)', fontsize=14)
    ax.set_title('Morning Commute Expected Wait Times (with 95% Confidence Intervals)', fontsize=18, pad=20, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)

    ax.set_ylim(bottom=0)
    ax.legend(fontsize=14, loc='upper right')

    plt.tight_layout()

    output_path_ci = '../assets/expected_wait_morning_ci.png'
    plt.savefig(output_path_ci, dpi=300)
    print(f"Plot saved to {output_path_ci}")

if __name__ == "__main__":
    plot_expected_wait()
