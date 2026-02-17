import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import scipy.spatial
import scipy.ndimage
import scipy.signal
import os

def test_consistency(input_path):
    print(f"Testing consistency on {input_path}...")
    y, sr = librosa.load(input_path)
    
    # Beats
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    
    # Features
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    beat_chroma = librosa.util.sync(chroma, beat_frames, aggregate=np.median)
    
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)
    beat_rms = librosa.util.sync(librosa.amplitude_to_db(rms, ref=np.max), beat_frames, aggregate=np.mean)
    beat_rms_norm = (beat_rms - beat_rms.min()) / (beat_rms.max() - beat_rms.min())
    
    features = np.vstack([beat_chroma, beat_rms_norm * 5.0])
    features_stack = librosa.feature.stack_memory(features, n_steps=4, delay=1)
    
    # 1. Original Novelty
    w = 8
    dists = []
    for i in range(w, features.shape[1] - w):
        past = features[:, i-w:i].flatten()
        future = features[:, i:i+w].flatten()
        d = scipy.spatial.distance.euclidean(past, future)
        dists.append(d)
        
    novelty_raw = np.array(dists)
    novelty_raw = np.pad(novelty_raw, (w, w), mode='edge')
    novelty_raw = scipy.ndimage.gaussian_filter1d(novelty_raw, sigma=2)
    
    # 2. Consistent Novelty
    rec = librosa.segment.recurrence_matrix(features_stack, mode='affinity', self=True, width=3)
    rec_simple = librosa.segment.recurrence_matrix(features, mode='affinity', self=True, width=3)
    
    alpha = 0.5
    novelty_consistent = (novelty_raw + alpha * rec_simple.dot(novelty_raw)) / (1 + alpha * np.sum(rec_simple, axis=1))
    
    # Plot
    plt.figure(figsize=(14, 8))
    
    plt.subplot(3, 1, 1)
    librosa.display.specshow(rec_simple, x_axis='frames', y_axis='frames')
    plt.title('Recurrence Matrix (Self-Similarity)')
    
    plt.subplot(3, 1, 2)
    plt.plot(novelty_raw, label='Raw Novelty', color='gray', alpha=0.7)
    plt.plot(novelty_consistent, label='Consistent Novelty (Smoothed)', color='blue', linewidth=2)
    plt.legend()
    plt.title('Novelty Curves')
    
    plt.subplot(3, 1, 3)
    # Peaks
    peaks_raw, _ = scipy.signal.find_peaks((novelty_raw - novelty_raw.min())/novelty_raw.ptp(), prominence=0.04, distance=12)
    peaks_const, _ = scipy.signal.find_peaks((novelty_consistent - novelty_consistent.min())/novelty_consistent.ptp(), prominence=0.04, distance=12)
    
    plt.vlines(peaks_raw, 0, 1, color='gray', linestyle='--', label='Raw Peaks')
    plt.vlines(peaks_const, 0, 1, color='blue', linestyle='-', label='Consistent Peaks')
    plt.legend()
    plt.title('Detected Boundaries')
    
    plt.tight_layout()
    output_path = 'consistency_check.png'
    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")

if __name__ == "__main__":
    # Find a Pixies track
    base_dir = "/Users/charliethompson/Documents/mosp/posts/loud_quiet_loud/data/pixies"
    import glob
    files = glob.glob(os.path.join(base_dir, "**/*.mp3"), recursive=True)
    if files:
        test_consistency(files[0]) # Test on first file (Cecilia Ann or similar)
    else:
        print("No audio found")
