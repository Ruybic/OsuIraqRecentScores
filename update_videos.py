import os
import json
import subprocess

# --- CONFIGURATION ---
CHANNELS = [
    "https://www.youtube.com/@FancyToast501/videos"
]
DATA_FILE = "data/video_db.json"
HTML_FILE = "Videos.html"

def get_videos():
    all_videos = []
    for url in CHANNELS:
        print(f"📡 Scanning full archive: {url}...")
        # REMOVED: --playlist-items limit. Now fetches everything.
        cmd = [
            "yt-dlp", 
            "--flat-playlist", 
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "--print", "%(title)s\n%(id)s\n%(upload_date)s", 
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if not result.stdout.strip():
            print(f"⚠️ No output for {url}")
            continue

        lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        # yt-dlp outputs 3 lines per video: Title, ID, Date
        for i in range(0, len(lines), 3):
            if i+2 < len(lines):
                all_videos.append({
                    "title": lines[i],
                    "id": lines[i+1],
                    "date": lines[i+2] # Format is YYYYMMDD
                })
    return all_videos

def main():
    os.makedirs("data", exist_ok=True)
    
    # 1. Load History (Database)
    db = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                db = json.load(f)
        except: db = []

    # 2. Get All Videos
    found_vids = get_videos()
    
    # 3. Merge (Update database with new finds)
    existing_ids = {v['id'] for v in db}
    for v in found_vids:
        if v['id'] not in existing_ids:
            db.append(v)
            print(f"✨ New Video Found: {v['title']}")
    
    # 4. Sort by Date (Newest First by default)
    # The date string "20231201" sorts correctly alphabetically
    db.sort(key=lambda x: x['date'], reverse=True)

    # 5. Save Database
    with open(DATA_FILE, "w") as f:
        json.dump(db, f, indent=2
                  
