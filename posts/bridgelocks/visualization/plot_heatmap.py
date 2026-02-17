import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Input/Output
INPUT_FILE = '../data/processed_bridge_openings.csv'
ASSETS_DIR = '../assets'

def main():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)

    print(f"Loading data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    
    # Convert timestamps if needed, though we already have hour_of_day and day_of_week
    # But we need to know the Total Minutes Observed to calculate a true probability?
    # Or just "Minutes of Opening per Hour"
    
    # Let's visualize "Average Minutes Open per Hour"
    # To do this correctly, we need to know how many times each (Day, Hour) slot occurred in the dataset.
    
    # Get distinct dates in dataset
    df['date'] = pd.to_datetime(df['start_time']).dt.date
    unique_dates = df['date'].unique()
    print(f"Dataset covers {len(unique_dates)} days.")
    
    # Create a reference for how many times each weekday appeared
    date_counts = pd.Series(pd.to_datetime(unique_dates).day_name()).value_counts()
    
    # Order of days
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Process each bridge
    bridges = df['bridge'].unique()
    
    for bridge in bridges:
        print(f"Processing {bridge}...")
        bridge_df = df[df['bridge'] == bridge]
        
        # Aggregate duration by Day and Hour
        heatmap_data = bridge_df.groupby(['day_of_week', 'hour_of_day'])['duration_minutes'].sum().reset_index()
        
        # Normalize by number of occurrences of that day
        heatmap_data['num_days'] = heatmap_data['day_of_week'].map(date_counts)
        heatmap_data['avg_min_per_hour'] = heatmap_data['duration_minutes'] / heatmap_data['num_days']
        
        # Pivot for heatmap
        pivot_table = heatmap_data.pivot(index='day_of_week', columns='hour_of_day', values='avg_min_per_hour')
        
        # Reindex to ensure all days/hours are present
        pivot_table = pivot_table.reindex(days_order)
        pivot_table = pivot_table.reindex(columns=range(24))
        pivot_table = pivot_table.fillna(0)
        
        # Plot
        plt.figure(figsize=(12, 6))
        sns.heatmap(pivot_table, cmap='Reds', annot=True, fmt=".1f", linewidths=.5)
        plt.title(f"{bridge} Bridge: Average Minutes Open per Hour")
        plt.xlabel("Hour of Day")
        plt.ylabel("Day of Week")
        
        output_path = f"{ASSETS_DIR}/heatmap_{bridge.replace(' ', '_').lower()}.png"
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        print(f"Saved {output_path}")

if __name__ == "__main__":
    main()
