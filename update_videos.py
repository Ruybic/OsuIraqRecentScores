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
        json.dump(db, f, indent=2)

    # 6. GENERATE HTML CARDS
    cards_html = ""
    for index, v in enumerate(db):
        display_num = len(db) - index
        # We add data-date and data-title attributes for the Search/Sort JS
        cards_html += f'''
        <div class="video-card" data-date="{v['date']}" data-title="{v['title'].lower()}">
            <div class="video-num">#{display_num}</div>
            <div class="vid-thumb">
                <iframe src="https://www.youtube.com/embed/{v['id']}" allowfullscreen loading="lazy"></iframe>
            </div>
            <h3>{v['title']}</h3>
        </div>'''

    # 7. THE TEMPLATE (Matches your Hub Index Style)
    template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>osu! Iraq | Showcase</title>
    <link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --osu-pink: #ff66aa; --dark-base: #1c1c21; --panel-bg: #2e2e38; --text-main: #ffffff; --text-muted: #888895; }}
        body {{ background-color: var(--dark-base); color: var(--text-main); font-family: 'Exo 2', sans-serif; margin: 0; }}

        /* HEADER */
        header {{
            background: #111116; padding: 12px 25px; display: flex; align-items: center;
            justify-content: space-between; border-bottom: 2px solid var(--panel-bg);
            position: sticky; top: 0; z-index: 1000;
        }}
        .logo-box img {{ height: 38px; display: block; }}
        
        .dropdown {{ position: relative; }}
        .dropbtn {{ background: var(--panel-bg); color: white; border: none; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-family: 'Exo 2'; font-weight: 600; transition: 0.2s; }}
        .dropbtn:hover {{ background: #3e3e4a; }}
        .dropdown-content {{
            display: none; position: absolute; right: 0; background-color: #25252e;
            min-width: 180px; box-shadow: 0px 8px 24px rgba(0,0,0,0.6); z-index: 1; border-radius: 6px; margin-top: 8px; overflow: hidden;
        }}
        .dropdown-content a {{ color: white; padding: 14px 20px; text-decoration: none; display: block; font-size: 14px; border-bottom: 1px solid #333; }}
        .dropdown-content.show {{ display: block; }}

        /* CONTROLS BAR */
        .controls-bar {{
            max-width: 1400px; margin: 30px auto 10px; padding: 0 20px;
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;
        }}
        .section-label {{ color: var(--osu-pink); font-weight: 800; font-size: 11px; letter-spacing: 2.5px; text-transform: uppercase; margin: 0; }}
        
        /* SEARCH & FILTER TOOLS */
        .tools-box {{ display: flex; gap: 10px; }}
        
        .search-input {{
            background: transparent; border: 1px solid #444; color: white;
            padding: 8px 12px; border-radius: 4px; font-family: 'Exo 2'; font-size: 13px;
            width: 200px; transition: 0.2s;
        }}
        .search-input:focus {{ border-color: var(--osu-pink); outline: none; }}
        
        .action-btn {{
            background: transparent; border: 1px solid var(--osu-pink); color: var(--osu-pink);
            padding: 8px 16px; border-radius: 4px; font-size: 12px; font-weight: bold;
            cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.2s;
        }}
        .action-btn:hover {{ background: var(--osu-pink); color: white; }}
        .action-btn.active {{ background: var(--osu-pink); color: white; }}

        /* VIDEO GRID */
        .feed-container {{ max-width: 1400px; margin: 0 auto; padding: 10px 20px 30px; }}
        .video-grid {{ 
            display: grid; gap: 20px; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); 
        }}
        
        .video-card {{ 
            background: var(--panel-bg); border-radius: 12px; overflow: hidden; 
            border: 1px solid #3e3e4a; position: relative; transition: 0.3s; 
        }}
        .video-card:hover {{ transform: translateY(-5px); border-color: var(--osu-pink); }}
        
        .video-num {{ 
            position: absolute; top: 10px; left: 10px; z-index: 5;
            background: rgba(0,0,0,0.8); color: var(--osu-pink); 
            padding: 3px 8px; border-radius: 6px; font-weight: 800; font-size: 12px; 
            border: 1px solid var(--osu-pink); pointer-events: none;
        }}

        .vid-thumb {{ width: 100%; aspect-ratio: 16 / 9; background: black; }}
        iframe {{ width: 100%; height: 100%; border: none; }}
        
        .video-card h3 {{ 
            font-size: 14px; padding: 15px; margin: 0; line-height: 1.4;
            background: #25252e; color: #eee; min-height: 40px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }}
        
        /* Message when search finds nothing */
        .no-results {{ 
            grid-column: 1 / -1; text-align: center; padding: 40px; 
            color: var(--text-muted); display: none; 
        }}
    </style>
</head>
<body>

<header>
    <div class="logo-box">
        <img src="https://i.im.ge/2026/02/13/eygP26.Picsart-26-02-13-01-23-55-682.jpeg" alt="osu! Iraq">
    </div>
    <div class="dropdown">
        <button class="dropbtn" id="menuBtn">MENU ▼</button>
        <div class="dropdown-content" id="myDropdown">
            <a href="index.html">Daily Scores</a>
            <a href="Videos.html">Showcase (Videos)</a>
            <a href="#">Rankings</a>
            <a href="#">Discord</a>
        </div>
    </div>
</header>

<div class="controls-bar">
    <span class="section-label">COMMUNITY SHOWCASE</span>
    
    <div class="tools-box">
        <input type="text" id="searchInput" class="search-input" placeholder="Search videos...">
        <button class="action-btn" id="sortBtn" onclick="toggleSort()">
            ⬇️ NEWEST
        </button>
    </div>
</div>

<div class="feed-container">
    <div class="video-grid" id="videoGrid">
        {cards_html}
        <div class="no-results" id="noResults">No videos match your search.</div>
    </div>
</div>

<script>
    // --- DROPDOWN LOGIC ---
    const menuBtn = document.getElementById('menuBtn');
    const dropdown = document.getElementById('myDropdown');
    menuBtn.onclick = (e) => {{ dropdown.classList.toggle("show"); e.stopPropagation(); }};
    window.onclick = (e) => {{ if (!e.target.matches('.dropbtn')) dropdown.classList.remove('show'); }};

    // --- SEARCH LOGIC ---
    const searchInput = document.getElementById('searchInput');
    const cards = document.querySelectorAll('.video-card');
    const noResults = document.getElementById('noResults');

    searchInput.addEventListener('keyup', (e) => {{
        const term = e.target.value.toLowerCase();
        let visibleCount = 0;

        cards.forEach(card => {{
            const title = card.getAttribute('data-title');
            if (title.includes(term)) {{
                card.style.display = "block";
                visibleCount++;
            }} else {{
                card.style.display = "none";
            }}
        }});
        
        noResults.style.display = visibleCount === 0 ? "block" : "none";
    }});

    // --- SORT LOGIC ---
    let isNewest = true;
    const grid = document.getElementById('videoGrid');
    const sortBtn = document.getElementById('sortBtn');

    function toggleSort() {{
        isNewest = !isNewest;
        sortBtn.innerText = isNewest ? "⬇️ NEWEST" : "⬆️ OLDEST";
        
        const cardsArray = Array.from(cards);
        cardsArray.sort((a, b) => {{
            const dateA = parseInt(a.getAttribute('data-date'));
            const dateB = parseInt(b.getAttribute('data-date'));
            return isNewest ? dateB - dateA : dateA - dateB;
        }});
        
        // Re-append in new order (Search filter stays active)
        cardsArray.forEach(card => grid.insertBefore(card, noResults));
    }}
</script>

</body>
</html>'''

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"✅ Rebuilt {HTML_FILE} with {len(db)} videos.")

if __name__ == "__main__":
    main()
    
