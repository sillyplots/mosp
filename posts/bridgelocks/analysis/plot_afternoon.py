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
            for seg_start, seg_end in segments:
                if seg_start < bin_end_min and seg_end > bin_start_min:
                    counts[t].add(row['start_time'].date())
                    break
    probs, cis = [], []
    for t in times:
        p = len(counts[t]) / total_weekdays
        probs.append(p)
        se = np.sqrt(p * (1 - p) / total_weekdays) if total_weekdays > 0 else 0
        cis.append(1.96 * se)
    return np.array(probs), np.array(cis)

def compute_expected_wait(df, bridge_name, times, active_dates):
    b_df = df[df['bridge'] == bridge_name]
    means, cis = [], []
    for t in times:
        bin_start = t.hour * 60 + t.minute
        bin_end = bin_start + 5.0
        date_to_wait = {d: 0.0 for d in active_dates}
        for _, row in b_df.iterrows():
            d = row['start_time'].date()
            if d not in active_dates: continue
            start_min = row['start_time'].hour * 60 + row['start_time'].minute + row['start_time'].second / 60.0
            end_min = row['end_time'].hour * 60 + row['end_time'].minute + row['end_time'].second / 60.0
            segments = []
            if end_min < start_min:
                segments.append((start_min, 1440, 1440 + end_min))
                segments.append((0, end_min, end_min))
            else:
                segments.append((start_min, end_min, end_min))
            for seg_start, seg_end, effective_end in segments:
                A = max(seg_start, bin_start)
                B = min(seg_end, bin_end)
                if A < B:
                    area = (B - A) * (effective_end - (A + B) / 2.0)
                    date_to_wait[d] += area / 5.0
        wait_array = list(date_to_wait.values())
        mean_wait = np.mean(wait_array)
        std_wait = np.std(wait_array, ddof=1) if len(wait_array) > 1 else 0
        se = std_wait / np.sqrt(len(wait_array))
        means.append(mean_wait)
        cis.append(1.96 * se)
    return np.array(means), np.array(cis)

def generate_afternoon_plots():
    sns.set_theme(style="whitegrid")

    file_path = '/Users/charliethompson/Documents/mosp/posts/bridgelocks/data/processed_bridge_openings.csv'
    if not os.path.exists(file_path):
        file_path = '../data/processed_bridge_openings.csv'

    df = pd.read_csv(file_path)
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    df = df[df['start_time'].dt.dayofweek < 5]

    # Clip at P95
    df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60.0
    cap = df['duration'].quantile(0.95)
    df['end_time'] = df.apply(
        lambda r: min(r['end_time'], r['start_time'] + pd.Timedelta(minutes=cap)), axis=1
    )

    active_dates = set(df['start_time'].dt.date)
    total_weekdays = len(active_dates)

    # 1:00 PM to 3:55 PM
    times = pd.date_range("13:00", "15:55", freq="5min").time
    x = np.arange(len(times))
    x_labels = [t.strftime("%H:%M") for t in times]

    probs_f, cis_f = compute_probs_and_errors(df, 'Fremont', times, total_weekdays)
    probs_b, cis_b = compute_probs_and_errors(df, 'Ballard', times, total_weekdays)
    wait_f, wait_ci_f = compute_expected_wait(df, 'Fremont', times, active_dates)
    wait_b, wait_ci_b = compute_expected_wait(df, 'Ballard', times, active_dates)

    os.makedirs('../assets', exist_ok=True)

    # 1. Probability with CIs
    fig, ax = plt.subplots(figsize=(16, 7))
    offset = 0.2
    ax.errorbar(x - offset, probs_f, yerr=cis_f, fmt='o', label='Fremont Bridge', color='#1f77b4', markersize=6, capsize=4, elinewidth=2, linestyle='none')
    ax.errorbar(x + offset, probs_b, yerr=cis_b, fmt='o', label='Ballard Bridge', color='#ff7f0e', markersize=6, capsize=4, elinewidth=2, linestyle='none')
    ax.set_ylabel('Probability of Closure', fontsize=14)
    ax.set_title('Afternoon Commute Closure Probability (with 95% CIs)', fontsize=18, pad=20, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=1))
    ax.set_ylim(bottom=0); ax.legend(fontsize=14, loc='upper right')
    plt.tight_layout()
    plt.savefig('../assets/fremont_vs_ballard_afternoon.png', dpi=300)
    print("Saved fremont_vs_ballard_afternoon.png")
    plt.close()

    # 2. Probability clean lines
    fig, ax = plt.subplots(figsize=(16, 7))
    ax.plot(x, probs_f, marker='o', label='Fremont Bridge', color='#1f77b4', markersize=6, linewidth=2)
    ax.plot(x, probs_b, marker='o', label='Ballard Bridge', color='#ff7f0e', markersize=6, linewidth=2)
    ax.set_ylabel('Probability of Closure', fontsize=14)
    ax.set_title('Afternoon Commute Closure Probability', fontsize=18, pad=20, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=1))
    ax.set_ylim(bottom=0); ax.legend(fontsize=14, loc='upper right')
    plt.tight_layout()
    plt.savefig('../assets/fremont_vs_ballard_afternoon_clean.png', dpi=300)
    print("Saved fremont_vs_ballard_afternoon_clean.png")
    plt.close()

    # 3. Expected wait clean lines
    fig, ax = plt.subplots(figsize=(16, 7))
    ax.plot(x, wait_f, marker='o', label='Fremont Bridge', color='#1f77b4', markersize=6, linewidth=2)
    ax.plot(x, wait_b, marker='o', label='Ballard Bridge', color='#ff7f0e', markersize=6, linewidth=2)
    ax.set_ylabel('Expected Wait Time (Minutes)', fontsize=14)
    ax.set_title('Afternoon Commute Expected Wait Times', fontsize=18, pad=20, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.set_ylim(bottom=0); ax.legend(fontsize=14, loc='upper right')
    plt.tight_layout()
    plt.savefig('../assets/expected_wait_afternoon.png', dpi=300)
    print("Saved expected_wait_afternoon.png")
    plt.close()

    # 4. Expected wait with CI bands
    fig, ax = plt.subplots(figsize=(16, 7))
    ax.plot(x, wait_f, marker='o', label='Fremont Bridge', color='#1f77b4', markersize=6, linewidth=2)
    ax.fill_between(x, np.maximum(wait_f - wait_ci_f, 0), wait_f + wait_ci_f, color='#1f77b4', alpha=0.2)
    ax.plot(x, wait_b, marker='o', label='Ballard Bridge', color='#ff7f0e', markersize=6, linewidth=2)
    ax.fill_between(x, np.maximum(wait_b - wait_ci_b, 0), wait_b + wait_ci_b, color='#ff7f0e', alpha=0.2)
    ax.set_ylabel('Expected Wait Time (Minutes)', fontsize=14)
    ax.set_title('Afternoon Commute Expected Wait Times (with 95% CIs)', fontsize=18, pad=20, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10)
    ax.set_ylim(bottom=0); ax.legend(fontsize=14, loc='upper right')
    plt.tight_layout()
    plt.savefig('../assets/expected_wait_afternoon_ci.png', dpi=300)
    print("Saved expected_wait_afternoon_ci.png")
    plt.close()

if __name__ == "__main__":
    generate_afternoon_plots()
