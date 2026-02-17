import yt_dlp
import os
import sys

def download_audio_url(url, output_path):
    """
    Downloads audio from a direct YouTube URL.
    """
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Configure yt-dlp to download directly to the specified path
    # We use a specific Output Template so it names the file exactly as we want
    # Note: yt-dlp might append the extension, so we handle that.
    
    # Base options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path + '.%(ext)s', 
        'noplaylist': True,
        'quiet': False,
    }

    # Check for manual cookies.txt
    cookies_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
    if os.path.exists(cookies_path):
        print(f"Using cookies from: {cookies_path}")
        ydl_opts['cookiefile'] = cookies_path

    print(f"Downloading {url} -> {output_path}...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Success!")
    except Exception as e:
        print(f"\n❌ Error downloading {url}: {e}")

if __name__ == "__main__":
    # URLs found by Browser Agent
    video_urls = {
      # Target: Pixies
      "Pixies_Debaser": "https://www.youtube.com/watch?v=PVyS9JwtFoQ",
      "Pixies_Tame": "https://www.youtube.com/watch?v=2Yn3Ls5jZ4g",
      "Pixies_Gigantic": "https://www.youtube.com/watch?v=xJncHEZ3URs",
      "Pixies_Where_Is_My_Mind": "https://www.youtube.com/watch?v=OJ62RzJkYUo",
      
      # Controls
      "Nirvana_Smells_Like_Teen_Spirit": "https://www.youtube.com/watch?v=hTWKbfoikeg",
      "Sonic_Youth_Kool_Thing": "https://www.youtube.com/watch?v=SDTSUwIZdMk",
      "Pavement_Cut_Your_Hair": "https://www.youtube.com/watch?v=QTTgpTeb0Z8",
      "Weezer_Buddy_Holly": "https://www.youtube.com/watch?v=kemivUKb4f4",
      "The_Breeders_Cannonball": "https://www.youtube.com/watch?v=fxvkI9MTQw4"
    }

    print(f"Preparing to download {len(video_urls)} tracks...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    for name, url in video_urls.items():
        # Determine group folder based on name prefix
        if name.startswith("Pixies"):
            out_file = os.path.join(base_dir, "data/pixies", name)
        else:
            out_file = os.path.join(base_dir, "data/control", name)
            
        # Check if already exists (yt-dlp appends .mp3)
        if os.path.exists(out_file + ".mp3"):
            print(f"Skipping {name} (already exists)")
            continue
            
        download_audio_url(url, out_file)
