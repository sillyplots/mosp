import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

def find_file(pattern, search_root):
    search_path = os.path.join(search_root, "**", pattern)
    files = glob.glob(search_path, recursive=True)
    if files:
        return files[0]
    return None

def analyze_structure(file_path):
    print(f"Loading {file_path} ...")
    y, sr = librosa.load(file_path)

    print("Detecting beats...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, np.ndarray):
        tempo = tempo[0]
    print(f"Estimated BPM: {tempo:.2f}")
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    print("Computing chromagram and recurrence for segmentation...")
    # Compute chroma features
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # Enhance chroma with recurrence (structural components)
    chroma_stack = librosa.feature.stack_memory(chroma, n_steps=10, delay=3)
    
    # Recurrence matrix
    rec = librosa.segment.recurrence_matrix(chroma_stack, mode='affinity', self=True)
    
    # Enhancing diagonal
    rec_smooth = librosa.segment.path_enhance(rec, 15, window='hann', n_filters=7)
    
    # Structural components?
    # Let's try Laplacian segmentation (simple clustering of similar regions)
    # k is number of segments/types. Verse, Chorus, Bridge = 3? Maybe Intro/Outro = 5.
    print("Performing segmentation...")
    # Use agglomerative clustering constrained by time
    # We want to find *boundaries*
    bounds = librosa.segment.agglomerative(chroma_stack, 8) # 8 distinct segments?
    bound_times = librosa.frames_to_time(bounds, sr=sr)
    
    # Visualization
    plt.figure(figsize=(16, 8))
    
    # 1. Waveform and Beats
    plt.subplot(2, 1, 1)
    librosa.display.waveshow(y, sr=sr, alpha=0.6)
    plt.vlines(beat_times, -1, 1, color='g', alpha=0.3, linestyle='--', label='Beats')
    plt.vlines(bound_times, -1, 1, color='r', linewidth=2, linestyle='-', label='Segment Boundaries')
    plt.legend()
    plt.title(f"Waveform, Beats (BPM: {tempo:.1f}), and Structural Boundaries")
    
    # 2. Chromagram (just to see harmonic content)
    plt.subplot(2, 1, 2)
    librosa.display.specshow(chroma, y_axis='chroma', x_axis='time')
    plt.colorbar()
    plt.vlines(bound_times, 0, 12, color='w', linestyle='-', linewidth=2, alpha=0.8)
    plt.title('Chromagram with Segment Boundaries')
    
    plt.tight_layout()
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(output_dir, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, 'structure_analysis.png')
    plt.savefig(output_path)
    print(f"Saved analysis plot to {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try multiple naming conventions since we don't know exact filename in 'data/pixies'
    search_root = os.path.join(base_dir, "data/pixies")
    target_path = find_file("*Where Is My Mind*.mp3", search_root)
    
    if target_path:
        analyze_structure(target_path)
    else:
        print("Could not find 'Where Is My Mind' audio file.")
