import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import scipy.spatial
import scipy.ndimage
import scipy.signal
import os
import glob

def test_jumps(file_pattern):
    base_dir = "/Users/charliethompson/Documents/mosp/posts/loud_quiet_loud/data/pixies"
    files = glob.glob(os.path.join(base_dir, "**", file_pattern), recursive=True)
    if not files:
        print(f"Could not find file matching {file_pattern}")
        return

    input_path = files[0]
    print(f"Testing jumps on {input_path}...")
    y, sr = librosa.load(input_path)
    
    # Beats
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Features
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    beat_chroma = librosa.util.sync(chroma, beat_frames, aggregate=np.median)
    
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)
    beat_rms = librosa.util.sync(librosa.amplitude_to_db(rms, ref=np.max), beat_frames, aggregate=np.mean)
    beat_rms_norm = (beat_rms - beat_rms.min()) / (beat_rms.max() - beat_rms.min())
    
    features = np.vstack([beat_chroma, beat_rms_norm * 5.0]) # 5.0 is loudness weight
    features_stack = librosa.feature.stack_memory(features, n_steps=4, delay=1)
    
    # 1. Original Novelty (Smoothed & Structurally Consistent)
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
    
    # Recurrence consistency
    rec = librosa.segment.recurrence_matrix(features, mode='affinity', self=True, width=3)
    alpha = 0.5
    novelty_struct = (novelty_raw + alpha * rec.dot(novelty_raw)) / (1 + alpha * np.sum(rec, axis=1))
    
    # 2. Add Jumps
    # beat_rms is (1, N)
    loudness_diff = np.diff(beat_rms, axis=1, prepend=beat_rms[:, :1])
    jump_signal = np.abs(loudness_diff)[0]
    
    novelty_final = novelty_struct + (jump_signal * 0.5)
    super_jumps = jump_signal > 10.0
    novelty_final[super_jumps] += 1.0
    
    # Plot
    plt.figure(figsize=(14, 10))
    
    plt.subplot(4, 1, 1)
    librosa.display.waveshow(y, sr=sr, alpha=0.5)
    plt.title(f'Waveform: {os.path.basename(input_path)}')
    
    plt.subplot(4, 1, 2)
    plt.plot(beat_rms, label='Loudness (dB)', color='orange')
    plt.plot(jump_signal * 10, label='Jump Signal (scaled)', color='red', alpha=0.5) # Scale for visibility
    plt.legend()
    plt.title('Loudness & Jumps')
    
    plt.subplot(4, 1, 3)
    plt.plot(novelty_struct, label='Novelty (Struct Only)', color='gray', alpha=0.5)
    plt.plot(novelty_final, label='Novelty (Final)', color='blue')
    plt.legend()
    plt.title('Novelty Curve Impact')
    
    plt.subplot(4, 1, 4)
    # Peaks
    peaks, _ = scipy.signal.find_peaks((novelty_final - novelty_final.min())/novelty_final.ptp(), prominence=0.04, distance=12)
    peak_times = beat_times[peaks]
    
    librosa.display.specshow(chroma, x_axis='time', y_axis='chroma')
    plt.vlines(peak_times, 0, 12, color='white', linewidth=2, linestyle='--')
    plt.title('Final Segments')
    
    plt.tight_layout()
    clean_name = os.path.basename(input_path).replace('.mp3', '').replace(' ', '_')
    output_path = f'jump_check_{clean_name}.png'
    plt.savefig(output_path)
    print(f"Saved plot to {output_path}")

if __name__ == "__main__":
    test_jumps("*Where Is My Mind*.mp3")
    test_jumps("*Tame*.mp3")
