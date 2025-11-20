from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, HTMLResponse
from pymongo import MongoClient
from datetime import datetime, timezone
import json
import base64
import os

app = FastAPI(title="MongoDB Data Server")

# 🔐 Secret Key - CHANGE THIS!
SECRET_KEY = "TeriGandMeinLoda9845@#14!!"

def simple_encrypt(data: str) -> str:
    """Simple XOR encryption"""
    key = SECRET_KEY
    encrypted = []
    for i, char in enumerate(data):
        key_char = key[i % len(key)]
        encrypted_char = chr(ord(char) ^ ord(key_char))
        encrypted.append(encrypted_char)
    encrypted_str = ''.join(encrypted)
    return base64.b64encode(encrypted_str.encode('latin-1')).decode()

def encrypt_data(data: dict) -> str:
    """Encrypt JSON data"""
    json_str = json.dumps(data)
    return simple_encrypt(json_str)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://elvishyadav_opm:naman1811421@cluster0.uxuplor.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["unacademy_db"]
educators_col = db["educators"]

def map_educator(doc: dict) -> dict:
    return {
        "id": doc.get("uid", ""),
        "name": f"{doc.get('first_name', '')} {doc.get('last_name', '')}".strip(),
        "subject": f"@{doc.get('username', 'unknown')}",
        "image": doc.get("avatar", ""),
        "batches": [map_batch(b) for b in doc.get("batches", [])],
        "courses": [map_course(c) for c in doc.get("courses", [])],
    }

def map_batch(b: dict) -> dict:
    return {
        "id": b.get("uid", ""),
        "name": b.get("name", "Unknown Batch"),
        "image": b.get("cover_photo", ""),
        "startDate": b.get("starts_at", ""),
        "endDate": b.get("completed_at", "") or b.get("ends_at", ""),
        "lastCheckedAt": b.get("last_checked_at", ""),
        "url": f"https://optech.com/op?={b.get('uid', '')}",
        "teachers": b.get("teachers", "Unknown")
    }

def map_course(c: dict) -> dict:
    return {
        "id": c.get("uid", ""),
        "name": c.get("name", "Unknown Course"),
        "image": c.get("thumbnail", ""),
        "startDate": c.get("starts_at", ""),
        "endDate": c.get("ends_at", ""),
        "lastCheckedAt": c.get("last_checked_at", ""),
        "url": f"https://optech.com/op?={c.get('uid', '')}",
        "teachers": c.get("teachers", "Unknown")
    }

def get_status(item: dict) -> str | None:
    start = item.get("startDate")
    end = item.get("endDate")
    if not start or not end:
        return None
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if start_dt <= now <= end_dt:
            return "live"
        elif now > end_dt:
            return "completed"
        return None
    except Exception:
        return None

