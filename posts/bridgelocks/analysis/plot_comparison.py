import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import PercentFormatter

def compute_probs_and_errors(df, bridge_name, times, total_weekdays):
    b_df = df[df['bridge'] == bridge_name]
    counts = {t: set() for t in times}

    for _, row in b_df.iterrows():
        event_start_min = row['start_time'].hour * 60 + row['start_time'].minute
        event_end_min = row['end_time'].hour * 60 + row['end_time'].minute
        
        if event_end_min < event_start_min:
            segments = [(event_start_min, 1440), (0, event_end_min)]
        else:
            segments = [(event_start_min, event_end_min)]
            
        for t in times:
            bin_start_min = t.hour * 60 + t.minute
            bin_end_min = bin_start_min + 5
            
            overlap = False
            for seg_start, seg_end in segments:
                if seg_start < bin_end_min and seg_end > bin_start_min:
                    overlap = True
                    break
                    
            if overlap:
                counts[t].add(row['start_time'].date())

    probs = []
    cis = []
    for t in times:
        p = len(counts[t]) / total_weekdays
        probs.append(p)
        # 95% Confidence Interval using normal approximation for binomial proportion
        se = np.sqrt(p * (1 - p) / total_weekdays) if total_weekdays > 0 else 0
        cis.append(1.96 * se)

    return np.array(probs), np.array(cis)

def plot_comparison():
    sns.set_theme(style="whitegrid")
    
    file_path = '/Users/charliethompson/Documents/mosp/posts/bridgelocks/data/processed_bridge_openings.csv'
    if not os.path.exists(file_path):
        file_path = '../data/processed_bridge_openings.csv'

    df = pd.read_csv(file_path)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])

    # Filter for Weekdays
    df = df[df['start_time'].dt.dayofweek < 5]

    # Active dates
    active_dates = set(df['start_time'].dt.date)
    total_weekdays = len(active_dates)

    # 09:00 to 11:55 (36 bins)
    times = pd.date_range("09:00", "11:55", freq="5min").time

    probs_fremont, cis_fremont = compute_probs_and_errors(df, 'Fremont', times, total_weekdays)
    probs_ballard, cis_ballard = compute_probs_and_errors(df, 'Ballard', times, total_weekdays)

    x = np.arange(len(times))
    offset = 0.2

    fig, ax = plt.subplots(figsize=(16, 7))
    
    # Error bar plots (points with CIs instead of bars)
    ax.errorbar(x - offset, probs_fremont, yerr=cis_fremont, fmt='o', label='Fremont Bridge', color='#1f77b4', markersize=6, capsize=4, elinewidth=2, linestyle='none')
    ax.errorbar(x + offset, probs_ballard, yerr=cis_ballard, fmt='o', label='Ballard Bridge', color='#ff7f0e', markersize=6, capsize=4, elinewidth=2, linestyle='none')

    ax.set_ylabel('Probability of Closure', fontsize=14)
    ax.set_title('Morning Commute Closure Probability (with 95% Confidence Intervals)', fontsize=18, pad=20, fontweight='bold')
    
    # Format x-ticks
    x_labels = [t.strftime("%H:%M") for t in times]
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    
    # Format y-ticks as percentages
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=1))
    
    # Ensure y-axis bounds make sense
    ax.set_ylim(bottom=0)
    
    ax.legend(fontsize=14, loc='upper right')

    plt.tight_layout()
    
    output_path = '../assets/fremont_vs_ballard_morning.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to {output_path}")
    plt.close()

    # --- Clean version: lines without error bars ---
    fig, ax = plt.subplots(figsize=(16, 7))

    ax.plot(x, probs_fremont, marker='o', label='Fremont Bridge', color='#1f77b4', markersize=6, linewidth=2)
    ax.plot(x, probs_ballard, marker='o', label='Ballard Bridge', color='#ff7f0e', markersize=6, linewidth=2)

    ax.set_ylabel('Probability of Closure', fontsize=14)
    ax.set_title('Morning Commute Closure Probability', fontsize=18, pad=20, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=1))
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=14, loc='upper right')

    plt.tight_layout()

    output_path_clean = '../assets/fremont_vs_ballard_morning_clean.png'
    plt.savefig(output_path_clean, dpi=300)
    print(f"Plot saved to {output_path_clean}")

if __name__ == "__main__":
    plot_comparison()
