import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
from matplotlib.ticker import PercentFormatter, AutoMinorLocator

def generate_plot():
    # Set plotting style exactly like the notebook
    sns.set_theme(style="whitegrid")
    plt.rcParams['figure.figsize'] = (14, 6)

    file_path = '/Users/charliethompson/Documents/mosp/posts/bridgelocks/data/processed_bridge_openings.csv'
    if not os.path.exists(file_path):
        file_path = '../data/processed_bridge_openings.csv'

    print(f"Loading data from: {file_path}")
    df = pd.read_csv(file_path)

    # Convert timestamps to datetime objects
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])

    # "just show me ballard AM for now"
    df = df[df['bridge'] == 'Ballard']

    # Filter for Weekdays (Monday=0, Sunday=6)
    df = df[df['start_time'].dt.dayofweek < 5]

    min_date = df['start_time'].dt.date.min()
    max_date = df['start_time'].dt.date.max()

    total_weekdays = np.busday_count(min_date, max_date + timedelta(days=1))

    # AM only: 00:00 to 11:55
    times = pd.date_range("00:00", "11:55", freq="5min").time

    counts = {t: 0 for t in times}

    for _, row in df.iterrows():
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

    probs_ballard = [counts[t] / total_weekdays for t in times]

    # Plotting the results (Same logic as notebook)
    fig, ax = plt.subplots()

    x_labels = [t.strftime("%H:%M") for t in times]

    ax.plot(x_labels, probs_ballard, label='Ballard Bridge', color='#ff7f0e', linewidth=2)
    ax.fill_between(x_labels, probs_ballard, alpha=0.2, color='#ff7f0e')

    # X-axis ticks
    # Show labels every 1 hour (every 12th bin)
    xticks_indices = np.arange(0, len(times), 12)
    ax.set_xticks(xticks_indices)
    ax.set_xticklabels([x_labels[i] for i in xticks_indices], rotation=45, ha='right')

    # "Minute markers on the outer rim" -> Add minor ticks to top and bottom axes
    # We have 144 bins (5 mins each) over 12 hours.
    # To simulate minute markers, we can add 5 minor ticks between each major 5-min bin
    # Actually, seaborn whitegrid hides the top/right spines.
    # Let's enable top/bottom ticks
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.tick_params(which='minor', length=4, color='gray', direction='out', top=True, bottom=True)
    ax.tick_params(which='major', length=8, color='black', direction='out', top=True, bottom=True)
    
    # Show top spine to create a "rim"
    ax.spines['top'].set_visible(True)
    ax.spines['bottom'].set_visible(True)

    ax.yaxis.set_major_formatter(PercentFormatter(1.0))

    plt.title('Probability of Ballard Bridge Closure (AM Weekdays)', fontsize=16, pad=15)
    plt.xlabel('Time of Day', fontsize=12)
    plt.ylabel('Probability of Closure', fontsize=12)
    plt.legend(fontsize=12)

    plt.tight_layout()
    
    output_path = '../assets/ballard_am_linear.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    generate_plot()
