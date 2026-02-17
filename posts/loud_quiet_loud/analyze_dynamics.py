import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from segmentation_pipeline import HybridSegmenter

def analyze_track_dynamics(file_path):
    """
    Analyzes the dynamic range of a track using Hybrid Segmentation.
    """
    try:
        # Load audio (mono)
        y, sr = librosa.load(file_path, mono=True)
        
        # Initialize Segmenter
        segmenter = HybridSegmenter(sr=sr)
        
        # Get Boundaries
        boundaries = segmenter.segment(file_path)
        
        # Calculate Segment Metrics
        # We want to know the "Loudness" of each segment to classify them.
        loudness_db = librosa.amplitude_to_db(librosa.feature.rms(y=y)[0], ref=np.max)
        times = librosa.times_like(loudness_db, sr=sr)
        
        transitions = boundaries['combined']
        # Add start and end
        segments_times = np.concatenate([[0], transitions, [times[-1]]])
        
        segment_levels = []
        for i in range(len(segments_times)-1):
            start = segments_times[i]
            end = segments_times[i+1]
            
            # Find indices
            idx_start = np.argmin(np.abs(times - start))
            idx_end = np.argmin(np.abs(times - end))
            
            if idx_end > idx_start:
                seg_loudness = np.mean(loudness_db[idx_start:idx_end])
                segment_levels.append(seg_loudness)
            else:
                segment_levels.append(np.nan) # Should not happen usually
                
        # Filter NaNs
        segment_levels = [l for l in segment_levels if not np.isnan(l)]
        
        # Calculate Jumps
        if len(segment_levels) > 1:
            jumps = np.diff(segment_levels)
            significant_jumps = jumps[np.abs(jumps) > 3.0] # 3dB threshold
            num_transitions = len(significant_jumps)
            avg_trans_mag = np.mean(np.abs(significant_jumps)) if num_transitions > 0 else 0
        else:
            num_transitions = 0
            avg_trans_mag = 0

        # Basic Metrics
        p90 = np.percentile(loudness_db, 90)
        p10 = np.percentile(loudness_db, 10)
        dynamic_range = p90 - p10
        
        filename = os.path.basename(file_path).replace('.mp3', '').replace('_', ' ')
        
        return {
            'track': filename,
            'dynamic_range': dynamic_range,
            'num_transitions': num_transitions,
            'avg_trans_mag': avg_trans_mag,
            'loudness_profile': loudness_db, 
            'boundaries': boundaries, # Store all boundary info
            'group': 'Pixies' if 'pixies' in file_path.lower() else 'Control'
        }
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def plot_dynamics_comparison(results_df):
    """
    Generates a scatter plot of Dynamic Range vs Loud/Quiet Diff
    """
    plt.figure(figsize=(12, 8))
    
    groups = results_df.groupby('group')
    for name, group in groups:
        plt.scatter(group['avg_trans_mag'], group['num_transitions'], 
                   marker='o', label=name, s=group['dynamic_range']*15, alpha=0.7)
        
        for i, row in group.iterrows():
            if row['avg_trans_mag'] > 5 or row['num_transitions'] > 8 or name == 'Pixies':
                plt.annotate(row['track'], (row['avg_trans_mag'], row['num_transitions']), 
                             fontsize=8, alpha=0.8, xytext=(5,5), textcoords='offset points')

    plt.title('Loud-Quiet-Loud: Hybrid Segmentation Analysis')
    plt.xlabel('Avg Step Size (dB)')
    plt.ylabel('Significant Transitions (Count)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, 'output', 'transition_analysis.png')
    plt.savefig(output_path)
    print(f"Saved {output_path}")

def plot_loudness_traces(metrics_list):
    """
    Plots the loudness envelope with DETECTED BOUNDARIES.
    """
    # Plot everything we analyzed
    tracks_to_plot = metrics_list
    
    for item in tracks_to_plot:
        plt.figure(figsize=(14, 6))
        
        profile = item['loudness_profile']
        times = librosa.times_like(profile)
        
        # Plot Loudness
        plt.plot(times, profile, label='Loudness (dB)', alpha=0.7, color='gray')
        
        # Plot Boundaries
        bounds = item['boundaries']
        
        # Calculate Step Function for Segment Levels
        # We need to reconstruct the "levels" based on the boundaries
        transitions = bounds['combined']
        segments_times = np.concatenate([[0], transitions, [times[-1]]])
        
        step_times = []
        step_levels = []
        
        for i in range(len(segments_times)-1):
            start = segments_times[i]
            end = segments_times[i+1]
            
            idx_start = np.argmin(np.abs(times - start))
            idx_end = np.argmin(np.abs(times - end))
            
            if idx_end > idx_start:
                level = np.mean(profile[idx_start:idx_end])
                # Add points for step plotting
                step_times.extend([start, end])
                step_levels.extend([level, level])
        
        # Plot Step Function
        plt.plot(step_times, step_levels, label='Segmented Level', color='orange', linewidth=2, alpha=0.9)

        # Harmonic = Blue
        for b in bounds['harmonic']:
            plt.axvline(x=b, color='blue', linestyle='--', alpha=0.3, label='Harmonic' if b==bounds['harmonic'][0] else "")
            
        # Dynamic = Red
        for b in bounds['dynamic']:
            plt.axvline(x=b, color='red', linestyle='-', alpha=0.5, label='Dynamic' if b==bounds['dynamic'][0] else "")
            
        plt.title(f"Segmentation Analysis: {item['track']}")
        plt.xlabel('Time (s)')
        plt.ylabel('Loudness (dB)')
        plt.legend()
        plt.tight_layout()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        clean_name = item['track'].replace(' ', '_').replace('?', '')
        output_path = os.path.join(base_dir, 'output', f'segmentation_{clean_name}.png')
        plt.savefig(output_path)
        print(f"Saved {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dirs = [
        os.path.join(base_dir, "data", "pixies"),
        os.path.join(base_dir, "data", "control")
    ]
    
    all_files = []
    for d in data_dirs:
        all_files.extend(glob.glob(os.path.join(d, "**", "*.mp3"), recursive=True))
        all_files.extend(glob.glob(os.path.join(d, "**", "*.m4a"), recursive=True))
        all_files.extend(glob.glob(os.path.join(d, "**", "*.wav"), recursive=True))
    
    print(f"Found {len(all_files)} files to analyze.")
    
    output_dir = os.path.join(base_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metrics_list = []
    for f in all_files:
        # if "Where Is My Mind" not in f and "Tame" not in f: continue 
        
        print(f"Analyzing {f}...")
        res = analyze_track_dynamics(f)
        if res:
            metrics_list.append(res)
    
    if metrics_list:
        df = pd.DataFrame(metrics_list)
        print("\nTop 'Switchers' (Hybrid Segmentation):")
        # Ensure we see all columns
        pd.set_option('display.max_columns', None)
        print(df[['track', 'num_transitions', 'avg_trans_mag']].sort_values('num_transitions', ascending=False).head(15))
        
        plot_dynamics_comparison(df)
        plot_loudness_traces(metrics_list)

