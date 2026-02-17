import librosa
import numpy as np
import os
import glob

def debug_track():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Find Where Is My Mind
    files = glob.glob(os.path.join(base_dir, "data/pixies/Surfer Rosa/*Where Is My Mind*.mp3"))
    if not files:
        print("File not found")
        return
    
    file_path = files[0]
    print(f"Testing {file_path}")
    
    y, sr = librosa.load(file_path)
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"Duration: {duration}")
    
    # Segmenting
    print("Computing Chroma...")
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_stack = librosa.feature.stack_memory(chroma, n_steps=10, delay=3)
    
    k_adaptive = max(2, int(duration / 25))
    print(f"Adaptive k: {k_adaptive}")
    
    print("Running Agglomerative Clustering...")
    try:
        bounds = librosa.segment.agglomerative(chroma_stack, k_adaptive)
        bound_times = librosa.frames_to_time(bounds, sr=sr)
        print(f"Success! Bounds: {bound_times}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_track()
