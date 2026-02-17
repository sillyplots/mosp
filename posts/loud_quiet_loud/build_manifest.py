import os
import json
import glob

def build_manifest():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    player_dir = os.path.join(base_dir, "player")
    tracks_dir = os.path.join(player_dir, "tracks")
    
    manifest = []
    
    track_dirs = glob.glob(os.path.join(tracks_dir, "*"))
    print(f"Found {len(track_dirs)} processed tracks.")
    
    for track_dir in track_dirs:
        data_path = os.path.join(track_dir, "data.json")
        if not os.path.exists(data_path):
            continue
            
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
                
            # Reconstruct info from data or assume ID
            track_id = os.path.basename(track_dir)
            
            # Heuristic for Artist/Title/Album from filename if possible, 
            # OR we can just store the metadata IN data.json during build.
            # But currently data.json only has filename.
            
            # Let's re-parse filename
            filename = data['filename']
            # Logic from build_player_assets.py
            if "Bossanova" in filename or "Surfer Rosa" in filename or "Doolitle" in filename or "Trompe" in filename or "Pixies" in filename:
                artist = "Pixies"
                # Try to extract Album
                if "Bossanova" in filename: album = "Bossanova"
                elif "Surfer Rosa" in filename: album = "Surfer Rosa"
                elif "Doolitle" in filename: album = "Doolittle"
                elif "Trompe" in filename: album = "Trompe le Monde"
                else: album = "Unknown"
                
                # Cleanup Title
                title = filename.replace('.mp3', '')
                if " - " in title:
                     title = title.split(" - ")[-1]
            else:
                # Contorl
                parts = filename.replace('.mp3', '').split('_')
                if len(parts) > 1:
                    artist = parts[0]
                    title = " ".join(parts[1:])
                else:
                    artist = "Unknown"
                    title = filename
                album = "Control"

            manifest.append({
                "id": track_id,
                "artist": artist,
                "title": title,
                "album": album
            })
            
        except Exception as e:
            print(f"Error reading {track_dir}: {e}")

    # Sort
    manifest.sort(key=lambda x: (x['artist'], x['album'], x['title']))
    
    manifest_path = os.path.join(player_dir, "manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Manifest rebuilt with {len(manifest)} tracks.")

if __name__ == "__main__":
    build_manifest()
