# 🏏 Cricbuzz LiveStats: Real-Time Cricket Insights & SQL-Based Analytics

**Skills:** Python • SQL • Streamlit • JSON • REST API  
**Domain:** Sports Analytics

## 🚀 What you get
- ⚡ Real-time updates from Cricbuzz (via RapidAPI)
- 📊 Top player stats visualization
- 🔍 25 SQL practice queries (easy → advanced)
- 🛠️ CRUD UI (players & matches)
- 🗄️ DB-agnostic setup (SQLite by default)

## 📦 Setup
```bash
# 1) Create & activate venv (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Configure environment
cp .env.example .env   # or copy manually on Windows
# Edit .env and place your RapidAPI key for Cricbuzz
# RAPIDAPI_KEY=... (from RapidAPI)
# RAPIDAPI_HOST=cricbuzz-cricket.p.rapidapi.com

# 4) (Optional) Seed local DB with sample data
python -m utils.seed

# 5) Run the app
streamlit run streamlit_app.py
```

## 🔑 RapidAPI (Cricbuzz Cricket) — How to get API key
1. Go to RapidAPI, subscribe to **Cricbuzz Cricket** API.
2. Copy your key → paste into `.env` as `RAPIDAPI_KEY`.
3. Host is usually `cricbuzz-cricket.p.rapidapi.com` (already set).

## 🧭 App Structure
- **Home**: project overview
- **Live Matches**: real-time scoreboard from API
- **Top Player Stats**: highlights from API
- **SQL Analytics**: run 25 curated SQL queries
- **CRUD**: add/update/delete Players & Matches

## 🗃️ Database
- Default: SQLite (`cricbuzz_livestats.db`)
- Change DB by editing `DATABASE_URL` in `.env`

## ✅ Coding Standards
- PEP 8, error handling, dotenv, modular services

## 📁 Folder Tree
```
cricbuzz_livestats/
├─ .env.example
├─ .env
├─ requirements.txt
├─ README.md
├─ streamlit_app.py
├─ pages/
│  ├─ 1_🏠_Home.py
│  ├─ 2_📡_Live_Matches.py
│  ├─ 3_⭐_Top_Player_Stats.py
│  ├─ 4_🧠_SQL_Analytics.py
│  └─ 5_🛠️_CRUD_Operations.py
├─ utils/
│  ├─ __init__.py
│  ├─ api.py
│  ├─ db_connection.py
│  ├─ helpers.py
│  ├─ models.py
│  ├─ seed.py
│  └─ sql_queries.py
└─ data/
   ├─ sample_players.json
   └─ sample_matches.json
```

## 🧮 Notes
- API rate-limits: handled with try/except + user-visible errors.
- If API calls fail, pages still render and show cached/sample content.
- SQL pages only run queries if related tables exist.
