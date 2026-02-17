import librosa
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from sklearn.tree import DecisionTreeRegressor

# --- Helper Functions (copied from plot_case_study.py) ---
def filename_from_path(path):
    return os.path.basename(path).replace('.mp3', '')

def analyze_loudness(file_path):
    print(f"Loading {file_path}...")
    y, sr = librosa.load(file_path, mono=True)
    hop_length = 512
    frame_length = 2048
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    loudness_db = librosa.amplitude_to_db(rms, ref=np.max)
    times = librosa.times_like(loudness_db, sr=sr, hop_length=hop_length)

    # Simple Smart Trim (Median - 12dB threshold)
    active_mask = loudness_db > -60
    if np.sum(active_mask) > 0:
        median_vol = np.median(loudness_db[active_mask])
    else:
        median_vol = -40 
    threshold = median_vol - 12.0 
    window = int(2.0 * sr / hop_length) 
    above_thresh = loudness_db > threshold
    if np.any(above_thresh):
        start_idx = np.argmax(above_thresh)
        end_idx = len(loudness_db) - np.argmax(above_thresh[::-1]) - 1
        buffer_frames = int(0.5 * sr / hop_length)
        start_idx = max(0, start_idx - buffer_frames)
        end_idx = min(len(loudness_db), end_idx + buffer_frames)
        if end_idx > start_idx + window: 
            loudness_db = loudness_db[start_idx:end_idx]
            times = times[start_idx:end_idx] - times[start_idx]
            
    return times, loudness_db, filename_from_path(file_path)

def fit_piecewise_constant(times, loudness_db, max_segments, min_samples_leaf):
    X = times.reshape(-1, 1)
    y = loudness_db
    tree = DecisionTreeRegressor(max_leaf_nodes=max_segments, min_samples_leaf=min_samples_leaf)
    tree.fit(X, y)
    return tree.predict(X)

# --- Tuning Script ---
def run_tuning():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tame_path = glob.glob(os.path.join(base_dir, "data/pixies/**", "*Tame.mp3"), recursive=True)[0]
    
    times, db, name = analyze_loudness(tame_path)
    # Smooth before fitting
    window_size = 50
    smoothed = np.convolve(db, np.ones(window_size)/window_size, mode='valid')
    time_axis = times[:len(smoothed)]

    # Parameters to test
    # min_samples_leaf = frames. 43 frames ~ 1 sec.
    test_params = [
        (10, 30), # ~0.2s min (Too noisy?)
        (20, 30), # ~0.45s min (Current)
        (43, 24), # ~1.0s min
        (86, 16), # ~2.0s min (Very strict)
    ]
    
    plt.figure(figsize=(15, 12))
    
    for i, (min_leaf, max_seg) in enumerate(test_params):
        ax = plt.subplot(len(test_params), 1, i+1)
        
        steps = fit_piecewise_constant(time_axis, smoothed, max_segments=max_seg, min_samples_leaf=min_leaf)
        
        # Count Transitions > 3dB
        diffs = np.diff(steps)
        trans_idxs = np.where(np.abs(diffs) > 3.0)[0]
        count = len(trans_idxs)
        
        duration_sec = min_leaf * (512/22050)
        
        ax.fill_between(time_axis, -100, smoothed, color='#1f77b4', alpha=0.3)
        ax.plot(time_axis, steps, color='black', linewidth=2)
        
        for idx in trans_idxs:
             ax.vlines(time_axis[idx], -40, 0, color='red', linestyle=':', alpha=0.8)

        ax.set_ylim(-40, 0)
        ax.set_title(f"Min Duration: ~{duration_sec:.2f}s ({min_leaf} frames) | Max Seg: {max_seg} | Transitions: {count}")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = os.path.join(base_dir, "output", "tuning_tame.png")
    plt.savefig(out_path)
    print(f"Saved tuning plot: {out_path}")

if __name__ == "__main__":
    run_tuning()
