import os
import requests
import zipfile
import io

def download_beatles_annotations():
    """
    Downloads the Isophonics Beatles annotations from a reliable source.
    Since the official Isophonics site can be flaky or require complex scraping,
    we will use the repository that mirrors these annotations if available,
    or try to download the specific zip file if we have a direct link.
    
    For this task, we will try to download the reference annotations from the Internet Archive 
    or a similar open data repository if possible. 
    
    However, a reliable mirror for the Isophonics Beatles annotations is often hosted on GitHub.
    Let's try to download the 'The Beatles' subset from a known mirror or the original source.
    
    Actually, the most robust way for now without a direct stable URL for the ZIP 
    is to use the `mirdata` library if installed, but better to keep it simple.
    
    Let's try downloading from the limitied Isophonics sample or a GitHub mirror.
    The 'isophonics-BIT-Mirex2009' might be available.
    
    Let's try a specific GitHub URL that hosts these.
    """
    
    # This is a known mirror for the lab files (annotations)
    # properly structured.
    # URL: https://github.com/TUT-ARG/structure-dataset/archive/refs/heads/master.zip
    # Which contains Beatles annotations in 'BeatlesTUT' folder.
    
    url = "https://github.com/TUT-ARG/structure-dataset/archive/refs/heads/master.zip"
    target_dir = os.path.join(os.path.dirname(__file__), "data", "beatles_annotations")
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    print(f"Downloading annotations from {url}...")
    try:
        r = requests.get(url)
        r.raise_for_status()
        
        print("Extracting...")
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            # We only want the BeatlesTUT folder partitions
            for file in z.namelist():
                if "BeatlesTUT" in file and file.endswith(".lab"):
                    # Extract to our target dir, flattening the structure slightly if needed
                    # The zip structure is structure-dataset-master/BeatlesTUT/annotations/...
                    
                    # Let's just extract it and we can organize later
                    z.extract(file, target_dir)
                    
        print(f"Downloaded and extracted annotations to {target_dir}")
        
    except Exception as e:
        print(f"Failed to download: {e}")

if __name__ == "__main__":
    download_beatles_annotations()
