import librosa
import numpy as np
import scipy.signal
import scipy.spatial
import scipy.ndimage
import os
import glob
import pandas as pd

def inspect_track(file_pattern):
    base_dir = "/Users/charliethompson/Documents/mosp/posts/loud_quiet_loud/data/pixies"
    files = glob.glob(os.path.join(base_dir, "**", file_pattern), recursive=True)
    if not files:
        print(f"File not found: {file_pattern}")
        return
        
    path = files[0]
    print(f"--- Analyzing {os.path.basename(path)} ---")
    
    y, sr = librosa.load(path)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Recalculate features exactly as in build_player_assets
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    beat_chroma = librosa.util.sync(chroma, beat_frames, aggregate=np.median)
    
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)
    beat_rms = librosa.util.sync(librosa.amplitude_to_db(rms, ref=np.max), beat_frames, aggregate=np.mean)
    beat_rms_norm = (beat_rms - beat_rms.min()) / (beat_rms.max() - beat_rms.min())
    
    features = np.vstack([beat_chroma, beat_rms_norm * 5.0])
    
    # Novelty
    w = 8
    dists = []
    for i in range(w, features.shape[1] - w):
        past = features[:, i-w:i].flatten()
        future = features[:, i:i+w].flatten()
        d = scipy.spatial.distance.euclidean(past, future)
        dists.append(d)
        
    novelty_curve = np.array(dists)
    novelty_curve = np.pad(novelty_curve, (w, w), mode='edge')
    novelty_curve = scipy.ndimage.gaussian_filter1d(novelty_curve, sigma=2)
    
    # Recurrence
    rec_simple = librosa.segment.recurrence_matrix(features, mode='affinity', self=True, width=3)
    alpha = 0.5
    novelty_struct = (novelty_curve + alpha * rec_simple.dot(novelty_curve)) / (1 + alpha * np.sum(rec_simple, axis=1))
    
    # Jump Logic
    loudness_diff = np.diff(beat_rms, axis=1, prepend=beat_rms[:, :1])
    jump_signal = np.abs(loudness_diff)[0]
    
    # Final Curve construction
    novelty_final = novelty_struct + (jump_signal * 0.5)
    super_jumps = jump_signal > 10.0
    novelty_final[super_jumps] += 1.0
    
    # Peaks
    if novelty_final.max() != novelty_final.min():
        norm_novelty = (novelty_final - novelty_final.min()) / (novelty_final.max() - novelty_final.min())
    else:
        norm_novelty = novelty_final
        
    peaks, _ = scipy.signal.find_peaks(norm_novelty, prominence=0.04, distance=12)
    peak_times = beat_times[peaks]
    
    # Print data around potential cuts (look for large jumps)
    # We want to see where jump_signal is high, and if a peak was found there.
    
    # Debug shapes
    print(f"Shapes -> beat_times: {beat_times.shape}, beat_rms: {beat_rms.shape}, novelty: {novelty_final.shape}")
    
    # Truncate to min length
    min_len = min(len(beat_times), beat_rms.shape[1], len(novelty_final))
    beat_times = beat_times[:min_len]
    beat_rms_val = beat_rms[0, :min_len]
    jump_signal = jump_signal[:min_len]
    novelty_final = novelty_final[:min_len]
    
    # Re-calc peaks indices to ensure they are valid
    is_peak = [False] * min_len
    for p in peaks:
        if p < min_len:
            is_peak[p] = True
    
    df = pd.DataFrame({
        'time': beat_times,
        'rms_db': beat_rms_val,
        'jump_db': jump_signal,
        'novelty': novelty_final,
        'is_peak': is_peak
    })
    
    # Filter for significant jumps (> 3dB)
    significant_jumps = df[df['jump_db'] > 3.0]
    print("\nSignificant Loudness Jumps (>3dB):")
    print(significant_jumps[['time', 'rms_db', 'jump_db', 'novelty', 'is_peak']].head(20))
    
    # Check specifically if super jumps (>10dB) were caught
    print("\nSuper Jumps (>10dB):")
    print(df[df['jump_db'] > 10.0][['time', 'rms_db', 'jump_db', 'novelty', 'is_peak']])

if __name__ == "__main__":
    inspect_track("*Where Is My Mind*.mp3")
    inspect_track("*Tame*.mp3")
