import json
import subprocess
import os

# 1. CHANNELS LIST
CHANNELS = [
    {"url": "https://www.youtube.com/channel/UCAZTO65RFJoH3thMzFlnHvw", "name": "FancyToast"},
    {"url": "https://www.youtube.com/@ano8859", "name": "Ano"},
    {"url": "https://youtube.com/@len_osu", "name": "Len"},
    {"url": "https://youtube.com/@ysolar", "name": "Solar"},
    {"url": "https://youtube.com/@greevcs", "name": "Gree"}
]

DATABASE_FILE = "data/video_database.json"

def load_db():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # Convert list to dict for lookup { "id": {video_obj} }
                return {v['id']: v for v in data} if isinstance(data, list) else data
            except: return {}
    return {}

def fetch_videos():
    db = load_db()
    print(f"Current database has {len(db)} entries.")

    for channel in CHANNELS:
        print(f"Scraping {channel['name']} (fetching real dates)...")
        # REMOVED --flat-playlist to get actual upload dates
        # Added --playlist-end 5 to only get the 5 newest (saves time)
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--quiet",
            "--no-warnings",
            "--playlist-end", "5", 
            f"{channel['url']}/videos"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            for line in result.stdout.splitlines():
                if not line.strip(): continue
                video = json.loads(line)
                v_id = video['id']
                
                # Real date format: YYYYMMDD -> YYYY-MM-DD
                raw_date = video.get('upload_date')
                if raw_date:
                    fmt_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                else:
                    fmt_date = "2000-01-01" # Bottom of the list if missing

                if v_id not in db:
                    print(f"  + Found NEW: {video.get('title')[:30]}")
                    db[v_id] = {
                        "id": v_id,
                        "title": video.get('title'),
                        "channel": channel['name'],
                        "published": fmt_date,
                        "url": f"https://youtu.be/{v_id}",
                        "status": "Yes" # Default to Yes
                    }
                else:
                    # Update metadata but KEEP your manual "Yes/No" status
                    db[v_id].update({
                        "title": video.get('title'),
                        "published": fmt_date
                    })
        except Exception as e:
            print(f"Error fetching {channel['name']}: {e}")

    # 2. SORT BY DATE & ASSIGN SEQUENCE
    # Sort newest date first
    sorted_list = sorted(db.values(), key=lambda x: x['published'], reverse=True)
    
    # Add sequence number (1 is the absolute newest)
    for index, item in enumerate(sorted_list, 1):
        item['sequence'] = index

    # 3. SAVE TO FILE
    os.makedirs("data", exist_ok=True)
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_list, f, indent=4)
    
    print(f"Success! {len(sorted_list)} videos indexed in {DATABASE_FILE}")

if __name__ == "__main__":
    fetch_videos()
