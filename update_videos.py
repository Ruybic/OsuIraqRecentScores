import json
import subprocess
import os
from datetime import datetime

# 1. SETUP YOUR CHANNELS
# We use full URLs now so we can mix IDs and Handles easily.
CHANNELS = [
    # Existing
    {"url": "https://www.youtube.com/channel/UCAZTO65RFJoH3thMzFlnHvw", "name": "FancyToast"},
    {"url": "https://www.youtube.com/channel/UC7yJx0OuUAa9WzrNVSnfhVw", "name": "Ano"},
    
    # New Additions
    {"url": "https://www.youtube.com/@len_osu", "name": "Len"},
    {"url": "https://www.youtube.com/@ysolar", "name": "Solar"},
    {"url": "https://www.youtube.com/@greevcs", "name": "Gree"}
]

DATABASE_FILE = "data/video_database.json"

def load_database():
    """Loads the existing JSON file if it exists."""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            try:
                # Load as a dictionary for fast ID lookups: { "VIDEO_ID": {data...}, ... }
                data = json.load(f)
                # Convert list back to dict if it was saved as list previously
                if isinstance(data, list):
                    return {v['id']: v for v in data}
                return data
            except json.JSONDecodeError:
                return {}
    return {}

def get_videos():
    # Load existing data so we don't lose your "No" edits
    db = load_database()
    new_videos_count = 0

    for channel in CHANNELS:
        print(f"Fetching: {channel['name']}...")
        
        # We allow yt-dlp to handle the URL parsing
        url = f"{channel['url']}/videos"
        
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--flat-playlist",  # Fast mode
            "--quiet",
            "--no-warnings",
            "--playlist-end", "15", # Fetch last 15 videos per channel (adjust as needed)
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if not line.strip(): continue
                
                try:
                    video_data = json.loads(line)
                    vid_id = video_data['id']
                    
                    # 2. DATE HANDLING
                    # yt-dlp returns YYYYMMDD. We format to YYYY-MM-DD.
                    raw_date = video_data.get('upload_date')
                    if raw_date:
                        formatted_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                    else:
                        # Fallback if yt-dlp misses the date in flat mode
                        formatted_date = "Unknown"

                    # 3. CHECK DATABASE
                    if vid_id in db:
                        # Video exists. We ONLY update details, NEVER overwrite "status".
                        # This ensures your "No" remains "No".
                        pass 
                    else:
                        # NEW VIDEO FOUND!
                        print(f"  + New video found: {video_data.get('title')[:30]}...")
                        db[vid_id] = {
                            "id": vid_id,
                            "title": video_data.get('title'),
                            "channel": channel['name'],
                            "published": formatted_date,
                            "url": f"https://youtu.be/{vid_id}",
                            "status": "Yes" # Default to Yes
                        }
                        new_videos_count += 1
                        
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            print(f"Error scraping {channel['name']}: {e}")

    # 4. SORTING & SEQUENCE
    # Convert dict back to list for sorting
    all_videos_list = list(db.values())
    
    # Sort by date (Newest first). 'Unknown' dates go to the bottom.
    all_videos_list.sort(key=lambda x: x.get('published', '0000-00-00'), reverse=True)

    # Re-save to JSON
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_videos_list, f, indent=4) # Indent 4 makes it easy for you to edit manually
    
    print(f"\nScan Complete.")
    print(f"New videos added: {new_videos_count}")
    print(f"Total database size: {len(all_videos_list)}")
    print(f"Saved to: {DATABASE_FILE}")

if __name__ == "__main__":
    get_videos()
    
