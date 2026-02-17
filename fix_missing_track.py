from posts.loud_quiet_loud.build_player_assets import build_assets, get_track_info
import os
import glob

def fix():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Find Where Is My Mind
    files = glob.glob(os.path.join(base_dir, "posts/loud_quiet_loud/data/pixies/Surfer Rosa/*Where Is My Mind*.mp3"))
    if not files:
        print("File not found")
        return
    
    file_path = files[0]
    print(f"Target: {file_path}")
    
    info = get_track_info(file_path)
    print(f"ID: {info['id']}")
    
    output_dir = os.path.join(base_dir, "posts/loud_quiet_loud/player/tracks", info['id'])
    print(f"Output Dir: {output_dir}")
    
    success = build_assets(file_path, output_dir)
    if success:
        print("Success!")
    else:
        print("Failed!")

if __name__ == "__main__":
    fix()
