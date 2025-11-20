from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, HTMLResponse
from pymongo import MongoClient
from datetime import datetime, timezone
import json
import base64
import os

app = FastAPI(title="MongoDB Data Server")

# 🔐 Secret Key - CHANGE THIS!
SECRET_KEY = "YourSuperSecret@123"

def xor_encrypt(data: str, key: str) -> str:
    """Simple XOR encryption"""
    encrypted = []
    for i in range(len(data)):
        encrypted.append(chr(ord(data[i]) ^ ord(key[i % len(key)])))
    return ''.join(encrypted)

def encode_data(obj: dict) -> str:
    """Encrypt and encode data"""
    json_str = json.dumps(obj)
    encrypted = xor_encrypt(json_str, SECRET_KEY)
    return base64.b64encode(encrypted.encode('latin-1')).decode('utf-8')

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
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>𝗖𝗛𝗨𝗡𝗔𝗖𝗔𝗗𝗘𝗠𝗬 😈</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --primary-light: #818cf8;
  --secondary: #ec4899;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --dark: #0f172a;
  --dark-light: #1e293b;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --border: #334155;
  --card-bg: #1e293b;
  --input-bg: #0f172a;
  --shadow: rgba(0, 0, 0, 0.3);
}

[data-theme="light"] {
  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --primary-light: #818cf8;
  --secondary: #ec4899;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --dark: #ffffff;
  --dark-light: #f8fafc;
  --text: #0f172a;
  --text-muted: #64748b;
  --border: #e2e8f0;
  --card-bg: #ffffff;
  --input-bg: #f8fafc;
  --shadow: rgba(0, 0, 0, 0.1);
}

body {
  font-family: 'Inter', sans-serif;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: var(--text);
  min-height: 100vh;
  transition: all 0.3s ease;
}

[data-theme="light"] body {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* Header Styles */
.header {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px var(--shadow);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border);
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 20px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 900;
  color: white;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

.logo-text h1 {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 5px;
}

.logo-text p {
  color: var(--text-muted);
  font-size: 14px;
}

/* Theme Toggle */
.theme-toggle {
  width: 60px;
  height: 32px;
  background: var(--input-bg);
  border-radius: 16px;
  position: relative;
  cursor: pointer;
  border: 2px solid var(--border);
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  border-color: var(--primary);
}

.theme-toggle-slider {
  position: absolute;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: transform 0.3s ease;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
}

.theme-toggle.active .theme-toggle-slider {
  transform: translateX(28px);
}

/* Promo Banner */
.promo-banner {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(236, 72, 153, 0.2));
  border-radius: 15px;
  padding: 20px 25px;
  margin-bottom: 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  border: 1px solid var(--border);
  flex-wrap: wrap;
}

.promo-content h2 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 5px;
}

.promo-content p {
  color: var(--text-muted);
  font-size: 14px;
}

.promo-btn {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  padding: 12px 28px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.promo-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
}

/* Search Bar */
.search-wrapper {
  position: relative;
  margin-bottom: 25px;
}

.search-input {
  width: 100%;
  padding: 16px 50px 16px 20px;
  background: var(--input-bg);
  border: 2px solid var(--border);
  border-radius: 12px;
  color: var(--text);
  font-size: 15px;
  transition: all 0.3s ease;
  outline: none;
}

.search-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.search-icon {
  position: absolute;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 20px;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.tab {
  padding: 12px 24px;
  background: var(--input-bg);
  border: 2px solid var(--border);
  border-radius: 10px;
  color: var(--text);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 15px;
}

.tab:hover {
  border-color: var(--primary-light);
  transform: translateY(-2px);
}

.tab.active {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

/* Sub Tabs */
.sub-tabs {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.sub-tab {
  padding: 10px 20px;
  background: var(--input-bg);
  border: 2px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.sub-tab:hover {
  border-color: var(--primary-light);
}

.sub-tab.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

/* Section Header */
.section-header {
  margin: 30px 0 20px 0;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
}

/* Grid */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 30px;
}

/* Card */
.card {
  background: var(--card-bg);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px var(--shadow);
  border-color: var(--primary);
}

.card-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  background: var(--input-bg);
}

.card-body {
  padding: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text);
}

.card-subtitle {
  color: var(--text-muted);
  font-size: 14px;
  margin-bottom: 15px;
}

/* Educator Card Specific */
.educator-header {
  display: flex;
  gap: 15px;
  align-items: center;
  padding: 20px;
}

.educator-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--border);
}

