import nbformat as nbf

nb = nbf.v4.new_notebook()

text = """# Seattle Bridge Closure Probability Analysis
This notebook analyzes the historical bridge closure data scraped from `@SDOTbridges` to determine the probability of a bridge being closed during any given 5-minute increment of the day.

We are specifically focusing on:
- **Weekdays only** (Monday - Friday)
- **Fremont Bridge** vs **Ballard Bridge** (All times in PST)
"""

code = """import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta

# Set plotting style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (14, 6)

# Handle different working directories by starting with the absolute path
file_path = '/Users/charliethompson/Documents/mosp/posts/bridgelocks/data/processed_bridge_openings.csv'

if not os.path.exists(file_path):
    file_path = '../data/processed_bridge_openings.csv'
if not os.path.exists(file_path):
    file_path = 'data/processed_bridge_openings.csv'
if not os.path.exists(file_path):
    file_path = 'processed_bridge_openings.csv' # Colab fallback

print(f"Loading data from: {file_path}")
df = pd.read_csv(file_path)

# Convert timestamps to datetime objects
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])

# Filter for Fremont and Ballard bridges only
df = df[df['bridge'].isin(['Fremont', 'Ballard'])]

# Filter for Weekdays (Monday=0, Sunday=6)
# Keep only days 0 to 4
df = df[df['start_time'].dt.dayofweek < 5]

print(f"Total weekday bridge closures analyzed:\\n{df['bridge'].value_counts().to_string()}")

# Calculate the total number of weekdays in our dataset's date range
min_date = df['start_time'].dt.date.min()
max_date = df['start_time'].dt.date.max()

total_weekdays = np.busday_count(min_date, max_date + timedelta(days=1))
print(f"\\nTotal number of weekdays in the dataset (from {min_date} to {max_date}): {total_weekdays}")
"""

code2 = """# Create 5-minute bins for a 24-hour day (288 bins total)
times = pd.date_range("00:00", "23:55", freq="5min").time

# Initialize counts
counts = {
    'Fremont': {t: 0 for t in times},
    'Ballard': {t: 0 for t in times}
}

# Iterate over all closure events
for _, row in df.iterrows():
    b = row['bridge']
    
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
            counts[b][t] += 1

probs_fremont = [counts['Fremont'][t] / total_weekdays for t in times]
probs_ballard = [counts['Ballard'][t] / total_weekdays for t in times]
"""

code3 = """# Plotting the results
fig, ax = plt.subplots()

x_labels = [t.strftime("%H:%M") for t in times]

ax.plot(x_labels, probs_fremont, label='Fremont Bridge', color='#1f77b4', linewidth=2)
ax.plot(x_labels, probs_ballard, label='Ballard Bridge', color='#ff7f0e', linewidth=2)

ax.fill_between(x_labels, probs_fremont, alpha=0.2, color='#1f77b4')
ax.fill_between(x_labels, probs_ballard, alpha=0.2, color='#ff7f0e')

xticks_indices = np.arange(0, len(times), 12)
ax.set_xticks(xticks_indices)
ax.set_xticklabels([x_labels[i] for i in xticks_indices], rotation=45, ha='right')

from matplotlib.ticker import PercentFormatter
ax.yaxis.set_major_formatter(PercentFormatter(1.0))

plt.title('Probability of Getting Stuck at a Seattle Bridge (Weekdays, PST)', fontsize=16, pad=15)
plt.xlabel('Time of Day', fontsize=12)
plt.ylabel('Probability of Closure', fontsize=12)
plt.legend(fontsize=12)

plt.tight_layout()
plt.show()
"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(text),
    nbf.v4.new_code_cell(code),
    nbf.v4.new_code_cell(code2),
    nbf.v4.new_code_cell(code3)
]

with open('bridge_probability.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Notebook regenerated successfully.")
