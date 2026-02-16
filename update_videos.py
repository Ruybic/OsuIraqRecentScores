import json
import subprocess
import os

CHANNELS = [
    {"url": "https://www.youtube.com/channel/UCAZTO65RFJoH3thMzFlnHvw", "name": "FancyToast"},
    {"url": "https://www.youtube.com/@ano8859", "name": "Ano"},
    {"url": "https://www.youtube.com/@len_osu", "name": "Len"},
    {"url": "https://www.youtube.com/@ysolar", "name": "Solar"},
    {"url": "https://www.youtube.com/@greevcs", "name": "Gree"}
]

DATABASE_FILE = "data/video_database.json"

def fetch_videos():
    db = {}
    # We always try to load existing data first
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                db = {v['id']: v for v in data}
        except: pass

    for channel in CHANNELS:
        print(f"--- Scraping: {channel['name']} ---")
        
        # We use --extract-flat and --get-id to verify links
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--flat-playlist", 
            "--playlist-end", "5",
            "--ignore-errors",
            f"{channel['url']}/videos"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            # Log the error if yt-dlp fails
            if result.stderr:
                print(f"Log info: {result.stderr[:100]}")

            lines = result.stdout.strip().split('\n')
            found_on_channel = 0
            
            for line in lines:
                if not line.strip(): continue
                video = json.loads(line)
                v_id = video.get('id')
                if not v_id: continue

                # Handle date
                raw_date = video.get('upload_date', '20240101')
                fmt_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"

                if v_id not in db:
                    db[v_id] = {
                        "id": v_id,
                        "title": video.get('title', 'Unknown Title'),
                        "channel": channel['name'],
                        "published": fmt_date,
                        "url": f"https://youtu.be/{v_id}",
                        "status": "Yes"
                    }
                    found_on_channel += 1
            
            print(f"Successfully found {found_on_channel} new videos.")

        except Exception as e:
            print(f"Error processing {channel['name']}: {e}")

    # Sort and Save
    sorted_list = sorted(db.values(), key=lambda x: x.get('published', '0000-00-00'), reverse=True)
    for i, v in enumerate(sorted_list, 1):
        v['sequence'] = i

    os.makedirs("data", exist_ok=True)
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_list, f, indent=4)
    
    print(f"Final Count: {len(sorted_list)} videos saved.")

if __name__ == "__main__":
    fetch_videos()
    