.educator-info {
  flex: 1;
}

.educator-actions {
  display: flex;
  gap: 10px;
  padding: 0 20px 20px 20px;
}

.action-btn {
  flex: 1;
  padding: 12px;
  background: var(--input-bg);
  border: 2px solid var(--border);
  border-radius: 10px;
  color: var(--text);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.action-btn:hover {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}

.action-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

/* Panel */
.panel {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.panel.show {
  max-height: 1000px;
}

.panel-content {
  padding: 0 20px 20px 20px;
  border-top: 1px solid var(--border);
  padding-top: 15px;
}

.list-item {
  display: flex;
  gap: 15px;
  padding: 12px;
  background: var(--input-bg);
  border-radius: 10px;
  margin-bottom: 10px;
  align-items: center;
  text-decoration: none;
  color: var(--text);
  border: 1px solid var(--border);
  transition: all 0.3s ease;
  position: relative;
}

.list-item:hover {
  border-color: var(--primary);
  transform: translateX(5px);
}

.list-item-image {
  width: 60px;
  height: 45px;
  object-fit: cover;
  border-radius: 8px;
}

.list-item-title {
  flex: 1;
  font-weight: 600;
}

.list-item-badge {
  padding: 4px 10px;
  background: var(--primary);
  color: white;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

/* Status Badge */
.status-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 6px;
  z-index: 10;
}

.status-badge.live {
  background: rgba(239, 68, 68, 0.2);
  color: var(--danger);
  border: 1px solid var(--danger);
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.2);
  color: var(--success);
  border: 1px solid var(--success);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.status-dot.live {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Info Section */
.info-grid {
  display: grid;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid var(--border);
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.info-label {
  color: var(--text-muted);
  font-weight: 600;
}

.info-value {
  color: var(--text);
  font-weight: 500;
}

.teacher-tag {
  margin-top: 12px;
  padding: 10px 15px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid var(--primary);
  border-radius: 8px;
  color: var(--primary);
  font-size: 13px;
  font-weight: 600;
}

/* Load More */
.load-more-wrapper {
  text-align: center;
  margin: 30px 0;
}

.load-more {
  padding: 14px 32px;
  background: var(--card-bg);
  border: 2px solid var(--border);
  border-radius: 12px;
  color: var(--text);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 15px;
}

.load-more:hover {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
}

/* Back to Top */
.back-to-top {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
  font-size: 24px;
  z-index: 1000;
}

.back-to-top.show {
  opacity: 1;
  visibility: visible;
}

.back-to-top:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(99, 102, 241, 0.5);
}

/* Modal */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal.show {
  display: flex;
}

.modal-content {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 30px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  border: 1px solid var(--border);
}

.modal-close {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 35px;
  height: 35px;
  background: var(--input-bg);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text);
  font-size: 20px;
  border: 1px solid var(--border);
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: var(--danger);
  border-color: var(--danger);
  color: white;
}

.modal-image {
  width: 100%;
  height: 250px;
  object-fit: cover;
  border-radius: 15px;
  margin-bottom: 20px;
}

.watch-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  margin-top: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
}

.watch-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
}

/* Footer */
.footer {
  text-align: center;
  padding: 30px;
  color: var(--text-muted);
  font-size: 14px;
  margin-top: 50px;
}

/* Responsive */
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
  
  .header-top {
    flex-direction: column;
    text-align: center;
  }
  
  .logo-section {
    flex-direction: column;
  }
  
  .promo-banner {
    flex-direction: column;
    text-align: center;
  }
}

/* Hidden */
[hidden] {
  display: none !important;
}

/* Smooth Scrollbar */
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: var(--input-bg);
}

