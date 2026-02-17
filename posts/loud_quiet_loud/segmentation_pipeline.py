import librosa
import numpy as np
import ruptures as rpt
import scipy.ndimage
import scipy.ndimage
from sklearn.preprocessing import StandardScaler

class HybridSegmenter:
    """
    Combines Harmonic Structure (Recurrence/MSAF-style) and 
    Dynamic Structure (Change Point Detection) to segment audio.
    """
    def __init__(self, sr=22050, hop_length=512):
        self.sr = sr
        self.hop_length = hop_length

    def compute_harmonic_boundaries(self, y):
        """
        Detects boundaries based on harmonic content (Chroma).
        Uses a simplified recurrence matrix + lag checkerboard approach (Foote's method).
        """
        # 1. Feature Extraction (Chroma)
        # Use larger hop_length for structure (approx 10Hz is enough) to save speed
        chroma = librosa.feature.chroma_cqt(y=y, sr=self.sr, hop_length=2048)
        
        # 2. Recurrence Matrix
        # Stack memory to capture texture
        chroma_stack = librosa.feature.stack_memory(chroma, n_steps=10, delay=3)
        rec = librosa.segment.recurrence_matrix(chroma_stack, mode='affinity', self=True, width=3)

        # 3. Novelty Curve (kernel-based)
        # Using a checkerboard kernel to find transitions
        novelty = librosa.segment.recurrence_to_lag(rec, pad=True, axis=-1)
        # Scan for peaks in novelty
        # We can use spectral clustering or peak picking
        # For robustness, let's use librosa's agglomerative clustering on the structure
        # which is often cleaner.
        
        # Agglomerative clustering on the chroma itself
        # Divide track into segments. We expect a segment roughly every 15s?
        duration = librosa.get_duration(y=y, sr=self.sr)
        k = max(2, int(duration / 15)) 
        
        boundaries_frames = librosa.segment.agglomerative(chroma_stack, k)
        return librosa.frames_to_time(boundaries_frames, sr=self.sr, hop_length=2048)

    def compute_dynamic_boundaries(self, y, min_size_seconds=5.0, pen=25.0):
        """
        Detects boundaries based on loudness changes (RMS).
        Uses Ruptures (Pelt or Window) for change point detection.
        """
        # 1. Compute Envelope via RMS
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=self.hop_length)[0]
        loudness_db = librosa.amplitude_to_db(rms, ref=np.max)
        
        # 2. Prepare for Ruptures
        # Standardize the signal so 'pen' is consistent
        scaler = StandardScaler()
        signal = scaler.fit_transform(loudness_db.reshape(-1, 1))
        
        # 3. Change Point Detection
        # Pelt (Pruned Exact Linear Time) is good for unknown number of change points
        # Model "l2" (least squares) works well for mean shifts
        # Min size: 2 seconds * (sr/hop) frames
        min_size_frames = int(min_size_seconds * self.sr / self.hop_length)
        
        # Pelt might overshoot if penalty is low.
        # KernelCPD is also an option.
        algo = rpt.Pelt(model="l2", min_size=min_size_frames, jump=5).fit(signal)
        try:
            result_frames = algo.predict(pen=pen)
        except Exception:
             # Fallback if pen is too high
            result_frames = [len(signal)]

        
        # Convert to time
        # Remove the last point which is just end of signal
        boundaries_frames = np.array(result_frames[:-1])
        return librosa.frames_to_time(boundaries_frames, sr=self.sr, hop_length=self.hop_length)

    def fuse_boundaries(self, boundaries, threshold=1.0):
        """
        Merges boundaries that are close to each other.
        """
        if len(boundaries) == 0:
            return np.array([])
            
        boundaries = np.sort(boundaries)
        fused = [boundaries[0]]
        
        for b in boundaries[1:]:
            if b - fused[-1] > threshold:
                fused.append(b)
            # If close, we could average them, but keeping the first (or largest) is often fine.
            # Here we just keep the earlier one (simple debounce)
            
        return np.array(fused)

    def segment(self, file_path):
        """
        Main pipeline.
        """
        y, sr = librosa.load(file_path, sr=self.sr)
        
        # 1. Structural (Harmonic)
        # Often too granular, let's trust Dynamic more for this specific task
        harmonic_bounds = self.compute_harmonic_boundaries(y)
        
        # 2. Dynamic (Loudness)
        # AGGRESSIVE TUNING: pen=25.0, min_size=5.0s
        dynamic_bounds = self.compute_dynamic_boundaries(y, min_size_seconds=5.0, pen=25.0)
        
        # 3. Fusion
        all_bounds = np.concatenate([harmonic_bounds, dynamic_bounds])
        
        # 4. Debounce/Fuse
        # Merge anything within 3 seconds? 2 seconds?
        # User wants < 10 transitions. 
        fused_bounds = self.fuse_boundaries(all_bounds, threshold=2.0)

        return {
            'harmonic': harmonic_bounds.tolist(),
            'dynamic': dynamic_bounds.tolist(),
            'combined': fused_bounds.tolist()
        }

if __name__ == "__main__":
    # Test on a file if run directly
    import sys
    if len(sys.argv) > 1:
        f = sys.argv[1]
        seg = HybridSegmenter()
        res = seg.segment(f)
        print("Harmonic:", res['harmonic'])
        print("Dynamic:", res['dynamic'])
