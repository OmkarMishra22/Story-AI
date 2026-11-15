# Story AL — Narrative World Engine & Cinematic Voice Studio

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/framework-Flask_3.0+-000000.svg?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Vercel](https://img.shields.io/badge/deploy-Vercel_Ready-000000.svg?style=flat&logo=vercel&logoColor=white)](https://vercel.com/)
[![Audio](https://img.shields.io/badge/audio-Neural_Speech_Synthesis-FF6B6B.svg?style=flat)](https://github.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

> **The living memory engine for fiction authors, novelists, and worldbuilders.**  
> Keep your world rules straight, query your canon with zero hallucinations, catch plot contradictions before your readers do, and listen to multi-character dialogue performed with cinematic voice casting.

---

## 🌟 Overview

**Story AL** is a specialized creative writing atelier built to solve the three hardest problems in long-form fiction and worldbuilding:

1. **Canon Drift & Plot Holes**: As manuscripts grow to hundreds of pages, keeping track of character status, travel distances, magical constraints, and historical timelines becomes overwhelming.
2. **AI Hallucinations**: Standard AI assistants invent plausible-sounding details that contradict established lore. Story AL strictly grounds every answer in your confirmed Story Bible.
3. **Dialogue Pacing & Character Voicing**: Writers often struggle to hear whether dialogue sounds distinct across different characters. Story AL provides a built-in **Cinematic Voice Studio** with 16 character voice archetypes, real-time emotion prosody modulation, dynamic audio telemetry, and line-by-line screenplay playback.

---

## 🏛️ Core Features

### 1. 📖 Story Bible Canon Memory
- Catalog characters, factions, places, artifacts, historical milestones, and immutable world rules.
- Fast categorization and tag-based filtering.
- Visual distinction between confirmed canon facts and working notes.
- Instant JSON import and export for full portability and offline backup.

### 2. 🔍 Ask Your Canon (Zero-Hallucination Q&A)
- Interrogate your world lore with natural language queries.
- **Strict Canon Grounding**: Answers cite exact Story Bible entries and rules.
- **Honest Ignorance**: If a question involves details not yet written into your Story Bible, Story AL explicitly states that the detail has not been established rather than inventing false facts.

### 3. 🛡️ Continuity & Conflict Scanner
- Paste any chapter draft, scene outline, or dialogue snippet.
- The engine checks text against:
  - **Rules of Reality & Magic**: Toxic atmospheres, contact restrictions, weapon bans.
  - **Character Status & Capabilities**: Inactive artifacts, missing gear, physical limitations.
  - **Timeline & Spatial Consistency**: Travel times and geographical constraints.
- Delivers a categorized report with violation severity badges, exact text citations, and actionable recommendations.

### 4. ⚡ Next Scene Generator
- Generates 3 distinct, canon-compliant narrative paths for writer's block:
  - **Character-Driven Path**: Deepens interpersonal friction and secret motives.
  - **World-Driven Path**: Introduces atmospheric hazards, ancient ruins, or faction disputes.
  - **High-Tension Path**: Accelerates urgency with timed stakes or unexpected encounters.
- Includes concrete scene objectives and stakes grounded in your world.

### 5. 🎙️ Cinematic Voice Studio
- **16 Character Voice Archetypes**:
  - *George*: Captivating Master Storyteller / Warm Narrator
  - *Adam*: Resonant Authority / Deep Narrator
  - *Rachel*: Calm Scholar / Narrative Heroine
  - *Callum*: Husky Smuggler / Sky-Pilot
  - *Charlotte*: Seductive Noble / Court Enchanter
  - *Liam*: Gritty Veteran / Hardened Mercenary
  - *Freya*: Fierce Rebel / Vanguard Warrior
  - *Matilda*: Mystic Oracle / Elder Matriarch
  - *Drew*: Neutral Observer / Chronicler
  - *Lily*: Melodic Bard / Minstrel
  - *Thomas*: Ancient Scholar / Grand Archivist
  - *Fin*: Cynical Sailor / Deep-Sea Harbor Hand
  - *Jessica*: Scholarly Mage / High Arcanist
  - *Antoni*: Eloquent Diplomat / Court Emissary
  - *Alice*: Spirited Apprentice / Novice Pathfinder
  - *Brian*: Cryptic Inquisitor / Night Marshal
- **Live Emotion Prosody**: Smooth slider dynamically adjusts pitch, rate, and delivery intensity across 4 expressive tiers (*Calm (25%)*, *Subtle (50%)*, *Dramatic (75%)*, *Intense (100%)*).
- **60 FPS Audio Telemetry Deck**: Real-time elapsed/total clock, live frequency waveform canvas, and sub-millisecond synthesis tracking.
- **Multi-Segmented Teleprompter**: Interactive 5-line screenplay timeline with live karaoke highlighting and zero-latency pre-buffering.

---

## 🏗️ Architecture & Tech Stack

```
Story AL Architecture
┌────────────────────────────────────────────────────────┐
│                   Frontend (SPA)                       │
│  - Dark-Atelier UI (Tailwind CSS, Plus Jakarta Sans)   │
│  - Web Audio API + HTML5 Audio Pre-buffering Engine    │
│  - 60 FPS Canvas Real-Time Waveform Visualizer         │
│  - Teleprompter Screenplay Controller                  │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP / JSON API
┌──────────────────────────▼─────────────────────────────┐
│                 Backend (Flask WSGI)                   │
│  - app.py: REST Endpoints & Route Controller           │
│  - lore_store.py: Persistent Lore DB Store             │
│  - ai_engine.py: Dual-Engine (Gemini API / Heuristic)  │
│  - voice_engine.py: Neural TTS Synthesis Pipeline      │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│               Storage & Serverless Core                │
│  - canon_db.json: Structured World Canon               │
│  - audio_cache/: Pre-warmed Voice Samples              │
│  - /tmp fallback for serverless hosting (Vercel)       │
└────────────────────────────────────────────────────────┘
```

---

## 📂 Project Directory Structure

```
Story_AL/
├── api/
│   └── index.py               # Vercel serverless WSGI entrypoint
├── lorekeeper/
│   ├── app.py                 # Core Flask application and REST routes
│   ├── ai_engine.py           # Canon Q&A and continuity audit engine
│   ├── lore_store.py          # Persistent JSON Story Bible store
│   ├── voice_engine.py        # 16-voice neural synthesis engine
│   ├── start_story_al.bat     # Windows launcher script
│   ├── data/
│   │   └── canon_db.json      # Complete seed Story Bible & audio scene
│   ├── templates/
│   │   └── index.html         # Atelier interface layout & teleprompter
│   └── static/
│       ├── app.js             # Client SPA controller & Web Audio logic
│       ├── styles.css         # Atelier styles & acoustic animations
│       └── audio_cache/       # Pre-rendered voice audition samples
├── .env.example               # Environment variable template
├── .gitignore                 # Optimized Git exclusions
├── requirements.txt           # Python dependencies
├── vercel.json                # Vercel deployment configuration
├── START_STORY_AL.bat         # Root Windows launcher
└── README.md                  # Project documentation
```

---

## 🚀 Local Quickstart Guide

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your system.

### Option 1: Quickstart on Windows (1-Click)
Double-click `START_STORY_AL.bat` in the project root. The launcher will automatically start the server and open your default browser to `http://localhost:5055`.

### Option 2: Command Line (Windows, macOS, Linux)

1. **Clone or navigate to the repository directory**:
   ```bash
   cd Story_AL
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the server**:
   ```bash
   python lorekeeper/app.py
   ```

5. **Open in browser**:
   Navigate to `http://localhost:5055`.

---

## 🌐 Deploying to Vercel

Story AL includes full out-of-the-box Vercel support via `vercel.json` and `api/index.py`.

### Method A: Deploy via GitHub (Recommended)

1. **Push this repository to GitHub** (see instructions below).
2. Go to [vercel.com](https://vercel.com) and log in.
3. Click **"Add New Project"** and select **"Import Git Repository"**.
4. Choose your `Story_AL` repository.
5. In the project settings:
   - **Framework Preset**: Select `Other` (or leave default).
   - **Root Directory**: `./` (leave default).
6. Click **Deploy**. Vercel will install dependencies from `requirements.txt` and launch your live application on a free `*.vercel.app` URL!

### Method B: Deploy via Vercel CLI

```bash
# 1. Install Vercel CLI (if not already installed)
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy to production
vercel --prod
```

> **Note on Serverless Storage**: On Vercel, the filesystem is read-only except for the `/tmp` directory. Story AL automatically detects the serverless environment and routes dynamic writes (e.g. newly generated audio lines or live edits) to `/tmp`, keeping the application fast and error-free.

---

## 🐙 Pushing to GitHub

To make this project a GitHub repository and push your code:

### Step 1: Create a new repository on GitHub
1. Go to [github.com/new](https://github.com/new).
2. Name your repository (e.g., `Story-AL` or `story-al`).
3. Leave **"Initialize this repository with a README"** **UNCHECKED** (we already have a complete README).
4. Click **Create repository**.

### Step 2: Link and push your local repository
Open your terminal in this project folder and run:

```bash
# Initialize git (if not already initialized)
git init

# Stage all files
git add .

# Create initial commit
git commit -m "feat: initial commit for Story AL"

# Set default branch to main
git branch -M main

# Link to your GitHub repository (replace with your GitHub URL)
git remote add origin https://github.com/<YOUR_USERNAME>/Story-AL.git

# Push code to GitHub
git push -u origin main
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Main Atelier SPA interface |
| `/api/status` | `GET` | Health check, mode status, and Story Bible statistics |
| `/api/canon` | `GET`, `POST` | List all canon entries or add a new entry |
| `/api/canon/<id>` | `GET`, `PUT`, `DELETE` | Read, update, or delete a canon entry |
| `/api/chat` | `POST` | Query the Story Bible with zero hallucinations |
| `/api/continuity` | `POST` | Audit a draft passage for canon contradictions |
| `/api/next_scene` | `POST` | Generate 3 grounded next scene directions |
| `/api/audio/scene` | `GET`, `PUT` | Retrieve or update current voice studio scene |
| `/api/audio/voices` | `GET` | List all 16 available character voices |
| `/api/audio/preview/<id>` | `GET` | Stream official audio audition for a voice |
| `/api/audio/synthesize_line` | `POST` | Synthesize single dialogue line with custom prosody |
| `/api/audio/synthesize_scene`| `POST` | Pre-buffer complete scene playlist |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
