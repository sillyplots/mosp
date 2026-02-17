import librosa
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import os
import glob

def analyze_track(file_path):
    print(f"\nAnalyzing: {os.path.basename(file_path)}")
    y, sr = librosa.load(file_path)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"Duration: {duration:.2f}s")
    
    # 1. Beat Tracking
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]
    print(f"BPM: {tempo:.1f}")
    
    # 2. Hybrid Feature Extraction (Beat Synced)
    
    # Harmony: Chroma
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    beat_chroma = librosa.util.sync(chroma, beat_frames, aggregate=np.median)
    
    # Loudness: RMS
    # Calc RMS on valid frames then sync
    hop_length = 512
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_length)
    # Sync RMS to beats (mean energy per beat)
    # Note: librosa.util.sync expects (n_features, n_time), RMS is (1, n_time)
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    beat_rms = librosa.util.sync(rms_db, beat_frames, aggregate=np.mean)
    
    # Normalize features to combine them
    # Chroma is 0-1 usually. RMS_dB is -80 to 0. Normalize RMS to 0-1
    beat_rms_norm = (beat_rms - beat_rms.min()) / (beat_rms.max() - beat_rms.min())
    
    # Hybrid Stack (Weight loudness x5)
    # User requested MORE sensitivity to "Loud-Quiet-Loud"
    loudness_weight = 5.0
    features = np.vstack([beat_chroma, beat_rms_norm * loudness_weight])
        
    # Stack Memory (1 bar / 4 beats context)
    features_stack = librosa.feature.stack_memory(features, n_steps=4, delay=1)
    
    # Rolling Euclidean Distance Novelty
    w = 8 # Lookahead/behind 2 bars (8 beats)
    dists = []
    for i in range(w, features.shape[1] - w):
        past = features[:, i-w:i].flatten()
        future = features[:, i:i+w].flatten()
        
        # Euclidean distance to capture magnitude (Loudness) shifts better
        d = scipy.spatial.distance.euclidean(past, future)
        dists.append(d)
        
    novelty_curve = np.array(dists)
    novelty_curve = np.pad(novelty_curve, (w, w), mode='edge')
    
    # Smooth
    novelty_curve = scipy.ndimage.gaussian_filter1d(novelty_curve, sigma=2)
    
    # Normalize Novelty
    novelty_curve = (novelty_curve - novelty_curve.min()) / (novelty_curve.max() - novelty_curve.min())
    
    print(f"Novelty Stats - Mean: {novelty_curve.mean():.3f}, Std: {novelty_curve.std():.3f}, Max: {novelty_curve.max():.3f}")
    
    # 6. Peak Picking (Global Context)
    # Debuging with very low prominence to find the peak user wants
    prominence = 0.01
    min_dist_beats = 4
    
    peaks, props = scipy.signal.find_peaks(novelty_curve, prominence=prominence, distance=min_dist_beats) 
    
    print(f"Found {len(peaks)} boundaries (Pre-filter).")
    
    bound_times = librosa.frames_to_time(beat_frames[peaks], sr=sr)
    print(f"Boundaries (s): {np.sort(bound_times)}")
    
    # Debug: Print peaks with prominences
    print("Peak Prominences:")
    for p, prop in zip(peaks, props['prominences']):
            t = librosa.frames_to_time(beat_frames[p], sr=sr)
            print(f"  Time: {t:.2f}s, Prominence: {prop:.3f}")
    
    # Add Start/End
    all_bounds = np.concatenate(([0.0], bound_times, [duration]))
    print(f"Segments: {len(all_bounds)-1}")
    return all_bounds

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test on Where Is My Mind
    files = glob.glob(os.path.join(base_dir, "data/pixies/Surfer Rosa/*Where Is My Mind*.mp3"))
    if files:
        analyze_track(files[0])
        
    # Test on Tame (Very dynamic)
    files_tame = glob.glob(os.path.join(base_dir, "data/pixies/*/Pixies*Tame*.mp3"))
    if files_tame:
        analyze_track(files_tame[0])

if __name__ == "__main__":
    main()
