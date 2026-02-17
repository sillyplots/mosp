import librosa
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage
import os
import glob

def compute_novelty(y, sr):
    # 1. Beat Track
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    print(f"BPM: {tempo}")
    
    # 2. Compute Chroma
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # 3. Sync Chroma to Beats
    # This averages the chroma within each beat
    beat_chroma = librosa.util.sync(chroma, beat_frames, aggregate=np.median)
    
    # 4. Recurrence Matrix on Beat-Synced Chroma
    # stack memory might not be needed if we are already beat-synced and looking at structure?
    # Actually, stacking helps capture "sequences" of chords (phases)
    beat_chroma_stack = librosa.feature.stack_memory(beat_chroma, n_steps=4, delay=1)
    
    rec = librosa.segment.recurrence_matrix(beat_chroma_stack, mode='affinity', self=True)
    
    # 5. Novelty Curve via Kernel
    # Since we don't have get_checkerboard in this env (apparently), let's make a simple one
    # Or use scipy gaussian_filter style logic?
    # Standard Spectral Clustering method:
    # L = laplacian(rec)
    # vals, vecs = eig(L)
    # ...
    
    # Let's try the "Lag" method which is robust
    lag = librosa.segment.recurrence_to_lag(rec)
    
    # Apply a vertical gaussian filter to smooth?
    # The " novelty" is often just the correlation of the lag matrix with a checkerboard.
    # We can create a checkerboard manually.
    
    def create_checkerboard(width):
        # Create a 2D checkerboard kernel
        w = np.ones((width, width))
        mid = width // 2
        w[:mid, :mid] = -1
        w[mid:, mid:] = -1
        # Gaussian window it
        return w
        
    # Actually, let's keep it simple.
    # Librosa has `segment.subsegment` which fits a structure?
    # Or just use `agglomerative` on the BEAT SYNCED features?
    # This naturally snaps to beats.
    # And we can use a simpler heuristic for K or use a threshold?
    
    # Let's try Agglomerative on Beat-Synced features first.
    # It cleans up the noise significantly.
    
    k_adaptive = max(2, int(len(beat_frames) / 16)) # One segment every 16 beats (4 bars)?
    # Or every 32 beats (8 bars)?
    # Where Is My Mind is approx 100bpm. 4 bars ~ 9.6s.
    # Verse is usually 8 or 16 bars.
    
    print(f"Adaptive K (assuming segments ~ 16 bars = 64 beats): {len(beat_frames)//64}")
    k_adaptive = max(2, len(beat_frames)//64) # coarser
    
    bounds_frames = librosa.segment.agglomerative(beat_chroma_stack, k_adaptive)
    # bounds_frames are indices into beat_chroma, i.e., beat indices!
    
    bound_beats = beat_frames[bounds_frames]
    bound_times = librosa.frames_to_time(bound_beats, sr=sr)
    
    return bound_times.tolist()

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Find Where Is My Mind
    files = glob.glob(os.path.join(base_dir, "data/pixies/Surfer Rosa/*Where Is My Mind*.mp3"))
    if not files:
        print("File not found")
        return
        
    file_path = files[0]
    y, sr = librosa.load(file_path)
    
    print("--- Dynamic Segmentation (Beat Synced) ---")
    bounds = compute_novelty(y, sr)
    print(f"Bounds (s): {np.sort(bounds)}")
    
    # Compare to manual Ground Truth?
    # Intro ends around 0:13
    # Verse 1 starts 0:13
    
if __name__ == "__main__":
    main()