::-webkit-scrollbar-thumb {
  background: var(--primary);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary-dark);
}
</style>
</head>
<body data-theme="dark">
<div class="container">
  <!-- Header -->
  <div class="header">
    <div class="header-top">
      <div class="logo-section">
        <div class="logo">C</div>
        <div class="logo-text">
          <h1>CHUNACADEMY</h1>
          <p>Your Ultimate Learning Platform 🚀</p>
        </div>
      </div>
      <div class="theme-toggle" id="themeToggle">
        <div class="theme-toggle-slider"></div>
      </div>
    </div>
    
    <!-- Promo Banner -->
    <div class="promo-banner">
      <div class="promo-content">
        <h2>🎯 Explore Our Main Website</h2>
        <p>Discover amazing free resources and tools</p>
      </div>
      <a href="https://yashyasag.github.io/hiddens" class="promo-btn">Visit Now →</a>
    </div>
    
    <!-- Search -->
    <div class="search-wrapper">
      <input type="text" class="search-input" id="searchInput" placeholder="Search educators, batches, courses...">
      <span class="search-icon">🔍</span>
    </div>
    
    <!-- Tabs -->
    <div class="tabs">
      <button class="tab active" data-tab="educators">👨‍🏫 Educators</button>
      <button class="tab" data-tab="batches">📚 Batches</button>
      <button class="tab" data-tab="courses">🎓 Courses</button>
    </div>
  </div>
  
  <!-- Main Content -->
  <main id="mainContent">
    <!-- Educators Section -->
    <section id="educatorsSection">
      <div class="section-header">
        <h2>📖 All Educators</h2>
      </div>
      <div class="grid" id="educatorsGrid"></div>
      <div class="load-more-wrapper" id="educatorsLoadMore"></div>
    </section>
    
    <!-- Batches Section -->
    <section id="batchesSection" hidden>
      <div class="section-header">
        <h2>📚 Batches</h2>
      </div>
      <div class="sub-tabs">
        <button class="sub-tab active" data-filter="live">🔴 Live Running</button>
        <button class="sub-tab" data-filter="completed">✅ Completed</button>
      </div>
      <div class="grid" id="batchesGrid"></div>
      <div class="load-more-wrapper" id="batchesLoadMore"></div>
    </section>
    
    <!-- Courses Section -->
    <section id="coursesSection" hidden>
      <div class="section-header">
        <h2>🎓 Courses</h2>
      </div>
      <div class="sub-tabs">
        <button class="sub-tab active" data-filter="live">🔴 Live Running</button>
        <button class="sub-tab" data-filter="completed">✅ Completed</button>
      </div>
      <div class="grid" id="coursesGrid"></div>
      <div class="load-more-wrapper" id="coursesLoadMore"></div>
    </section>
    
    <!-- Search Results Section -->
    <section id="searchSection" hidden>
      <div class="section-header">
        <h2>🔍 Search Results</h2>
      </div>
      
      <h3 style="margin: 20px 0 10px 0; color: var(--text);">Educators</h3>
      <div class="grid" id="searchEducatorsGrid"></div>
      <div class="load-more-wrapper" id="searchEducatorsLoadMore"></div>
      
      <h3 style="margin: 20px 0 10px 0; color: var(--text);">Batches</h3>
      <div class="grid" id="searchBatchesGrid"></div>
      <div class="load-more-wrapper" id="searchBatchesLoadMore"></div>
      
      <h3 style="margin: 20px 0 10px 0; color: var(--text);">Courses</h3>
      <div class="grid" id="searchCoursesGrid"></div>
      <div class="load-more-wrapper" id="searchCoursesLoadMore"></div>
    </section>
  </main>
  
  <!-- Footer -->
  <div class="footer">
    <p>🔐 All data is encrypted and secured | Made with ❤️ by CHUNACADEMY</p>
  </div>
</div>

<!-- Back to Top -->
<div class="back-to-top" id="backToTop">↑</div>

<!-- Modal -->
<div class="modal" id="modal">
  <div class="modal-content">
    <div class="modal-close" id="modalClose">×</div>
    <div id="modalBody"></div>
    <button class="watch-btn" id="watchBtn">🎬 Watch Now</button>
  </div>
</div>

<script>
const KEY='""" + SECRET_KEY + """';
function xorDecrypt(e,t){let r='';for(let n=0;n<e.length;n++)r+=String.fromCharCode(e.charCodeAt(n)^t.charCodeAt(n%t.length));return r}
function decryptData(e){try{const t=atob(e),r=xorDecrypt(t,KEY);return JSON.parse(r)}catch(e){return console.error('Decrypt error:',e),null}}

const IMG_USER="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='70' height='70'%3E%3Ccircle cx='35' cy='35' r='35' fill='%236366f1'/%3E%3Ctext x='50%25' y='50%25' font-size='30' text-anchor='middle' dy='.3em' fill='white'%3E👤%3C/text%3E%3C/svg%3E";
const IMG_PH="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='200'%3E%3Crect fill='%231e293b' width='400' height='200'/%3E%3Ctext x='50%25' y='50%25' font-size='40' text-anchor='middle' dy='.3em' fill='%2364748b'%3E📚%3C/text%3E%3C/svg%3E";