@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>𝗖𝗛𝗨𝗡𝗔𝗖𝗔𝗗𝗘𝗠𝗬 😈</title>
  <style>
    :root{{--bg: #0b1020;--surface: #121832;--text: #e8ecf8;--muted: #9aa3b2;--primary: #2ea8ff;--accent: #ff6b6b;--success: #33ff66;--radius: 12px;}}
    [data-theme="light"] {{--bg: #f8f9fc;--surface: #ffffff;--text: #1a1a1a;--muted: #666;--primary: #0066cc;--accent: #cc0000;--success: #006600;}}
    * {{ box-sizing: border-box; }}
    html, body {{ height: 100%; }}
    body{{margin:0;font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;background: var(--bg);color: var(--text);line-height:1.5;overflow-x: hidden;transition: background 0.3s ease;}}
    a {{ color: var(--primary); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    #bg-canvas{{position: fixed;inset: 0;z-index: -1;display:block;background: radial-gradient(1000px 600px at 80% -10%, rgba(46,168,255,0.12), transparent),radial-gradient(800px 500px at 10% -20%, rgba(255,255,255,0.06), transparent),var(--bg);}}
    .container{{max-width: 1100px;margin-inline:auto;padding: 16px;}}
    header{{display:flex;flex-direction: column;gap: 12px;padding-block: 16px;}}
    .brand{{display:flex;align-items:center;justify-content: space-between;}}
    .brand-left {{ display: flex; align-items: center; gap: 12px; }}
    .brand-badge{{width:36px; height:36px; border-radius:999px;display:grid; place-items:center;background: var(--primary);color:#001122; font-weight:800;box-shadow: 0 0 0 6px rgba(46,168,255,0.15);}}
    .title{{font-size: clamp(20px, 2.5vw, 28px);font-weight: 800;letter-spacing: -0.01em;}}
    .subtitle{{ color: var(--muted); font-size: 14px; }}
    .theme-toggle {{background: var(--surface);border: 1px solid rgba(255,255,255,0.1);border-radius: 999px;width: 48px; height: 28px;position: relative;cursor: pointer;transition: all 0.3s;}}
    .theme-toggle::after {{content: '';position: absolute;top: 4px; left: 4px;width: 20px; height: 20px;background: var(--primary);border-radius: 50%;transition: transform 0.3s;}}
    .theme-toggle.active::after {{ transform: translateX(20px); }}
    .promo-banner{{background: linear-gradient(135deg, rgba(46,168,255,0.15), rgba(255,107,107,0.15));border: 1px solid rgba(46,168,255,0.3);border-radius: var(--radius);padding: 16px 20px;margin-bottom: 12px;display: flex;align-items: center;justify-content: space-between;gap: 12px;flex-wrap: wrap;position: relative;overflow: hidden;}}
    .promo-banner::before{{content: '';position: absolute;top: -50%;right: -20%;width: 200px;height: 200px;background: radial-gradient(circle, rgba(255,255,255,0.1), transparent);border-radius: 50%;}}
    .promo-content{{flex: 1;min-width: 200px;position: relative;z-index: 1;}}
    .promo-title{{font-size: 18px;font-weight: 800;margin: 0 0 4px 0;color: var(--text);}}
    .promo-text{{font-size: 14px;color: var(--muted);margin: 0;}}
    .promo-link{{background: var(--primary);color: #001122;padding: 10px 20px;border-radius: 999px;font-weight: 700;text-decoration: none;display: inline-block;transition: transform 0.2s ease, box-shadow 0.2s ease;position: relative;z-index: 1;}}
    .promo-link:hover{{transform: translateY(-2px);box-shadow: 0 6px 20px rgba(46,168,255,0.4);text-decoration: none;}}
    .search-row{{display:flex; gap:8px; flex-wrap:wrap;align-items:center;background: color-mix(in oklab, var(--surface) 92%, black 0%);padding: 8px;border-radius: var(--radius);border: 1px solid rgba(255,255,255,0.06);}}
    .search-row input{{flex:1 1 260px;padding: 10px 12px;border-radius: 10px;border: 1px solid rgba(255,255,255,0.08);background: #0f1530;color: var(--text);outline: none;}}
    [data-theme="light"] .search-row input {{ background: #fff; color: #000; }}
    .search-row input::placeholder{{ color: #7b8496; }}
    .tabs{{display:flex; gap:8px; flex-wrap: wrap;background: color-mix(in oklab, var(--surface) 92%, black 0%);padding: 8px;border-radius: var(--radius);border: 1px solid rgba(255,255,255,0.06);}}
    .tab-btn{{appearance: none; border: 1px solid rgba(255,255,255,0.08); background: #0f1530;padding: 8px 12px; border-radius: 999px; cursor: pointer;color: var(--text); font-weight: 700;transition: all 0.2s ease;}}
    [data-theme="light"] .tab-btn {{ background: #eee; }}
    .tab-btn[aria-selected="true"]{{background: var(--primary);color: #001122;border-color: transparent;box-shadow: 0 4px 20px rgba(46,168,255,0.25);}}
    .section-head{{display:flex; align-items:center; justify-content:space-between;margin-top: 16px;margin-bottom: 8px;}}
    .section-head h2{{margin:0; font-size: 18px; font-weight: 800;}}
    .sub-tabs{{display: flex;gap: 8px;margin-top: 12px;margin-bottom: 8px;}}
    .sub-tab-btn{{appearance: none;border: 1px solid rgba(255,255,255,0.08);background: #0f1530;padding: 8px 16px;border-radius: 999px;cursor: pointer;color: var(--text);font-weight: 600;font-size: 14px;transition: all 0.2s ease;}}
    [data-theme="light"] .sub-tab-btn {{ background: #eee; }}
    .sub-tab-btn.active{{background: var(--primary);color: #001122;border-color: transparent;}}
    .grid{{display:grid;grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));gap:16px;margin-top:16px;}}
    .card{{background: linear-gradient(180deg, #0f1530, #0e1429);border-radius: var(--radius);padding: 16px;display:flex; flex-direction: column; gap: 12px;border: 1px solid rgba(255,255,255,0.06);transform: perspective(800px) translateZ(0);transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;position: relative;cursor: default;}}
    [data-theme="light"] .card {{ background: #fff; border-color: #ddd; }}
    .card:hover{{transform: perspective(800px) rotateX(2deg) rotateY(-2deg);border-color: rgba(46,168,255,0.35);box-shadow: 0 8px 30px rgba(46,168,255,0.15);}}
    .status-badge{{position: absolute;top: 12px;left: 12px;display: flex;align-items: center;gap: 6px;padding: 4px 8px;border-radius: 6px;font-size: 11px;font-weight: 700;text-transform: uppercase;letter-spacing: 0.5px;z-index: 1;}}
    .status-badge.live{{background: rgba(255, 51, 51, 0.2);border: 1px solid rgba(255, 51, 51, 0.5);color: #ff6b6b;}}
    .status-badge.completed{{background: rgba(51, 255, 102, 0.2);border: 1px solid rgba(51, 255, 102, 0.5);color: #33ff66;}}
    .status-dot{{width: 6px;height: 6px;border-radius: 50%;display: inline-block;}}
    .status-dot.live{{background: #ff6b6b;animation: pulse-red 1.5s ease-in-out infinite;}}
    .status-dot.completed{{background: #33ff66;}}
    @keyframes pulse-red {{0%, 100% {{ opacity: 1; }}50% {{ opacity: 0.5; }}}}
    .row{{ display:flex; align-items:center; gap:12px; }}
    .avatar{{width:64px; height:64px; border-radius: 999px; flex: 0 0 64px;object-fit: cover; border: 1px solid rgba(255,255,255,0.08);background: #1a2142;}}
    [data-theme="light"] .avatar {{ border-color: #ccc; background: #f0f0f0; }}
    .thumb{{width:100%; height:140px; object-fit: cover; border-radius: 10px;border: 1px solid rgba(255,255,255,0.06); background:#10152c;}}
    [data-theme="light"] .thumb {{ border-color: #ddd; background: #f9f9f9; }}
    .meta h3{{ margin:0; font-size:18px; font-weight:800; }}
    .meta p{{ margin:0; color: var(--muted); font-size: 13px; }}
    .dates{{display: flex; flex-direction: column; gap: 6px;font-size: 12px; color: var(--muted);border-top: 1px dashed rgba(255,255,255,0.08);padding-top: 8px;margin-top: 8px;}}
    .date-item{{display: flex; justify-content: space-between; gap: 8px;}}
    .date-label{{ font-weight: 600; color: var(--text); }}
    .teachers-section {{margin-top: 8px;}}
    .teacher-box {{background: rgba(46,168,255,0.2);color: var(--text);padding: 8px 12px;border-radius: 8px;font-size: 12px;font-weight: 500;border: 1px solid rgba(46,168,255,0.3);}}
    .actions{{display:flex;gap:8px;flex-wrap: wrap;margin-top: 8px;}}
    .pill{{flex:1 1 auto;min-width: 120px;display:flex;align-items:center;justify-content:center;padding: 10px 12px;border-radius: 10px;background: #0f1530;border: 1px solid rgba(255,255,255,0.08);color: var(--text);font-weight: 700;cursor: pointer;position: relative;transition: all 0.2s ease;}}
    [data-theme="light"] .pill {{ background: #eee; }}
    .pill:hover{{border-color: rgba(46,168,255,0.45);background: #121832;}}
    [data-theme="light"] .pill:hover {{ background: #ddd; }}
    .pill.active{{background: var(--primary);color: #001122;border-color: transparent;}}
    .panel{{border-top: 1px dashed rgba(255,255,255,0.08);padding-top: 12px;margin-top: 12px;display: none;}}
    .panel.show{{ display:block; }}
    .list{{display:flex;flex-direction: column;gap:8px;}}
    .list-item{{background:#0f1530;border:1px solid rgba(255,255,255,0.08);padding:10px 12px;border-radius: 8px;display:grid;grid-template-columns: 56px 1fr auto;gap:10px;align-items:center;text-decoration:none;color: var(--text);cursor: pointer;transition: border-color .2s ease;position: relative;}}
    [data-theme="light"] .list-item {{ background: #fff; border-color: #ddd; }}
    .list-item:hover{{ border-color: rgba(46,168,255,0.35); }}
    .list-item-status{{position: absolute;top: 4px;left: 4px;width: 8px;height: 8px;border-radius: 50%;}}
    .list-item-status.live{{background: #ff6b6b;animation: pulse-red 1.5s ease-in-out infinite;}}
    .list-item-status.completed{{background: #33ff66;}}
    .mini{{width:56px;height:40px;object-fit: cover;border-radius: 6px;background:#0e1328;border: 1px solid rgba(255,255,255,0.06);}}
    [data-theme="light"] .mini {{ background: #f0f0f0; border-color: #ccc; }}
    .list .right-hint{{color: var(--muted);font-size: 12px;}}
    .load-more-wrap{{display:flex;justify-content:center;margin-top: 16px;}}
    .load-more{{appearance:none;border:1px solid rgba(255,255,255,0.12);background:#0f1530;color:var(--text);font-weight:700;padding:10px 20px;border-radius: 10px;cursor:pointer;transition: all 0.2s ease;}}
    [data-theme="light"] .load-more {{ background: #eee; border-color: #ccc; }}
    .load-more:hover{{border-color: rgba(46,168,255,0.5);background: #121832;}}
    [data-theme="light"] .load-more:hover {{ background: #ddd; }}
    footer{{margin-top: 40px;padding: 24px 0;color: var(--muted);font-size: 14px;text-align:center;}}
    .sr-only{{position: absolute;width: 1px;height: 1px;padding: 0;margin: -1px;overflow: hidden;clip: rect(0, 0, 0, 0);white-space: nowrap;border: 0;}}
    .back-to-top {{position: fixed;bottom: 20px;right: 20px;width: 48px;height: 48px;background: var(--primary);color: white;border-radius: 50%;display: grid;place-items: center;font-size: 20px;cursor: pointer;opacity: 0;visibility: hidden;transition: all 0.3s;box-shadow: 0 4px 12px rgba(0,0,0,0.3);z-index: 1000;}}
    .back-to-top.show {{ opacity: 1; visibility: visible; }}
    .modal {{position: fixed;z-index: 1000;left: 0;top: 0;width: 100%;height: 100%;overflow: auto;background: rgba(0,0,0,0.5);display: none;align-items: center;justify-content: center;}}
    .modal.show {{display: flex;}}
    .modal-content {{background: var(--surface);padding: 20px;border-radius: 12px;position: relative;max-width: 500px;width: 90%;}}
    [data-theme="light"] .modal-content {{ background: #fff; }}
    .close {{position: absolute;top: 10px;right: 10px;cursor: pointer;font-size: 24px;color: var(--muted);}}
    .watch-btn {{margin-top: 16px;background: var(--primary);color: white;padding: 12px;border: none;border-radius: 8px;width: 100%;cursor: pointer;font-weight: 700;}}
  </style>
</head>
<body data-theme="dark">
  <canvas id="bg-canvas" aria-hidden="true"></canvas>
  <div class="container">
    <header>
      <div class="brand">
        <div class="brand-left">
          <div class="brand-badge" aria-hidden="true">ED</div>
          <div>
            <div class="title">CHUNACADEMY 😈</div>
            <p class="subtitle">Yaha pe Aapko Sabhi Batches, Courses milenge unke 😁 Enjoy...</p>
          </div>
        </div>
        <div class="theme-toggle" id="theme-toggle"></div>
      </div>
      <div class="promo-banner">
        <div class="promo-content">
          <h3 class="promo-title">𝐂𝐡𝐞𝐜𝐤𝐨𝐮𝐭 𝐎𝐮𝐫 𝐌𝐚𝐢𝐧 𝐖𝐞𝐛𝐬𝐢𝐭𝐞 ✅</h3>
          <p class="promo-text">Discover amazing free other Websites 🔥</p>
        </div>
        <a href="https://yashyasag.github.io/hiddens" class="promo-link">Visit Now</a>
      </div>
      <div class="search-row" role="search">
        <label class="sr-only" for="search">Search</label>
        <input id="search" placeholder="Search keyword (e.g., 'Rahul', 'Physics', 'Batch A')" />
      </div>
      <nav class="tabs" role="tablist" aria-label="Sections">
        <button class="tab-btn" role="tab" aria-selected="true" id="tab-educators">Educators</button>
        <button class="tab-btn" role="tab" aria-selected="false" id="tab-batches">Batches</button>
        <button class="tab-btn" role="tab" aria-selected="false" id="tab-courses">Courses</button>
      </nav>
    </header>
    <main id="main">
      <section id="panel-educators" role="tabpanel">
        <div class="section-head"><h2>Educators</h2></div>
        <div id="edu-grid" class="grid"></div>
        <div id="edu-load" class="load-more-wrap"></div>
      </section>
      <section id="panel-batches" role="tabpanel" hidden>
        <div class="section-head"><h2>Batches</h2></div>
        <div class="sub-tabs">
          <button class="sub-tab-btn active" data-filter="live">Live Running</button>
          <button class="sub-tab-btn" data-filter="completed">Completed</button>
        </div>
        <div id="batch-grid" class="grid"></div>
        <div id="batch-load" class="load-more-wrap"></div>
      </section>
      <section id="panel-courses" role="tabpanel" hidden>
        <div class="section-head"><h2>Courses</h2></div>
        <div class="sub-tabs">
          <button class="sub-tab-btn active" data-filter="live">Live Running</button>
          <button class="sub-tab-btn" data-filter="completed">Completed</button>
        </div>
        <div id="course-grid" class="grid"></div>
        <div id="course-load" class="load-more-wrap"></div>
      </section>
      <section id="panel-search" hidden>
        <div class="section-head"><h2>Search Results</h2></div>
        <div class="section-head"><h2>Educators</h2></div>
        <div id="search-edu" class="grid"></div>
        <div id="search-edu-load" class="load-more-wrap"></div>
        <div class="section-head"><h2>Batches</h2></div>
        <div id="search-batch" class="grid"></div>
        <div id="search-batch-load" class="load-more-wrap"></div>
        <div class="section-head"><h2>Courses</h2></div>
        <div id="search-course" class="grid"></div>
        <div id="search-course-load" class="load-more-wrap"></div>
      </section>
    </main>
    <footer>🔐 Encrypted & Secured API</footer>
  </div>
  <div class="back-to-top" id="back-to-top">Up</div>
  <div id="modal" class="modal">
    <div class="modal-content">
      <span id="modal-close" class="close">×</span>
      <div id="modal-body"></div>
      <button id="modal-watch" class="watch-btn">CLICK TO WATCH LECTURES</button>
    </div>
  </div>
  <script>
    const SECRET_KEY = "{SECRET_KEY}";
    function simpleDecrypt(encrypted) {{
      try {{
        const decoded = atob(encrypted);
        const key = SECRET_KEY;
        let decrypted = '';
        for (let i = 0; i < decoded.length; i++) {{
          const charCode = decoded.charCodeAt(i) ^ key.charCodeAt(i % key.length);
          decrypted += String.fromCharCode(charCode);
        }}
        return JSON.parse(decrypted);
      }} catch(e) {{
        console.error('Decryption error:', e);
        return null;
      }}
    }}
    const IMG_USER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Crect fill='%231a2142' width='64' height='64'/%3E%3Ctext x='50%25' y='50%25' font-size='24' text-anchor='middle' dy='.3em' fill='%239aa3b2'%3EUser%3C/text%3E%3C/svg%3E";
    const IMG_PH = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='200'%3E%3Crect fill='%2310152c' width='400' height='200'/%3E%3Ctext x='50%25' y='50%25' font-size='20' text-anchor='middle' dy='.3em' fill='%239aa3b2'%3EBook%3C/text%3E%3C/svg%3E";
    const TODAY = new Date();
    const PAGE = 5;
    function formatDate(dateStr) {{if (!dateStr) return 'N/A';let date;try {{date = new Date(dateStr);}} catch (e) {{return dateStr;}}const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];const day = date.getDate();const month = monthNames[date.getMonth()];const year = date.getFullYear();const hours = String(date.getHours()).padStart(2, '0');const mins = String(date.getMinutes()).padStart(2, '0');return `${{day}}-${{month}}-${{year}} [${{hours}}:${{mins}}]`;}}
    function getStatus(startDate, endDate) {{if (!startDate || !endDate) return null;const start = new Date(startDate);const end = new Date(endDate);if (TODAY >= start && TODAY <= end) {{return 'live';}} else if (TODAY > end) {{return 'completed';}}return null;}}
    const state = {{tab: "educators",batchFilter: "live",courseFilter: "live",offsets: {{ educators: 0, batches: 0, courses: 0 }},searchQuery: "",searchOffsets: {{ educators: 0, batches: 0, courses: 0 }},panels: {{}},}};
    const lazyObserver = new IntersectionObserver((entries) => {{for (const entry of entries) {{const img = entry.target;if (entry.isIntersecting && !img.src && img.dataset.src) {{img.src = img.dataset.src;}}}}}}, {{ rootMargin: "200px" }});
    const tabEdu = document.getElementById("tab-educators");
    const tabBat = document.getElementById("tab-batches");
    const tabCou = document.getElementById("tab-courses");
    const panelEdu = document.getElementById("panel-educators");
    const panelBat = document.getElementById("panel-batches");
    const panelCou = document.getElementById("panel-courses");
    const panelSearch = document.getElementById("panel-search");
    const eduGrid = document.getElementById("edu-grid");
    const eduLoad = document.getElementById("edu-load");
    const batchGrid = document.getElementById("batch-grid");
    const batchLoad = document.getElementById("batch-load");
    const courseGrid = document.getElementById("course-grid");
    const courseLoad = document.getElementById("course-load");
    const sEdu = document.getElementById("search-edu");
    const sEduLoad = document.getElementById("search-edu-load");
    const sBat = document.getElementById("search-batch");
    const sBatLoad = document.getElementById("search-batch-load");
    const sCou = document.getElementById("search-course");
    const sCouLoad = document.getElementById("search-course-load");
    const searchInput = document.getElementById("search");
    const themeToggle = document.getElementById("theme-toggle");
    const backToTop = document.getElementById("back-to-top");
    const modal = document.getElementById("modal");
    const modalClose = document.getElementById("modal-close");
    const modalBody = document.getElementById("modal-body");
    const modalWatch = document.getElementById("modal-watch");
    function createStatusBadge(status) {{const badge = document.createElement("div");badge.className = `status-badge ${{status}}`;const dot = document.createElement("span");dot.className = `status-dot ${{status}}`;const text = status === 'live' ? 'Live Running' : 'Completed';badge.appendChild(dot);badge.appendChild(document.createTextNode(text));return badge;}}
    function selectTab(which) {{state.tab = which;tabEdu.setAttribute("aria-selected", which === "educators" ? "true" : "false");tabBat.setAttribute("aria-selected", which === "batches" ? "true" : "false");tabCou.setAttribute("aria-selected", which === "courses" ? "true" : "false");panelEdu.hidden = which !== "educators";panelBat.hidden = which !== "batches";panelCou.hidden = which !== "courses";panelSearch.hidden = true;renderCurrent();}}
    tabEdu.addEventListener("click", () => selectTab("educators"));
    tabBat.addEventListener("click", () => selectTab("batches"));
    tabCou.addEventListener("click", () => selectTab("courses"));
    const batchSubTabs = document.querySelectorAll('#panel-batches .sub-tab-btn');
    batchSubTabs.forEach(btn => {{btn.addEventListener('click', () => {{batchSubTabs.forEach(b => b.classList.remove('active'));btn.classList.add('active');state.batchFilter = btn.dataset.filter;renderBatches(true);}});}});
    const courseSubTabs = document.querySelectorAll('#panel-courses .sub-tab-btn');
    courseSubTabs.forEach(btn => {{btn.addEventListener('click', () => {{courseSubTabs.forEach(b => b.classList.remove('active'));btn.classList.add('active');state.courseFilter = btn.dataset.filter;renderCourses(true);}});}});
    function educatorCard(ed) {{const card = document.createElement("article");card.className = "card";card.addEventListener("click", (e) => {{if (e.target.closest('.pill, .list-item, .load-more')) return;window.location.href = `https://optech.com/op?=${{ed.id}}`;}} );const row = document.createElement("div");row.className = "row";const img = document.createElement("img");img.className = "avatar";img.width = 64; img.height = 64; img.alt = `Photo of ${{ed.name}}`;img.loading = "lazy";img.dataset.src = ed.image || IMG_USER;lazyObserver.observe(img);const meta = document.createElement("div");meta.className = "meta";const h3 = document.createElement("h3"); h3.textContent = ed.name;const p = document.createElement("p"); p.textContent = ed.subject;meta.append(h3, p);row.append(img, meta);const actions = document.createElement("div");actions.className = "actions";const b1 = document.createElement("button");b1.className = "pill"; b1.type = "button"; b1.textContent = `Batches (${{ed.batches.length}})`;const b2 = document.createElement("button");b2.className = "pill"; b2.type = "button"; b2.textContent = `Courses (${{ed.courses.length}})`;actions.append(b1, b2);const panel = document.createElement("div");panel.className = "panel";const list = document.createElement("div");list.className = "list";panel.append(list);const loadWrap = document.createElement("div");loadWrap.className = "load-more-wrap";panel.append(loadWrap);if (!state.panels[ed.id]) state.panels[ed.id] = {{ batches: 0, courses: 0, mode: null }};function renderPanel(kind, reset = false) {{const pstate = state.panels[ed.id];if (reset || pstate.mode !== kind) {{pstate.mode = kind;pstate[kind] = 0;list.innerHTML = "";loadWrap.innerHTML = "";}}const all = kind === "batches" ? ed.batches : ed.courses;const start = pstate[kind];const end = Math.min(start + 5, all.length);for (let i = start; i < end; i++) {{const it = all[i];const item = document.createElement("a");item.className = "list-item";item.href = it.url;item.target = "_blank";const statusDot = document.createElement("div");statusDot.className = "list-item-status";const status = getStatus(it.startDate, it.endDate);if (status) statusDot.classList.add(status);item.appendChild(statusDot);const mini = document.createElement("img");mini.className = "mini"; mini.alt = "";mini.loading = "lazy"; mini.dataset.src = it.image || IMG_PH;lazyObserver.observe(mini);const label = document.createElement("div");label.textContent = it.name;const hint = document.createElement("div");hint.className = "right-hint";hint.textContent = kind === "batches" ? "Batch" : "Course";const detailsBtn = document.createElement("span");detailsBtn.textContent = "Info";detailsBtn.style.cursor = "pointer";detailsBtn.style.marginLeft = "8px";detailsBtn.title = "Show Details";detailsBtn.onclick = (e) => {{e.preventDefault();e.stopPropagation();showDetails(it, kind);}};item.append(mini, label, hint, detailsBtn);list.append(item);}}pstate[kind] = end;loadWrap.innerHTML = "";if (end < all.length) {{const btn = document.createElement("button");btn.className = "load-more"; btn.textContent = `Load more (${{all.length - end}} remaining)`;btn.addEventListener("click", (e) => {{e.stopPropagation();renderPanel(kind, false);}});loadWrap.append(btn);}}}}function togglePanel(kind) {{const isOpen = panel.classList.contains("show") && state.panels[ed.id].mode === kind;if (isOpen) {{panel.classList.remove("show");b1.classList.remove("active");b2.classList.remove("active");}} else {{panel.classList.add("show");b1.classList.toggle("active", kind === "batches");b2.classList.toggle("active", kind === "courses");renderPanel(kind, true);}}}}b1.addEventListener("click", (e) => {{e.stopPropagation();togglePanel("batches");}});b2.addEventListener("click", (e) => {{e.stopPropagation();togglePanel("courses");}});card.append(row, actions, panel);return card;}}
    function batchCard(b) {{const card = document.createElement("article");card.className = "card";card.addEventListener("click", () => window.location.href = b.url);const status = getStatus(b.startDate, b.endDate);if (status) card.appendChild(createStatusBadge(status));const img = document.createElement("img");img.className = "thumb"; img.alt = "";img.loading = "lazy"; img.dataset.src = b.image || IMG_PH;lazyObserver.observe(img);const meta = document.createElement("div");meta.className = "meta";const h3 = document.createElement("h3"); h3.textContent = b.name;const p = document.createElement("p"); p.textContent = "Batch";meta.append(h3, p);const dates = document.createElement("div");dates.className = "dates";const startItem = document.createElement("div");startItem.className = "date-item";const startLabel = document.createElement("span");startLabel.className = "date-label";startLabel.textContent = "Starts At:";const startDate = document.createElement("span");startDate.textContent = formatDate(b.startDate);startItem.append(startLabel, startDate);const endItem = document.createElement("div");endItem.className = "date-item";const endLabel = document.createElement("span");endLabel.className = "date-label";endLabel.textContent = "Completed At:";const endDate = document.createElement("span");endDate.textContent = formatDate(b.endDate);endItem.append(endLabel, endDate);const lastItem = document.createElement("div");lastItem.className = "date-item";const lastLabel = document.createElement("span");lastLabel.className = "date-label";lastLabel.textContent = "Last Checked At:";const lastDate = document.createElement("span");lastDate.textContent = b.lastCheckedAt || "N/A";lastItem.append(lastLabel, lastDate);dates.append(startItem, endItem, lastItem);const teachersSection = document.createElement("div");teachersSection.className = "teachers-section";const teachersLabel = document.createElement("span");teachersLabel.className = "date-label";teachersLabel.textContent = "Teachers:";const teacherBox = document.createElement("div");teacherBox.className = "teacher-box";teacherBox.textContent = b.teachers || "Unknown";teachersSection.append(teachersLabel, teacherBox);dates.append(teachersSection);card.append(img, meta, dates);return card;}}
    function courseCard(c) {{const card = document.createElement("article");card.className = "card";card.addEventListener("click", () => window.location.href = c.url);const status = getStatus(c.startDate, c.endDate);if (status) card.appendChild(createStatusBadge(status));const img = document.createElement("img");img.className = "thumb"; img.alt = "";img.loading = "lazy"; img.dataset.src = c.image || IMG_PH;lazyObserver.observe(img);const meta = document.createElement("div");meta.className = "meta";const h3 = document.createElement("h3"); h3.textContent = c.name;const p = document.createElement("p"); p.textContent = "Course";meta.append(h3, p);const dates = document.createElement("div");dates.className = "dates";const startItem = document.createElement("div");startItem.className = "date-item";const startLabel = document.createElement("span");startLabel.className = "date-label";startLabel.textContent = "Starts At:";const startDate = document.createElement("span");startDate.textContent = formatDate(c.startDate);startItem.append(startLabel, startDate);const endItem = document.createElement("div");endItem.className = "date-item";const endLabel = document.createElement("span");endLabel.className = "date-label";endLabel.textContent = "Ends At:";const endDate = document.createElement("span");endDate.textContent = formatDate(c.endDate);endItem.append(endLabel, endDate);const lastItem = document.createElement("div");lastItem.className = "date-item";const lastLabel = document.createElement("span");lastLabel.className = "date-label";lastLabel.textContent = "Last Checked At:";const lastDate = document.createElement("span");lastDate.textContent = c.lastCheckedAt || "N/A";lastItem.append(lastLabel, lastDate);dates.append(startItem, endItem, lastItem);const teachersSection = document.createElement("div");teachersSection.className = "teachers-section";const teachersLabel = document.createElement("span");teachersLabel.className = "date-label";teachersLabel.textContent = "Teachers:";const teacherBox = document.createElement("div");teacherBox.className = "teacher-box";teacherBox.textContent = c.teachers || "Unknown";teachersSection.append(teachersLabel, teacherBox);dates.append(teachersSection);card.append(img, meta, dates);return card;}}
    function showDetails(it, kind) {{modalBody.innerHTML = "";const status = getStatus(it.startDate, it.endDate);if (status) {{const badge = createStatusBadge(status);modalBody.append(badge);}}const img = document.createElement("img");img.className = "thumb";img.alt = "";img.src = it.image || IMG_PH;modalBody.append(img);const meta = document.createElement("div");meta.className = "meta";const h3 = document.createElement("h3");h3.textContent = it.name;const p = document.createElement("p");p.textContent = kind === "batches" ? "Batch" : "Course";meta.append(h3, p);modalBody.append(meta);const dates = document.createElement("div");dates.className = "dates";const startItem = document.createElement("div");startItem.className = "date-item";const startLabel = document.createElement("span");startLabel.className = "date-label";startLabel.textContent = "Starts At:";const startDate = document.createElement("span");startDate.textContent = formatDate(it.startDate);startItem.append(startLabel, startDate);const endItem = document.createElement("div");endItem.className = "date-item";const endLabel = document.createElement("span");endLabel.className = "date-label";endLabel.textContent = kind === "batches" ? "Completed At:" : "Ends At:";const endDate = document.createElement("span");endDate.textContent = formatDate(it.endDate);endItem.append(endLabel, endDate);const lastItem = document.createElement("div");lastItem.className = "date-item";const lastLabel = document.createElement("span");lastLabel.className = "date-label";lastLabel.textContent = "Last Checked At:";const lastDate = document.createElement("span");lastDate.textContent = it.lastCheckedAt || "N/A";lastItem.append(lastLabel, lastDate);dates.append(startItem, endItem, lastItem);const teachersSection = document.createElement("div");teachersSection.className = "teachers-section";const teachersLabel = document.createElement("span");teachersLabel.className = "date-label";teachersLabel.textContent = "Teachers:";const teacherBox = document.createElement("div");teacherBox.className = "teacher-box";teacherBox.textContent = it.teachers || "Unknown";teachersSection.append(teachersLabel, teacherBox);dates.append(teachersSection);modalBody.append(dates);modalWatch.onclick = () => {{ window.open(it.url, '_blank'); }};modal.classList.add('show');}}
    async function fetchWithDisable(btn, url) {{if (btn) btn.disabled = true;const response = await fetch(url);if (btn) btn.disabled = false;const encryptedData = await response.json();if (encryptedData.encrypted) {{const decrypted = simpleDecrypt(encryptedData.data);if (!decrypted) {{console.error('Failed to decrypt data');return {{ data: [], total: 0 }};}}return decrypted;}}return encryptedData;}}
    async function renderEducators(reset = false) {{if (reset) {{ state.offsets.educators = 0; eduGrid.innerHTML = ""; eduLoad.innerHTML = ""; }}const skip = state.offsets.educators;const {{data, total}} = await fetchWithDisable(null, `/educators?skip=${{skip}}&limit=${{PAGE}}`);data.forEach(ed => eduGrid.append(educatorCard(ed)));state.offsets.educators += data.length;eduLoad.innerHTML = "";if (state.offsets.educators < total) {{const btn = document.createElement("button");btn.className = "load-more"; btn.textContent = `Load more (${{total - state.offsets.educators}} remaining)`;btn.addEventListener("click", async (e) => {{e.target.disabled = true;await renderEducators(false);e.target.disabled = false;}});eduLoad.append(btn);}}}}
    async function renderBatches(reset = false) {{if (reset) {{ state.offsets.batches = 0; batchGrid.innerHTML = ""; batchLoad.innerHTML = ""; }}const skip = state.offsets.batches;const {{data, total}} = await fetchWithDisable(null, `/batches?status=${{state.batchFilter}}&skip=${{skip}}&limit=${{PAGE}}`);data.forEach(b => batchGrid.append(batchCard(b)));state.offsets.batches += data.length;batchLoad.innerHTML = "";if (state.offsets.batches < total) {{const btn = document.createElement("button");btn.className = "load-more"; btn.textContent = `Load more (${{total - state.offsets.batches}} remaining)`;btn.addEventListener("click", async (e) => {{e.target.disabled = true;await renderBatches(false);e.target.disabled = false;}});batchLoad.append(btn);}}}}
    async function renderCourses(reset = false) {{if (reset) {{ state.offsets.courses = 0; courseGrid.innerHTML = ""; courseLoad.innerHTML = ""; }}const skip = state.offsets.courses;const {{data, total}} = await fetchWithDisable(null, `/courses?status=${{state.courseFilter}}&skip=${{skip}}&limit=${{PAGE}}`);data.forEach(c => courseGrid.append(courseCard(c)));state.offsets.courses += data.length;courseLoad.innerHTML = "";if (state.offsets.courses < total) {{const btn = document.createElement("button");btn.className = "load-more"; btn.textContent = `Load more (${{total - state.offsets.courses}} remaining)`;btn.addEventListener("click", async (e) => {{e.target.disabled = true;await renderCourses(false);e.target.disabled = false;}});courseLoad.append(btn);}}}}
    async function runSearch(q) {{const Q = q.trim();state.searchQuery = Q;state.searchOffsets = {{ educators: 0, batches: 0, courses: 0 }};sEdu.innerHTML = sBat.innerHTML = sCou.innerHTML = "";sEduLoad.innerHTML = sBatLoad.innerHTML = sCouLoad.innerHTML = "";if (!Q) {{panelSearch.hidden = true;panelEdu.hidden = state.tab !== "educators";panelBat.hidden = state.tab !== "batches";panelCou.hidden = state.tab !== "courses";return;}}panelSearch.hidden = false;panelEdu.hidden = panelBat.hidden = panelCou.hidden = true;await renderSearchGroup("educators", true);await renderSearchGroup("batches", true);await renderSearchGroup("courses", true);}}
    async function renderSearchGroup(group, reset = false) {{const map = {{educators: {{ list: sEdu, load: sEduLoad, card: (e) => educatorCard(e) }},batches: {{ list: sBat, load: sBatLoad, card: (b) => batchCard(b) }},courses: {{ list: sCou, load: sCouLoad, card: (c) => courseCard(c) }},}};const cfg = map[group];if (reset) {{ state.searchOffsets[group] = 0; cfg.list.innerHTML = ""; cfg.load.innerHTML = ""; }}const skip = state.searchOffsets[group];const endpoint = group === "educators" ? "search_educator" : group === "batches" ? "search_batch" : "search_courses";const {{data, total}} = await fetchWithDisable(null, `/${{endpoint}}?keyword=${{encodeURIComponent(state.searchQuery)}}&skip=${{skip}}&limit=${{PAGE}}`);data.forEach(item => cfg.list.append(cfg.card(item)));state.searchOffsets[group] += data.length;cfg.load.innerHTML = "";if (state.searchOffsets[group] < total) {{const btn = document.createElement("button");btn.className = "load-more"; btn.textContent = `Load more (${{total - state.searchOffsets[group]}} remaining)`;btn.addEventListener("click", async (e) => {{e.target.disabled = true;await renderSearchGroup(group, false);e.target.disabled = false;}});cfg.load.append(btn);}}}}
    searchInput.addEventListener("input", (e) => runSearch(e.target.value));
    function renderCurrent() {{if (state.tab === "educators") renderEducators(true);if (state.tab === "batches") renderBatches(true);if (state.tab === "courses") renderCourses(true);}}
    (function bg() {{const c = document.getElementById("bg-canvas");const ctx = c.getContext("2d");let w = 0, h = 0, rafId, t = 0;function resize() {{w = c.width = window.innerWidth;h = c.height = window.innerHeight;}}function draw() {{ctx.clearRect(0, 0, w, h);ctx.globalAlpha = 1;const grd = ctx.createLinearGradient(0, 0, w, h);grd.addColorStop(0, "rgba(46,168,255,0.04)");grd.addColorStop(1, "rgba(255,255,255,0.02)");ctx.fillStyle = grd;ctx.fillRect(0, 0, w, h);ctx.lineWidth = 1;ctx.strokeStyle = "rgba(255,255,255,0.06)";const spacing = 42;const offset = (t * 12) % spacing;for (let x = -w; x < w * 2; x += spacing) {{ctx.beginPath();ctx.moveTo(x + offset, 0);ctx.lineTo(x - h + offset, h);ctx.stroke();}}for (let y = -h; y < h * 2; y += spacing) {{ctx.beginPath();ctx.moveTo(0, y + offset);ctx.lineTo(w, y - w + offset);ctx.stroke();}}t += 0.002;rafId = requestAnimationFrame(draw);}}resize();window.addEventListener("resize", resize);draw();}})();
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.body.dataset.theme = savedTheme;
    themeToggle.classList.toggle("active", savedTheme === "light");
    themeToggle.addEventListener("click", () => {{const isLight = document.body.dataset.theme === "light";document.body.dataset.theme = isLight ? "dark" : "light";themeToggle.classList.toggle("active", !isLight);localStorage.setItem("theme", document.body.dataset.theme);}});
    window.addEventListener("scroll", () => {{backToTop.classList.toggle("show", window.scrollY > 300);}});
    backToTop.addEventListener("click", () => {{window.scrollTo({{ top: 0, behavior: "smooth" }});}});
    modalClose.addEventListener("click", () => {{ modal.classList.remove('show'); }});
    modal.addEventListener("click", (e) => {{ if (e.target === modal) modal.classList.remove('show'); }});
    selectTab("educators");
    renderCurrent();
  </script>
</body>
</html>"""

@app.get("/educators")
async def get_all_educators(skip: int = Query(0, ge=0), limit: int = Query(5, ge=1)):
    seen = set()
    educators = []
    for doc in educators_col.find({}, {"_id": 0}):
        uid = doc.get("uid", "")
        username = doc.get("username", "").lower()
        key = f"{uid}_{username}"
        if key in seen:
            continue
        seen.add(key)
        mapped = map_educator(doc)
        educators.append(mapped)
    educators.sort(key=lambda e: e["name"])
    total = len(educators)
    data = educators[skip: skip + limit]
    encrypted = encrypt_data({"data": data, "total": total})
    return JSONResponse({"encrypted": True, "data": encrypted})

@app.get("/batches")
async def get_all_batches(skip: int = Query(0, ge=0), limit: int = Query(5, ge=1), status: str = Query(None)):
    seen = set()
    batches = []
    for educator in educators_col.find({}, {"_id": 0, "batches": 1}):
        for batch in educator.get("batches", []):
            mapped = map_batch(batch)
            uid = mapped["id"]
            if uid in seen:
                continue
            seen.add(uid)
            batch_status = get_status(mapped)
            if not status or batch_status == status:
                batches.append(mapped)
    if status == "live":
        batches.sort(key=lambda b: datetime.fromisoformat((b["startDate"] or "0000-00-00T00:00:00Z").replace("Z", "+00:00")), reverse=True)
    elif status == "completed":
        batches.sort(key=lambda b: datetime.fromisoformat((b["endDate"] or "0000-00-00T00:00:00Z").replace("Z", "+00:00")), reverse=True)
    total = len(batches)
    data = batches[skip: skip + limit]
    encrypted = encrypt_data({"data": data, "total": total})
    return JSONResponse({"encrypted": True, "data": encrypted})

@app.get("/courses")
async def get_all_courses(skip: int = Query(0, ge=0), limit: int = Query(5, ge=1), status: str = Query(None)):
    seen = set()
    courses = []
    for educator in educators_col.find({}, {"_id": 0, "courses": 1}):
        for course in educator.get("courses", []):
            mapped = map_course(course)
            uid = mapped["id"]
            if uid in seen:
                continue
            seen.add(uid)
            course_status = get_status(mapped)
            if not status or course_status == status:
                courses.append(mapped)
    if status == "live":
        courses.sort(key=lambda c: datetime.fromisoformat((c["startDate"] or "0000-00-00T00:00:00Z").replace("Z", "+00:00")), reverse=True)
    elif status == "completed":
        courses.sort(key=lambda c: datetime.fromisoformat((c["endDate"] or "0000-00-00T00:00:00Z").replace("Z", "+00:00")), reverse=True)
    total = len(courses)
    data = courses[skip: skip + limit]
    encrypted = encrypt_data({"data": data, "total": total})
    return JSONResponse({"encrypted": True, "data": encrypted})

@app.get("/search_educator")
async def search_educator(keyword: str = Query(...), skip: int = Query(0, ge=0), limit: int = Query(5, ge=1)):
    query = {
        "$or": [
            {"first_name": {"$regex": keyword, "$options": "i"}},
            {"last_name": {"$regex": keyword, "$options": "i"}},
            {"username": {"$regex": keyword, "$options": "i"}}
        ]
    }
    seen = set()
    educators = []
    for doc in educators_col.find(query, {"_id": 0}):
        uid = doc.get("uid", "")
        username = doc.get("username", "").lower()
        key = f"{uid}_{username}"
        if key in seen:
            continue
        seen.add(key)
        mapped = map_educator(doc)
        educators.append(mapped)
    educators.sort(key=lambda e: e["name"])
    total = len(educators)
    data = educators[skip: skip + limit]
    encrypted = encrypt_data({"data": data, "total": total})
    return JSONResponse({"encrypted": True, "data": encrypted})

@app.get("/search_batch")
async def search_batch(keyword: str = Query(...), skip: int = Query(0, ge=0), limit: int = Query(5, ge=1)):
    seen = set()
    batches = []
    query = {
        "$or": [
            {"batches.name": {"$regex": keyword, "$options": "i"}},
            {"batches.teachers": {"$regex": keyword, "$options": "i"}}
        ]
    }
    for educator in educators_col.find(query, {"_id": 0, "batches": 1}):
        for batch in educator.get("batches", []):
            if keyword.lower() in batch["name"].lower() or (batch.get("teachers") and keyword.lower() in batch["teachers"].lower()):
                mapped = map_batch(batch)
                uid = mapped["id"]
                if uid in seen:
                    continue
                seen.add(uid)
                batches.append(mapped)
    total = len(batches)
    data = batches[skip: skip + limit]
    encrypted = encrypt_data({"data": data, "total": total})
    return JSONResponse({"encrypted": True, "data": encrypted})

@app.get("/search_courses")
async def search_courses(keyword: str = Query(...), skip: int = Query(0, ge=0), limit: int = Query(5, ge=1)):
    seen = set()
    courses = []
    query = {
        "$or": [
            {"courses.name": {"$regex": keyword, "$options": "i"}},
            {"courses.teachers": {"$regex": keyword, "$options": "i"}}
        ]
    }
    for educator in educators_col.find(query, {"_id": 0, "courses": 1}):
        for course in educator.get("courses", []):
            if keyword.lower() in course["name"].lower() or (course.get("teachers") and keyword.lower() in course["teachers"].lower()):
                mapped = map_course(course)
                uid = mapped["id"]
                if uid in seen:
                    continue
                seen.add(uid)
                courses.append(mapped)
    total = len(courses)
    data = courses[skip: skip + limit]
    encrypted = encrypt_data({"data": data, "total": total})
    return JSONResponse({"encrypted": True, "data": encrypted})
