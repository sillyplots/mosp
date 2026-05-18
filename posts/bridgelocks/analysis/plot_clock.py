import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from matplotlib.ticker import PercentFormatter

# Helper to split data and plot clocks
def plot_clock_face(ax, probs, title, color, max_prob=None):
    num_bins = len(probs)
    angles = np.linspace(0, 2 * np.pi, num_bins, endpoint=False)
    width = (2 * np.pi) / num_bins

    # Plot the probability bars
    ax.bar(angles, probs, width=width, color=color, alpha=0.8, edgecolor='none', zorder=2)

    # Thematic clock settings
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)

    # Set full 12-hour clock labels
    tick_labels = ['12', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
    tick_angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)

    ax.set_xticks(tick_angles)
    ax.set_xticklabels(tick_labels, fontsize=28, fontweight='bold')
    
    # Minute markers (60 ticks explicitly drawn to ensure visibility)
    rmax = max_prob if max_prob else (max(probs) if len(probs) > 0 else 0.15)
    
    for i in range(60):
        angle = i * (2 * np.pi / 60)
        if i % 5 == 0:
            # Major tick (thicker, longer)
            ax.plot([angle, angle], [rmax * 0.93, rmax], color='#333333', linewidth=3, zorder=10)
        else:
            # Minor tick (thinner, shorter)
            ax.plot([angle, angle], [rmax * 0.97, rmax], color='#333333', linewidth=1.5, zorder=10)
            
    # Push hour labels further out so they don't overlap the new ticks
    ax.tick_params(axis='x', pad=20)

    plt.draw()

    for label, angle in zip(ax.get_xticklabels(), tick_angles):
        rotation = np.degrees(-angle)
        label.set_rotation(rotation)
        label.set_va('center')
        label.set_ha('center')

    # Styling
    ax.set_title(title, fontsize=14, pad=35, fontweight='bold')
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_rlabel_position(0)

    if max_prob:
        ax.set_ylim(0, max_prob)

    # Visual elements: pin and thick border
    ax.plot(0, 0, marker='o', markersize=10, color='black', zorder=5)
    ax.spines['polar'].set_linewidth(3)
    ax.spines['polar'].set_color('#333333')
    ax.set_facecolor('#f9f9f9')

def compute_probs(df, bridge_name, times, total_weekdays):
    b_df = df[df['bridge'] == bridge_name]
    counts = {t: 0 for t in times}

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
                counts[t] += 1

    return [counts[t] / total_weekdays for t in times]

def generate_analog_clocks():
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

    # Only count valid, active weekdays recorded by the scraper
    active_dates = set(df['start_time'].dt.date)
    total_weekdays = len(active_dates)

    # Full 24 hours: 00:00 to 23:55 (288 bins)
    times = pd.date_range("00:00", "23:55", freq="5min").time

    probs_fremont = compute_probs(df, 'Fremont', times, total_weekdays)
    probs_ballard = compute_probs(df, 'Ballard', times, total_weekdays)

    # Split 288 bins into 144 AM and 144 PM
    am_fremont = probs_fremont[:144]
    pm_fremont = probs_fremont[144:]
    am_ballard = probs_ballard[:144]
    pm_ballard = probs_ballard[144:]

    # Add minimal 5% padding so it tightly hugs the maximum probability
    global_max = max(max(probs_fremont), max(probs_ballard)) * 1.05

    # Layout adjustments
    fig, axes = plt.subplots(2, 2, figsize=(16, 16), subplot_kw={'projection': 'polar'})

    plot_clock_face(axes[0,0], am_fremont, 'Fremont Bridge (AM)', '#1f77b4', max_prob=global_max)
    plot_clock_face(axes[0,1], pm_fremont, 'Fremont Bridge (PM)', '#1f77b4', max_prob=global_max)
    plot_clock_face(axes[1,0], am_ballard, 'Ballard Bridge (AM)', '#ff7f0e', max_prob=global_max)
    plot_clock_face(axes[1,1], pm_ballard, 'Ballard Bridge (PM)', '#ff7f0e', max_prob=global_max)

    plt.suptitle('Seattle Bridge Closure Probabilities\n(Linked Scale Analog Clocks)', fontsize=22, y=0.98, fontweight='bold')
    plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.9, bottom=0.05, left=0.05, right=0.95)
    
    output_path = '../assets/analog_clocks.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    generate_analog_clocks()