const TODAY = new Date();
const PAGE = 5;

function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  try {
    const date = new Date(dateStr);
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const mins = String(date.getMinutes()).padStart(2, '0');
    return `${day} ${month} ${year}, ${hours}:${mins}`;
  } catch (e) {
    return dateStr;
  }
}

function getStatus(startDate, endDate) {
  if (!startDate || !endDate) return null;
  const start = new Date(startDate);
  const end = new Date(endDate);
  if (TODAY >= start && TODAY <= end) return 'live';
  if (TODAY > end) return 'completed';
  return null;
}

const state = {
  tab: "educators",
  batchFilter: "live",
  courseFilter: "live",
  offsets: { educators: 0, batches: 0, courses: 0 },
  searchQuery: "",
  searchOffsets: { educators: 0, batches: 0, courses: 0 },
  panels: {}
};

const lazyObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && entry.target.dataset.src) {
      entry.target.src = entry.target.dataset.src;
      entry.target.removeAttribute('data-src');
    }
  });
}, { rootMargin: "100px" });

// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('theme') || 'dark';
document.body.dataset.theme = savedTheme;
if (savedTheme === 'light') themeToggle.classList.add('active');

themeToggle.addEventListener('click', () => {
  const current = document.body.dataset.theme;
  const newTheme = current === 'dark' ? 'light' : 'dark';
  document.body.dataset.theme = newTheme;
  localStorage.setItem('theme', newTheme);
  themeToggle.classList.toggle('active');
});

// Tab Switching
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const tabName = tab.dataset.tab;
    state.tab = tabName;
    
    document.getElementById('educatorsSection').hidden = tabName !== 'educators';
    document.getElementById('batchesSection').hidden = tabName !== 'batches';
    document.getElementById('coursesSection').hidden = tabName !== 'courses';
    document.getElementById('searchSection').hidden = true;
    
    renderCurrent();
  });
});

// Sub-tab Switching (Batches)
document.querySelectorAll('#batchesSection .sub-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('#batchesSection .sub-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    state.batchFilter = tab.dataset.filter;
    renderBatches(true);
  });
});

// Sub-tab Switching (Courses)
document.querySelectorAll('#coursesSection .sub-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('#coursesSection .sub-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    state.courseFilter = tab.dataset.filter;
    renderCourses(true);
  });
});

