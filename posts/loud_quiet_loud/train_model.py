import os
import json
import numpy as np
import librosa
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report
import glob
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def load_manifest(manifest_path):
    with open(manifest_path, 'r') as f:
        return json.load(f)

def get_audio_path(track_id, manifest, base_dir):
    # Find track in manifest
    track_info = next((t for t in manifest if t['id'] == track_id), None)
    if not track_info:
        return None
    
    # Construct searching logic similar to build_player_assets or just search recursively
    # The manifest doesn't have absolute paths anymore (we deleted them in build_player_assets to keep it clean)
    # But we know the structure: data/pixies/[Album]/[Track]
    # Let's search for the filename in data directory
    
    filename = track_info.get('title') # This might not be the filename
    # Actually build_player_assets saved 'filename' in data.json for the track.
    # But we don't have that here easily without looking into tracks/ID/data.json
    
    # Better approach: Look into `player/tracks/{id}/data.json` to get the audio filename
    # Then find that file in `data/`
    
    track_data_path = os.path.join(base_dir, "player", "tracks", track_id, "data.json")
    if not os.path.exists(track_data_path):
        return None
        
    with open(track_data_path, 'r') as f:
        data = json.load(f)
        audio_filename = data.get('filename') # e.g. "Pixies - Surfer Rosa - Where Is My Mind.mp3"
        
    # Search for this file in data dir
    search_pattern = os.path.join(base_dir, "data", "**", audio_filename)
    files = glob.glob(search_pattern, recursive=True)
    if files:
        return files[0]
        
    return None

def extract_features(y, sr):
    # Features to extract:
    # 1. Loudness (RMS) - Mean, Std, Max
    # 2. Chroma (Harmonic) - Mean, Std
    # 3. Spectral Contrast (Timbre) - Mean, Std
    # 4. Zero Crossing Rate (Percussive/Noise) - Mean
    
    features = {}
    
    # 1. Loudness
    rms = librosa.feature.rms(y=y)[0]
    features['rms_mean'] = np.mean(rms)
    features['rms_std'] = np.std(rms)
    features['rms_max'] = np.max(rms)
    
    # 2. Chroma
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    features['chroma_mean'] = np.mean(chroma)
    features['chroma_std'] = np.std(chroma)
    
    # 3. Spectral Contrast
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    features['contrast_mean'] = np.mean(contrast)
    features['contrast_std'] = np.std(contrast)
    
    # 4. Zero Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(y=y)[0]
    features['zcr_mean'] = np.mean(zcr)
    
    return np.array(list(features.values()))

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    golden_data_dir = os.path.join(base_dir, "player", "golden_data")
    manifest_path = os.path.join(base_dir, "player", "manifest.json")
    
    if not os.path.exists(golden_data_dir):
        print("No golden data found.")
        return

    manifest = load_manifest(manifest_path)
    
    X = []
    y = []
    
    print("Loading Golden Data...")
    
    json_files = glob.glob(os.path.join(golden_data_dir, "*.json"))
    
    feature_names = None
    
    for json_file in json_files:
        track_id = os.path.splitext(os.path.basename(json_file))[0]
        print(f"Processing Track ID: {track_id}")
        
        audio_path = get_audio_path(track_id, manifest, base_dir)
        if not audio_path:
            print(f"  Audio file not found for {track_id}")
            continue
            
        print(f"  Loading audio: {os.path.basename(audio_path)}")
        y_full, sr = librosa.load(audio_path)
        
        with open(json_file, 'r') as f:
            segments = json.load(f)
            
        for seg in segments:
            label = seg.get('label')
            if not label or label == "Other": 
                continue # Skip unlabeled or generic
                
            start_time = seg['start']
            end_time = seg['end']
            
            # Convert to samples
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            
            if end_sample <= start_sample:
                continue
                
            y_seg = y_full[start_sample:end_sample]
            
            # Skip very short segments (< 0.5s)
            if len(y_seg) < 0.5 * sr:
                continue
                
            feats = extract_features(y_seg, sr)
            X.append(feats)
            y.append(label)
            
    X = np.array(X)
    y = np.array(y)
    
    print(f"\nExtracted {len(X)} labeled segments.")
    print(f"Classes: {np.unique(y)}")
    
    if len(X) < 5:
        print("Not enough data to train.")
        return
        
    # Train Model
    print("\nTraining Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # Evaluate if we have enough data for CV
    if len(X) > 10:
        scores = cross_val_score(clf, X, y, cv=StratifiedKFold(n_splits=3))
        print(f"Cross-Validation Accuracy: {scores.mean():.2f} (+/- {scores.std() * 2:.2f})")
    
    clf.fit(X, y)
    
    # Save Model
    model_path = os.path.join(base_dir, "segment_classifier.pkl")
    joblib.dump(clf, model_path)
    print(f"\nModel saved to {model_path}")

if __name__ == "__main__":
    main()
