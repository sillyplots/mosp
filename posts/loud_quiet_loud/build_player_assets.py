import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import json
import shutil
import hashlib
import scipy.spatial
import scipy.ndimage
import scipy.signal

def build_assets(input_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Processing {input_path}...")
    
    # 1. Copy Audio
    audio_filename = "track.mp3"
    dest_audio_path = os.path.join(output_dir, audio_filename)
    shutil.copyfile(input_path, dest_audio_path)
    # print(f"Copied audio to {dest_audio_path}")

    # 2. Analyze
    try:
        y, sr = librosa.load(input_path)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # print("Detecting beats...")
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        if isinstance(tempo, np.ndarray):
            tempo = tempo[0]
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
        # print("Segmenting...")
        
        # 3. Structural Segmentation (Agglomerative Clustering - "Research" Logic)
        # Harmony: Chroma
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        beat_chroma = librosa.util.sync(chroma, beat_frames, aggregate=np.median)
        
        # Loudness: RMS
        hop_length = 512
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_length)
        beat_rms = librosa.util.sync(librosa.amplitude_to_db(rms, ref=np.max), beat_frames, aggregate=np.mean)
        # Normalize RMS (0-1)
        if beat_rms.max() != beat_rms.min():
           beat_rms_norm = (beat_rms - beat_rms.min()) / (beat_rms.max() - beat_rms.min())
        else:
           beat_rms_norm = np.zeros_like(beat_rms)

        # Hybrid Stack (Weight loudness x5)
        loudness_weight = 5.0
        features = np.vstack([beat_chroma, beat_rms_norm * loudness_weight])
        
        # Stack Memory (1 bar / 4 beats context)
        features_stack = librosa.feature.stack_memory(features, n_steps=4, delay=1)
        
        # Agglomerative Clustering
        # Target ~1 segment every 16 bars (64 beats)
        # This produces ~10 segments for a typical 4min song
        k_adaptive = max(2, len(beat_frames) // 64)
        
        # Bound frames are indices into the BEAT frames (beat indices)
        bounds_beat_indices = librosa.segment.agglomerative(features_stack, k_adaptive)
        
        # Convert to time
        bound_times = librosa.frames_to_time(beat_frames[bounds_beat_indices], sr=sr)
        bound_times = np.sort(bound_times)
        
        # --- NEW: Check for Golden Data first ---
        # Track ID is the basename of the output directory
        track_id = os.path.basename(output_dir)
        golden_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "player", "golden_data", f"{track_id}.json")
        
        segments_data = []
        bound_times_final = []

        if os.path.exists(golden_path):
            print(f"  Using Golden Data from {golden_path}")
            with open(golden_path, 'r') as f:
                golden_data = json.load(f)
                
                # Check format: List of Dicts (Old) vs List of Floats (New)
                if isinstance(golden_data, list) and len(golden_data) > 0:
                    if isinstance(golden_data[0], dict):
                        # Old format: [{'start': 0, 'end': 10, 'label': 'Intro'}, ...]
                        segments_data = golden_data
                        
                        boundaries = set([0.0, duration])
                        for seg in golden_data:
                            boundaries.add(seg['start'])
                            boundaries.add(seg['end'])
                        bound_times_final = sorted(list(boundaries))
                        
                    elif isinstance(golden_data[0], (int, float)):
                        # New format: [0.0, 15.5, 45.1, ...] (Breakpoints)
                        # We need to construct segments from these points
                        breakpoints = sorted(golden_data)
                        
                        # Ensure 0 and duration are in there for proper segment construction
                        # If the user just gave internal points, we add start/end
                        unique_points = sorted(list(set([0.0] + breakpoints + [duration])))
                        bound_times_final = [t for t in unique_points if t > 0.01 and t < duration - 0.01]
                        
                        # Construct labeled segments
                        segments_data = []
                        for i in range(len(unique_points) - 1):
                            segments_data.append({
                                "start": unique_points[i],
                                "end": unique_points[i+1],
                                "label": "Golden"
                            })
                else:
                     # Handle empty list case
                     bound_times_final = []
                     segments_data = []

        else:
            # Fallback to Automated Prediction
            
            # Helper to extract features (MUST match train_model.py)
            def extract_segment_features(y_seg, sr):
                feats = {}
                rms_seg = librosa.feature.rms(y=y_seg)[0]
                if len(rms_seg) == 0: return np.zeros(8) # Fallback for empty
                
                feats['rms_mean'] = np.mean(rms_seg)
                feats['rms_std'] = np.std(rms_seg)
                feats['rms_max'] = np.max(rms_seg)
                
                chroma_seg = librosa.feature.chroma_cqt(y=y_seg, sr=sr)
                if chroma_seg.shape[1] == 0: return np.zeros(8)
                
                feats['chroma_mean'] = np.mean(chroma_seg)
                feats['chroma_std'] = np.std(chroma_seg)
                
                contrast_seg = librosa.feature.spectral_contrast(y=y_seg, sr=sr)
                feats['contrast_mean'] = np.mean(contrast_seg)
                feats['contrast_std'] = np.std(contrast_seg)
                
                zcr_seg = librosa.feature.zero_crossing_rate(y=y_seg)[0]
                feats['zcr_mean'] = np.mean(zcr_seg)
                
                return np.array(list(feats.values()))

            # Load Model (Global or load once)
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "segment_classifier.pkl")
            clf = None
            if os.path.exists(model_path):
                try:
                    import joblib
                    clf = joblib.load(model_path)
                except:
                    print("Failed to load classifier.")
            
            # Process each segment
            # We need start/end times. bound_times are just boundaries.
            # Add 0.0 and duration to bounds to get full segments
            bound_times_final = bound_times.tolist() # Keep original detected boundaries
            all_bounds = np.unique(np.concatenate(([0.0], bound_times, [duration])))
            
            for k in range(len(all_bounds) - 1):
                start = all_bounds[k]
                end = all_bounds[k+1]
                
                label = "Unknown"
                if clf:
                    # Extract Audio
                    start_sample = int(start * sr)
                    end_sample = int(end * sr)
                    if end_sample > start_sample:
                        y_seg = y[start_sample:end_sample]
                        if len(y_seg) > 0.5 * sr:
                            feats = extract_segment_features(y_seg, sr)
                            # Reshape for prediction (1, -1)
                            if feats.shape[0] == 8: # Ensure correct shape
                                 label = clf.predict([feats])[0]
                
                segments_data.append({
                    "start": start,
                    "end": end,
                    "label": label
                })

        # 3. Export Data JSON
        data = {
            "filename": os.path.basename(input_path),
            "duration": duration,
            "bpm": float(tempo),
            "beats": beat_times.tolist(),
            "segments": bound_times_final,
            "labeled_segments": segments_data, # New detailed list
            "audio_url": audio_filename
        }

        
        json_path = os.path.join(output_dir, "data.json")
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        # print(f"Saved metadata to {json_path}")

        # 4. Generate Clean Chromagram Image
        # print("Generating chromagram image...")
        plt.figure(figsize=(10, 4))
        librosa.display.specshow(chroma, y_axis='chroma', x_axis='time', cmap='coolwarm')
        plt.axis('off')
        plt.gca().set_position([0, 0, 1, 1])
        img_path = os.path.join(output_dir, "chromagram.png")
        plt.savefig(img_path, bbox_inches=0, pad_inches=0)
        plt.close()

        # 5. Generate Loudness Chart
        # print("Generating loudness image...")
        hop_length = 512
        frame_length = 2048
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        loudness_db = librosa.amplitude_to_db(rms, ref=np.max)
        times = librosa.times_like(loudness_db, sr=sr, hop_length=hop_length)
        
        plt.figure(figsize=(10, 4))
        plt.fill_between(times, -80, loudness_db, color='#d62728', alpha=0.6)
        plt.plot(times, loudness_db, color='#ff7f0e', linewidth=1.5)
        plt.xlim(0, duration)
        plt.ylim(-60, 0)
        plt.axis('off')
        plt.gca().set_position([0, 0, 1, 1])
        loudness_path = os.path.join(output_dir, "loudness.png")
        plt.savefig(loudness_path, bbox_inches=0, pad_inches=0, transparent=True)
        plt.close()
        
        return True
    except Exception as e:
        print(f"FAILED to process {input_path}: {e}")
        return False

