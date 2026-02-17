import librosa
import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_loudness(file_path):
    print(f"Loading {file_path}...")
    y, sr = librosa.load(file_path, mono=True)
    
    hop_length = 512
    frame_length = 2048
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    loudness_db = librosa.amplitude_to_db(rms, ref=np.max)
    times = librosa.times_like(loudness_db, sr=sr, hop_length=hop_length)

    # SMART FADE REMOVAL
    # 1. Calculate the 'Body' of the song (Median Loudness)
    # We ignore the absolute silence (-80dB) for the median calc
    active_mask = loudness_db > -60
    if np.sum(active_mask) > 0:
        median_vol = np.median(loudness_db[active_mask])
    else:
        median_vol = -40 # Fallback

    # 2. Define a threshold for "Song has started/ended"
    threshold = median_vol - 12.0 
    
    # We use a rolling window to ensure we don't pick up a split-second silence in the middle
    window = int(2.0 * sr / hop_length) # 2 seconds window
    
    # Create a boolean mask of "Above Threshold"
    above_thresh = loudness_db > threshold
    
    # Find indices
    if np.any(above_thresh):
        # Start: First index > threshold
        start_idx = np.argmax(above_thresh)
        
        # End: Last index > threshold (search backwards)
        end_idx = len(loudness_db) - np.argmax(above_thresh[::-1]) - 1
        
        # Add a buffer (0.5s)
        buffer_frames = int(0.5 * sr / hop_length)
        start_idx = max(0, start_idx - buffer_frames)
        end_idx = min(len(loudness_db), end_idx + buffer_frames)
        
        # Apply Trim if reasonable
        if end_idx > start_idx + window: 
            loudness_db = loudness_db[start_idx:end_idx]
            times = times[start_idx:end_idx]
            # Adjust time axis
            times = times - times[0]
            
            print(f"Trimmed {start_idx} frames from start and {len(y)//512 - end_idx} from end.")
    
    return times, loudness_db, filename_from_path(file_path)

def filename_from_path(path):
    return os.path.basename(path).replace('.mp3', '')

from sklearn.tree import DecisionTreeRegressor

def fit_piecewise_constant(times, loudness_db, max_segments=20):
    """
    Fits a step function to the loudness curve to identify stable ranges.
    """
    # X needs to be 2D array for sklearn
    X = times.reshape(-1, 1)
    y = loudness_db
    
    # Fit a simple tree. Limit leaf nodes to force it to pick the "major" levels
    # Min samples leaf ensures we don't pick up tiny noisy blips
    # 86 frames ~ 2.0 seconds (at 512 hop, 22050Hz)
    tree = DecisionTreeRegressor(max_leaf_nodes=max_segments, min_samples_leaf=86)
    tree.fit(X, y)
    
    y_pred = tree.predict(X)
    return y_pred

def plot_case_study(tracks):
    plt.figure(figsize=(14, 12))
    
    # Create subplots sharing X axis
    fig, axes = plt.subplots(len(tracks), 1, figsize=(14, 14), sharex=False, sharey=True)
    
    colors = ['#1f77b4', '#d62728', '#2ca02c'] 
    
    for i, (path, label, color) in enumerate(tracks):
        ax = axes[i]
        times, db, name = analyze_loudness(path)
        
        # Smooth heavily for valid "range" detection input
        window_size = 50 
        smoothed = np.convolve(db, np.ones(window_size)/window_size, mode='valid')
        time_axis = times[:len(smoothed)]
        
        # 1. Plot Raw Trace (Grey/Faint)
        ax.fill_between(time_axis, -100, smoothed, color=color, alpha=0.15)
        ax.plot(time_axis, smoothed, color=color, linewidth=0.8, alpha=0.4, label='Raw Loudness')
        
        # 2. Fit Piecewise Step Function
        # We try to fit ~6-8 major "levels" per song. Max segments 30 allows for rapid changes.
        steps = fit_piecewise_constant(time_axis, smoothed, max_segments=30)
        
        # 3. Plot The "Ranges" (Step Function)
        ax.plot(time_axis, steps, color='#333333', linewidth=2.0, linestyle='-', label='Detected Ranges')
        
        ax.set_title(f"{label}: {name}", fontsize=12, fontweight='bold', loc='left')
        ax.set_ylabel('Loudness (dB)')
        
        # Annotate Significant Shifts
        # Find jump points in the step function
        diffs = np.diff(steps)
        change_indices = np.where(np.abs(diffs) > 3.0)[0] # Threshold for "significant" shift
        
        transition_count = 0
        for idx in change_indices:
            shift_amp = steps[idx+1] - steps[idx]
            # Only count if the jump is > 3.0 dB (lowered from 5.0 to catch more shifts)
            if abs(shift_amp) > 3.0:
                 ax.vlines(time_axis[idx], -40, 0, color='red', linestyle=':', alpha=0.5)
                 transition_count += 1
        
        print(f"Track: {name} | Transitions Detected: {transition_count}")

        ax.grid(True, alpha=0.3)
        ax.set_ylim(-40, 0) # Fixed scale
        if i == 0:
            ax.legend(loc='lower right')
        
    plt.xlabel('Time (s)')
    plt.tight_layout()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, 'case_study.png')
    plt.savefig(output_path)
    print(f"Case study saved to {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    import glob

    def find_file(pattern, search_root):
        # Recursive glob search
        search_path = os.path.join(search_root, "**", pattern)
        files = glob.glob(search_path, recursive=True)
        if files:
            return files[0] # Return first match
        return None

    # Find the files dynamically
    # User Request: "Mr. Grieves", "Where Is My Mind", "Brick Is Red"
    mr_grieves_path = find_file("*Mr. Grieves.mp3", os.path.join(base_dir, "data/pixies"))
    wimm_path = find_file("*Where Is My Mind*.mp3", os.path.join(base_dir, "data/pixies"))
    brick_path = find_file("*Brick Is Red.mp3", os.path.join(base_dir, "data/pixies"))
    
    tracks_to_plot = []
    
    if mr_grieves_path:
        tracks_to_plot.append((mr_grieves_path, "Mr. Grieves", '#1f77b4'))
    else:
        print("Error: Could not find 'Mr. Grieves'")
        
    if wimm_path:
        tracks_to_plot.append((wimm_path, "Where Is My Mind?", '#1f77b4'))
    else:
        print("Error: Could not find 'Where Is My Mind'")

    if brick_path:
        tracks_to_plot.append((brick_path, "Brick Is Red", '#1f77b4'))
    else:
        print("Error: Could not find 'Brick Is Red'")

    if tracks_to_plot:
        # Override output name for this custom run
        global output_path
        output_dir = os.path.join(base_dir, 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # We need to pass this inside the function or just hack it here by modifying the function
        # Actually simpler: Just run the plot function, it saves to 'case_study.png' by default
        # But we want 'custom_case_study.png'.
        # Let's just modify the save path inside plot_case_study temporarily or overwrite.
        # User just wants to SEE the plots. Overwriting is fine/easier, or I can rename it after.
        plot_case_study(tracks_to_plot)
        
        # Rename for clarity
        dst = os.path.join(output_dir, 'custom_pixies_study.png')
        src = os.path.join(output_dir, 'case_study.png')
        if os.path.exists(src):
            os.rename(src, dst)
            print(f"Renamed output to {dst}")
    else:
        print("Skipping plot due to missing files.")