// Educator Card
function createEducatorCard(educator) {
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    <div class="educator-header">
      <img class="educator-avatar" data-src="${educator.image || IMG_USER}" alt="${educator.name}">
      <div class="educator-info">
        <div class="card-title">${educator.name}</div>
        <div class="card-subtitle">${educator.subject}</div>
      </div>
    </div>
    <div class="educator-actions">
      <button class="action-btn" data-type="batches">📚 Batches (${educator.batches.length})</button>
      <button class="action-btn" data-type="courses">🎓 Courses (${educator.courses.length})</button>
    </div>
    <div class="panel" id="panel-${educator.id}">
      <div class="panel-content" id="panel-content-${educator.id}"></div>
    </div>
  `;
  
  const avatar = card.querySelector('.educator-avatar');
  lazyObserver.observe(avatar);
  
  card.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const type = btn.dataset.type;
      togglePanel(educator, type, card);
    });
  });
  
  return card;
}

function togglePanel(educator, type, card) {
  const panel = card.querySelector('.panel');
  const panelContent = card.querySelector('.panel-content');
  const buttons = card.querySelectorAll('.action-btn');
  
  const isOpen = panel.classList.contains('show') && state.panels[educator.id]?.mode === type;
  
  if (isOpen) {
    panel.classList.remove('show');
    buttons.forEach(b => b.classList.remove('active'));
  } else {
    panel.classList.add('show');
    buttons.forEach(b => b.classList.remove('active'));
    card.querySelector(`[data-type="${type}"]`).classList.add('active');
    
    state.panels[educator.id] = { mode: type, offset: 0 };
    renderPanel(educator, type, panelContent);
  }
}

function renderPanel(educator, type, container) {
  const items = type === 'batches' ? educator.batches : educator.courses;
  const offset = state.panels[educator.id].offset;
  const limit = 5;
  const displayItems = items.slice(offset, offset + limit);
  
  if (offset === 0) container.innerHTML = '';
  
  displayItems.forEach(item => {
    const listItem = document.createElement('a');
    listItem.className = 'list-item';
    listItem.href = item.url;
    listItem.target = '_blank';
    
    const status = getStatus(item.startDate, item.endDate);
    const statusBadge = status ? `<span class="list-item-badge ${status}">${status === 'live' ? '🔴 Live' : '✅ Done'}</span>` : '';
    
    listItem.innerHTML = `
      <img class="list-item-image" data-src="${item.image || IMG_PH}" alt="${item.name}">
      <div class="list-item-title">${item.name}</div>
      ${statusBadge}
    `;
    
    const img = listItem.querySelector('.list-item-image');
    lazyObserver.observe(img);
    
    listItem.addEventListener('click', (e) => {
      if (e.target.classList.contains('list-item-badge')) {
        e.preventDefault();
        showModal(item, type);
      }
    });
    
    container.appendChild(listItem);
  });
  
  state.panels[educator.id].offset += displayItems.length;
  
  if (state.panels[educator.id].offset < items.length) {
    const loadMore = document.createElement('button');
    loadMore.className = 'load-more';
    loadMore.textContent = `Load More (${items.length - state.panels[educator.id].offset} remaining)`;
    loadMore.addEventListener('click', () => {
      loadMore.remove();
      renderPanel(educator, type, container);
    });
    container.appendChild(loadMore);
  }
}

// Batch/Course Card
function createBatchCard(batch) {
  const status = getStatus(batch.startDate, batch.endDate);
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    ${status ? `<div class="status-badge ${status}"><span class="status-dot ${status}"></span>${status === 'live' ? 'Live Running' : 'Completed'}</div>` : ''}
    <img class="card-image" data-src="${batch.image || IMG_PH}" alt="${batch.name}">
    <div class="card-body">
      <div class="card-title">${batch.name}</div>
      <div class="card-subtitle">📚 Batch</div>
      <div class="info-grid">
        <div class="info-row">
          <span class="info-label">Start Date:</span>
          <span class="info-value">${formatDate(batch.startDate)}</span>
        </div>
        <div class="info-row">
          <span class="info-label">End Date:</span>
          <span class="info-value">${formatDate(batch.endDate)}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Last Checked:</span>
          <span class="info-value">${batch.lastCheckedAt || 'N/A'}</span>
        </div>
      </div>
      <div class="teacher-tag">👨‍🏫 ${batch.teachers || 'Unknown'}</div>
    </div>
  `;
  
  const img = card.querySelector('.card-image');
  lazyObserver.observe(img);
  
  card.addEventListener('click', () => window.location.href = batch.url);
  
  return card;
}