def get_track_info(path):
    filename = os.path.basename(path)
    # Simple heuristics based on our folder structure
    # Pixies: data/pixies/<Album>/<Song>.mp3
    # Control: data/control/<Artist_Song>.mp3
    
    parts = path.split(os.sep)
    
    if "pixies" in parts:
        artist = "Pixies"
        title = filename.replace('.mp3', '')
        # Try to clean up "Pixies - " prefix if present
        title = title.replace("Pixies - ", "")
        # Remove album info if in filename
        if " - " in title:
             # Assume format "Album - TrackNum - Title" or similar
             # Usually standardizing manually is safer, but let's try
             title = title.split(" - ")[-1]
        
        # Album is parent dir
        try:
            album_idx = parts.index("pixies") + 1
            if album_idx < len(parts) - 1:
                album = parts[album_idx]
            else:
                album = "Unknown Album"
        except:
            album = "Unknown"
            
    elif "control" in parts:
        # data/control/Nirvana_Smells_Like_Teen_Spirit.mp3
        name_parts = filename.replace('.mp3', '').split('_')
        artist = name_parts[0]
        title = " ".join(name_parts[1:])
        album = "Control Track"
    else:
        artist = "Unknown"
        title = filename
        album = "Unknown"
        
    # Create a stable ID
    track_id = hashlib.md5(f"{artist}_{title}".encode('utf-8')).hexdigest()[:10]
    
    return {
        "id": track_id,
        "artist": artist,
        "title": title,
        "album": album,
        "path": path
    }

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    player_dir = os.path.join(base_dir, "player")
    tracks_dir = os.path.join(player_dir, "tracks")
    
    if not os.path.exists(tracks_dir):
        os.makedirs(tracks_dir)

    all_files = glob.glob(os.path.join(data_dir, "**/*.mp3"), recursive=True)
    
    manifest = []
    
    print(f"Found {len(all_files)} audio files. Starting batch processing...")
    
    for i, file_path in enumerate(all_files):
        info = get_track_info(file_path)
        track_out_dir = os.path.join(tracks_dir, info['id'])
        
        # Check if already done (skip for speed if re-running)
        # Check if already done (skip for speed if re-running), unless golden data is newer
        json_path = os.path.join(track_out_dir, "data.json")
        golden_path = os.path.join(player_dir, "golden_data", f"{info['id']}.json")
        
        should_process = True
        if os.path.exists(json_path):
            json_mtime = os.path.getmtime(json_path)
            golden_mtime = os.path.getmtime(golden_path) if os.path.exists(golden_path) else 0
            
            if golden_mtime > json_mtime:
                 print(f"[{i+1}/{len(all_files)}] Reprocessing {info['artist']} - {info['title']} (Golden Data Updated)")
            else:
                 print(f"[{i+1}/{len(all_files)}] Skipping {info['artist']} - {info['title']} (Cached)")
                 del info['path'] # Don't put absolute path in manifest
                 manifest.append(info)
                 continue
            
        print(f"[{i+1}/{len(all_files)}] Processing {info['artist']} - {info['title']}...")
        success = build_assets(file_path, track_out_dir)
        
        if success:
            del info['path']
            manifest.append(info)
            
    # Sort manifest by Artist, then Album, then Title
    manifest.sort(key=lambda x: (x['artist'], x['album'], x['title']))
    
    manifest_path = os.path.join(player_dir, "manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"\nBatch processing complete! Manifest saved to {manifest_path}")
