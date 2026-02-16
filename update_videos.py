import json
import subprocess
import os

CHANNELS = [
    {"url": "https://www.youtube.com/@FancyToast/videos501", "name": "FancyToast"},
    {"url": "https://www.youtube.com/@ano8859/videos", "name": "Ano"},
    {"url": "https://www.youtube.com/@len_osu/videos", "name": "Len"},
    {"url": "https://www.youtube.com/@ysolar/videos", "name": "Solar"},
    {"url": "https://www.youtube.com/@greevcs/videos", "name": "Gree"}
]

DATABASE_FILE = "data/video_database.json"

def fetch_videos():
    db = {}
    # 1. Load existing data to preserve manual "No" statuses
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                db = {v['id']: v for v in data}
        except: pass

    for channel in CHANNELS:
        print(f"--- Fetching {channel['name']} ---")
        cmd = [
            "yt-dlp", "--dump-json", "--flat-playlist", 
            "--ignore-errors", "--no-warnings", channel['url']
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            for line in result.stdout.splitlines():
                video = json.loads(line)
                v_id = video.get('id')
                if not v_id: continue

                raw_date = video.get('upload_date')
                # If no date, use 20000101 so it stays at the bottom
                fmt_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}" if raw_date else "2000-01-01"

                if v_id not in db:
                    db[v_id] = {
                        "id": v_id,
                        "title": video.get('title'),
                        "channel": channel['name'],
                        "published": fmt_date,
                        "url": f"https://youtu.be/{v_id}",
                        "status": "Yes"
                    }
                else:
                    # Update date if it was previously missing
                    if db[v_id]["published"] == "2000-01-01" and fmt_date != "2000-01-01":
                        db[v_id]["published"] = fmt_date

        except Exception as e:
            print(f"Error: {e}")

    # --- THE MAGIC SORT ---
    # Sort everything OLDEST to NEWEST first to assign sequence numbers
    all_vids = sorted(db.values(), key=lambda x: (x['published'], x['id']))
    
    for i, v in enumerate(all_vids, 1):
        v['sequence'] = i

    # Sort NEWEST to OLDEST for the website display
    final_list = sorted(all_vids, key=lambda x: (x['published'], x['sequence']), reverse=True)

    os.makedirs("data", exist_ok=True)
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4)
    
    print(f"Total Database: {len(final_list)} videos.")

if __name__ == "__main__":
    fetch_videos()
    