function createCourseCard(course) {
  const status = getStatus(course.startDate, course.endDate);
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    ${status ? `<div class="status-badge ${status}"><span class="status-dot ${status}"></span>${status === 'live' ? 'Live Running' : 'Completed'}</div>` : ''}
    <img class="card-image" data-src="${course.image || IMG_PH}" alt="${course.name}">
    <div class="card-body">
      <div class="card-title">${course.name}</div>
      <div class="card-subtitle">🎓 Course</div>
      <div class="info-grid">
        <div class="info-row">
          <span class="info-label">Start Date:</span>
          <span class="info-value">${formatDate(course.startDate)}</span>
        </div>
        <div class="info-row">
          <span class="info-label">End Date:</span>
          <span class="info-value">${formatDate(course.endDate)}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Last Checked:</span>
          <span class="info-value">${course.lastCheckedAt || 'N/A'}</span>
        </div>
      </div>
      <div class="teacher-tag">👨‍🏫 ${course.teachers || 'Unknown'}</div>
    </div>
  `;
  
  const img = card.querySelector('.card-image');
  lazyObserver.observe(img);
  
  card.addEventListener('click', () => window.location.href = course.url);
  
  return card;
}

// Modal
function showModal(item, type) {
  const modal = document.getElementById('modal');
  const modalBody = document.getElementById('modalBody');
  const watchBtn = document.getElementById('watchBtn');
  
  const status = getStatus(item.startDate, item.endDate);
  
  modalBody.innerHTML = `
    ${status ? `<div class="status-badge ${status}" style="position: static; margin-bottom: 15px;"><span class="status-dot ${status}"></span>${status === 'live' ? 'Live Running' : 'Completed'}</div>` : ''}
    <img class="modal-image" src="${item.image || IMG_PH}" alt="${item.name}">
    <div class="card-title" style="margin-bottom: 10px;">${item.name}</div>
    <div class="card-subtitle" style="margin-bottom: 20px;">${type === 'batches' ? '📚 Batch' : '🎓 Course'}</div>
    <div class="info-grid">
      <div class="info-row">
        <span class="info-label">Start Date:</span>
        <span class="info-value">${formatDate(item.startDate)}</span>
      </div>
      <div class="info-row">
        <span class="info-label">End Date:</span>
        <span class="info-value">${formatDate(item.endDate)}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Last Checked:</span>
        <span class="info-value">${item.lastCheckedAt || 'N/A'}</span>
      </div>
    </div>
    <div class="teacher-tag">👨‍🏫 ${item.teachers || 'Unknown'}</div>
  `;
  
  watchBtn.onclick = () => window.open(item.url, '_blank');
  modal.classList.add('show');
}

document.getElementById('modalClose').addEventListener('click', () => {
  document.getElementById('modal').classList.remove('show');
});

document.getElementById('modal').addEventListener('click', (e) => {
  if (e.target.id === 'modal') {
    document.getElementById('modal').classList.remove('show');
  }
});

// Fetch Data
async function fetchData(url) {
  const response = await fetch(url);
  const encrypted = await response.json();
  if (encrypted.encrypted) {
    return decryptData(encrypted.data);
  }
  return encrypted;
}

// Render Functions
async function renderEducators(reset = false) {
  const grid = document.getElementById('educatorsGrid');
  const loadMore = document.getElementById('educatorsLoadMore');
  
  if (reset) {
    state.offsets.educators = 0;
    grid.innerHTML = '';
    loadMore.innerHTML = '';
  }
  
  const { data, total } = await fetchData(`/educators?skip=${state.offsets.educators}&limit=${PAGE}`);
  data.forEach(educator => grid.appendChild(createEducatorCard(educator)));
  
  state.offsets.educators += data.length;
  loadMore.innerHTML = '';
  
  if (state.offsets.educators < total) {
    const btn = document.createElement('button');
    btn.className = 'load-more';
    btn.textContent = `Load More (${total - state.offsets.educators} remaining)`;
    btn.addEventListener('click', () => renderEducators(false));
    loadMore.appendChild(btn);
  }
}

async function renderBatches(reset = false) {
  const grid = document.getElementById('batchesGrid');
  const loadMore = document.getElementById('batchesLoadMore');
  
  if (reset) {
    state.offsets.batches = 0;
    grid.innerHTML = '';
    loadMore.innerHTML = '';
  }
  
  const { data, total } = await fetchData(`/batches?status=${state.batchFilter}&skip=${state.offsets.batches}&limit=${PAGE}`);
  data.forEach(batch => grid.appendChild(createBatchCard(batch)));
  
  state.offsets.batches += data.length;
  loadMore.innerHTML = '';
  
  if (state.offsets.batches < total) {
    const btn = document.createElement('button');
    btn.className = 'load-more';
    btn.textContent = `Load More (${total - state.offsets.batches} remaining)`;
    btn.addEventListener('click', () => renderBatches(false));
    loadMore.appendChild(btn);
  }
}

async function renderCourses(reset = false) {
  const grid = document.getElementById('coursesGrid');
  const loadMore = document.getElementById('coursesLoadMore');
  
  if (reset) {
    state.offsets.courses = 0;
    grid.innerHTML = '';
    loadMore.innerHTML = '';
  }
  
  const { data, total } = await fetchData(`/courses?status=${state.courseFilter}&skip=${state.offsets.courses}&limit=${PAGE}`);
  data.forEach(course => grid.appendChild(createCourseCard(course)));
  
  state.offsets.courses += data.length;
  loadMore.innerHTML = '';
  
  if (state.offsets.courses < total) {
    const btn = document.createElement('button');
    btn.className = 'load-more';
    btn.textContent = `Load More (${total - state.offsets.courses} remaining)`;
    btn.addEventListener('click', () => renderCourses(false));
    loadMore.appendChild(btn);
  }
}

function renderCurrent() {
  if (state.tab === 'educators') renderEducators(true);
  if (state.tab === 'batches') renderBatches(true);
  if (state.tab === 'courses') renderCourses(true);
}

// Search
let searchTimeout;
document.getElementById('searchInput').addEventListener('input', (e) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => runSearch(e.target.value), 500);
});

async function runSearch(query) {
  const q = query.trim();
  state.searchQuery = q;
  
  if (!q) {
    document.getElementById('searchSection').hidden = true;
    document.getElementById('educatorsSection').hidden = state.tab !== 'educators';
    document.getElementById('batchesSection').hidden = state.tab !== 'batches';
    document.getElementById('coursesSection').hidden = state.tab !== 'courses';
    return;
  }
  
  document.getElementById('searchSection').hidden = false;
  document.getElementById('educatorsSection').hidden = true;
  document.getElementById('batchesSection').hidden = true;
  document.getElementById('coursesSection').hidden = true;
  
  state.searchOffsets = { educators: 0, batches: 0, courses: 0 };
  
  await renderSearchEducators(true);
  await renderSearchBatches(true);
  await renderSearchCourses(true);
}

async function renderSearchEducators(reset = false) {
  const grid = document.getElementById('searchEducatorsGrid');
  const loadMore = document.getElementById('searchEducatorsLoadMore');
  
  if (reset) {
    grid.innerHTML = '';
    loadMore.innerHTML = '';
  }
  
  const { data, total } = await fetchData(`/search_educator?keyword=${encodeURIComponent(state.searchQuery)}&skip=${state.searchOffsets.educators}&limit=${PAGE}`);
  data.forEach(educator => grid.appendChild(createEducatorCard(educator)));
  
  state.searchOffsets.educators += data.length;
  loadMore.innerHTML = '';
  
  if (state.searchOffsets.educators < total) {
    const btn = document.createElement('button');
    btn.className = 'load-more';
    btn.textContent = `Load More (${total - state.searchOffsets.educators} remaining)`;
    btn.addEventListener('click', () => renderSearchEducators(false));
    loadMore.appendChild(btn);
  }
}

async function renderSearchBatches(reset = false) {
  const grid = document.getElementById('searchBatchesGrid');
  const loadMore = document.getElementById('searchBatchesLoadMore');
  
  if (reset) {
    grid.innerHTML = '';
    loadMore.innerHTML = '';
  }
  
  const { data, total } = await fetchData(`/search_batch?keyword=${encodeURIComponent(state.searchQuery)}&skip=${state.searchOffsets.batches}&limit=${PAGE}`);
  data.forEach(batch => grid.appendChild(createBatchCard(batch)));
  
  state.searchOffsets.batches += data.length;
  loadMore.innerHTML = '';
  
  if (state.searchOffsets.batches < total) {
    const btn = document.createElement('button');
    btn.className = 'load-more';
    btn.textContent = `Load More (${total - state.searchOffsets.batches} remaining)`;
    btn.addEventListener('click', () => renderSearchBatches(false));
    loadMore.appendChild(btn);
  }
}

async function renderSearchCourses(reset = false) {
  const grid = document.getElementById('searchCoursesGrid');
  const loadMore = document.getElementById('searchCoursesLoadMore');
  
  if (reset) {
    grid.innerHTML = '';
    loadMore.innerHTML = '';
  }
  
  const { data, total } = await fetchData(`/search_courses?keyword=${encodeURIComponent(state.searchQuery)}&skip=${state.searchOffsets.courses}&limit=${PAGE}`);
  data.forEach(course => grid.appendChild(createCourseCard(course)));
  
  state.searchOffsets.courses += data.length;
  loadMore.innerHTML = '';
  
  if (state.searchOffsets.courses < total) {
    const btn = document.createElement('button');
    btn.className = 'load-more';
    btn.textContent = `Load More (${total - state.searchOffsets.courses} remaining)`;
    btn.addEventListener('click', () => renderSearchCourses(false));
    loadMore.appendChild(btn);
  }
}

// Back to Top
const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', () => {
  backToTop.classList.toggle('show', window.scrollY > 300);
});
backToTop.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Initialize
renderEducators(true);
</script>
</body>
</html>"""
    return html_content

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
    encrypted = encode_data({"data": data, "total": total})
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
    encrypted = encode_data({"data": data, "total": total})
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
    encrypted = encode_data({"data": data, "total": total})
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
    encrypted = encode_data({"data": data, "total": total})
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
    encrypted = encode_data({"data": data, "total": total})
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
    encrypted = encode_data({"data": data, "total": total})
    return JSONResponse({"encrypted": True, "data": encrypted})
