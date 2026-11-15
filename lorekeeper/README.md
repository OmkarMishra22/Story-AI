# Story AL — Narrative World Engine
> **A quiet, reliable companion for fiction writers — keep your world rules straight, ask questions about your lore, explore what could happen next, and hear your dialogue read aloud in character voices.**

Story AL is a creative workspace crafted specifically for fiction authors, novelists, and worldbuilders. It provides a tactile, calm digital writing atelier where you can catalog characters, locations, events, and physical/magical world rules, ask questions answered strictly from established facts, catch accidental contradictions in scene drafts, brainstorm three grounded directions for your next scene, and listen to a short scene performed with character voices.

---

## 🖋️ Design Philosophy: Handcrafted for Writers, Not Robots
- **Warm Atelier Aesthetics**: Deep warm espresso, natural bookbinder ink, aged paperboard cards, and calming honey, terracotta, sage, and plum accents.
- **Literary Typography**: Headings set in **Lora** (a warm, handcrafted literary serif), clean interface text in **Plus Jakarta Sans**, and manuscript excerpts in **Courier Prime**.
- **Human, Easy Language**: No cold AI buzzwords like *"LLM inference parameters"* or *"heuristic vector alignment"*. Features are titled naturally: **Writing Desk**, **Story Bible**, **Ask Your Canon**, **Check Draft for Conflicts**, **Scene Ideas**, and **Voice Studio**.
- **Clear Boundaries**: High visual distinction between **Confirmed Story Bible Canon** (solid badges) and **Draft Ideas / Non-Canon Possibilities** (dashed warm badges, kept separate in your notebook).

---

## 🌟 Six Core Features

### 1. Writing Desk (Overview)
- **One-Sentence Product Goal**: Clearly introduces the workspace at a glance.
- **Canon Snapshot**: Live counts of Characters, Locations, Historical Events, Binding World Rules, and Saved Draft Notes.
- **Seeded Fictional Universe**: Preloaded with ***The Aethermoor Chronicles: The Shattered Citadel*** (a submerged canal setting after the Great Shattering cataclysm).
- **Persistent Local Database**: Changes are preserved in `data/canon_db.json`. A one-click **"Reset Sample Lore"** button restores the starting state at any time.

### 2. Story Bible (CRUD Canon Management)
- **Characters**: Name, archetype/role, primary goals, relationships, and tags.
- **Locations**: Name, atmospheric description, defining details, and environmental hazards (e.g. *The Obsidian Trench below Depth 400 requires sealed respirators to prevent fatal crystal-lung*).
- **Historical Events**: Cataclysms, treaties, and council tribunals (e.g. *The Great Shattering [Year 412]*, *The Treaty of the Seven Bells [Year 425]*, *The Banishment of Lyra Vance [Year 438]*).
- **World Rules**: Inviolable physical and magical laws (e.g. *The Law of Aetheric Resonance — raw Aether petrifies bare flesh into black glass without an insulated catalyst lens*).
- **Author Tools**: Live search, category filtering, dynamic Add/Edit modal, and deletion confirmation.

### 3. Ask Your Canon (Factual Q&A)
- **Strict Factual Grounding**: Answers are derived strictly and exclusively from saved Story Bible facts and cite supporting entries.
- **Zero Hallucination / No Guessing**: If you ask about something you haven't written into canon yet (e.g., *"Does Lyra have a pet dragon?"* or unrecorded family members), LoreKeeper explicitly states that the canon does not specify the answer rather than inventing one.
- **Citation Badges**: Every answer highlights the exact Story Bible entries that substantiate it, allowing you to jump directly to that entry.
- **Instant Test Chips**: One-click prompts to test Rule #1 (contact toxicity), Rule #2 (trench respirators), Rule #3 (Grand Library weapon prohibition), character exile, and the negative pet dragon test.

### 4. Check Draft for Conflicts (Continuity Review)
- **Draft Scanner**: Paste a scene or chapter draft to compare it against your saved Story Bible.
- **Preloaded Demonstration Scenes**:
  - **Sample 1 (Double Discrepancy)**: Bare hands touching raw Aether (*violates Rule #1*) and drawing an iron cutlass inside the Grand Library (*violates Rule #3*).
  - **Sample 2 (Atmospheric Hazard)**: Discarding respirators to breathe deep trench mist (*violates Rule #2*).
  - **Sample 3 (Clean Scene)**: Demonstrates lore-compliant navigation with protective catalyst gauntlets and respirator masks (*passes with 0 conflicts*).
- **Constructive Review Cards**: Displays the highlighted draft passage, links to the conflicting rule, explains why it conflicts, and suggests friendly revisions for the author to review.

### 5. Scene Ideas (What Could Happen Next)
- **Three Grounded Pathways**: Select a character (e.g. *Lyra Vance*, *Captain Kaelen*, *Master Corvus*, or *General Ensemble*) and enter your current story situation to generate three distinct directions:
  1. **Action & Stakes** (High-tension pursuit, ticking clock, direct physical danger)
  2. **Investigation & Secrets** (Quiet encounters, concealed motives, espionage)
  3. **Lore & Revelation** (Ancient conduits, celestial eclipse mysteries, historical discoveries)
- **Grounding & Canon Safety**: Each idea explains *why it fits* your character's goals and respects your world rules without creating plot holes.
- **Clearly Labeled Non-Canon**: Explicitly tagged as **"Draft Idea · Non-Canon"** so generated suggestions never pollute your confirmed canon.
- **Writer's Notebook**: Save any suggestion to your notebook with one click, or copy it to your clipboard.

### 6. Voice Studio (ElevenLabs Storyteller AI Voices [Voice Library])
- **Sample Dramatic Scene**: *"Descent into the Mist Shallows"* featuring the Narrator, Lyra Vance, and Captain Kaelen.
- **Exclusively Powered by ElevenLabs Storyteller Voice Library**:
  - **Narrators & Storytellers**: *George* (Warm British Literary Storyteller), *Adam* (Deep, Dominant Narrator), *Bill* (Wise Mature Elder), *Daniel* (Steady Formal Chronicler).
  - **Heroines & Scholars**: *Rachel* (Calm Narrative Heroine), *Sarah* (Mature Reassuring Scholar), *Alice* (Clear British Inquisitor), *Lily* (Velvety Dramatic Actress), *Bella* (Warm Emotional Voice), *Jessica* (Young Adventurer).
  - **Rogues, Pilots & Warriors**: *Callum* (Husky Rogue Smuggler), *Roger* (Laid-Back Resonant Pilot), *Arnold* (Crisp Action Narrator), *Sam* (Gritty Folk Storyteller), *Harry* (Fierce Warrior), *Charlie* (Deep Australian Explorer).
- **Official Voice Library Auditioning**: Every character card features an **"Audition Voice"** button that streams authentic, master studio recordings directly from ElevenLabs's public voice library.
- **Live Cloud + Offline Acoustic Mode**: Seamlessly switches between live cloud neural synthesis (`ELEVENLABS_API_KEY`) and offline acoustic emulation without interruptions.
- **Interactive Audio Controls**: Individual line performance, full-scene playback with conversational pauses (400ms), illuminated karaoke line tracking, and local MP3 caching in `static/audio_cache/`.

---

## 🤖 Real AI & Audio Services vs. Demo Mode Behavior

| Feature | Offline / Zero-Key Mode | Live Cloud AI / API Mode |
| :--- | :--- | :--- |
| **Story Bible CRUD** | Fully functional local JSON persistence (`data/canon_db.json`). | Fully functional local JSON persistence (`data/canon_db.json`). |
| **Ask Your Canon** | Strict entity & rule-matching engine answering from canon text without hallucinations. | Gemini (`gemini-2.5-flash`) with strict grounding prompts prohibiting extrapolation. |
| **Check Draft Conflicts** | Pattern scanner against world rules, atmospheric limits, and character history. | Gemini (`gemini-2.5-flash`) for deep contextual contradiction analysis. |
| **Scene Ideas** | 3 narrative directions tailored to character goals and physical world rules. | Gemini (`gemini-2.5-flash`) tailored creative directions grounded in canon. |
| **Voice Studio** | **Microsoft Azure Neural (`edge-tts`)**, **Google Web (`gTTS`)**, and **Windows SAPI5 (`pyttsx3`)** with real, ultra-lifelike audio caching and line-by-line playback. | **OpenAI TTS-1-HD** and **ElevenLabs Neural** when API keys are configured. |

---

## 🚀 Quickstart & Setup Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Modern web browser (Chrome, Edge, Safari, Firefox)

### Starting LoreKeeper

1. Open PowerShell or Terminal in the project root:
   ```powershell
   cd "d:\SIH 2026\lorekeeper"
   python app.py
   ```
   Or double-click [`START_LOREKEEPER.bat`](file:///d:/SIH%202026/START_LOREKEEPER.bat).

2. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

3. (Optional) To enable Live Gemini AI mode:
   - Click **"Settings & Keys"** in the sidebar.
   - Enter your `GEMINI_API_KEY`.
   - Alternatively, set the environment variable before starting:
     ```powershell
     $env:GEMINI_API_KEY="your-gemini-api-key"
     python app.py
     ```

---

## 🧪 Quick 5-Minute Verification Walkthrough

1. **Writing Desk & Project Snapshot**: Open `http://127.0.0.1:5000` and view the 5 universe counters, world summary, and featured highlights.
2. **Story Bible CRUD**: Go to **Story Bible**, click **"+ Add Entry"**, create a new rule (e.g. *"The Law of Lunar Echoes"*), edit it, and verify that it updates immediately.
3. **Ask Your Canon**: Go to **Ask Your Canon**, click the prompt chip *"What happens if someone touches raw Aether directly?"* to see the grounded rule citation. Next, click *"Does Lyra have a pet dragon?"* to see LoreKeeper explicitly state that the canon contains no record of dragons.
4. **Check Draft for Conflicts**: Go to **Check Draft Conflicts**, click **"Sample 1: Double Contradiction"** and **"Check Draft"** to see both flagged discrepancies. Next, click **"Sample 3: Canon-Consistent Passage"** to verify the clean verification pass.
5. **Scene Ideas**: Go to **Scene Ideas**, select a character, click **"Generate 3 Ideas"**, review the 3 distinct paths, and click **"Save to Notes"** to store an idea in your notebook.
6. **Voice Studio**: Go to **Voice Studio**, review the casting and delivery notes, and click **"Play Full Scene"** or individual **"Play"** buttons to hear the dialogue spoken aloud in character voices with real-time line tracking.

---

## 📁 Project Architecture

```
lorekeeper/
├── app.py                  # Flask web server and REST API endpoints
├── ai_engine.py            # Dual-mode engine: Gemini 2.5 Flash caller & grounded demo generator
├── lore_store.py           # Persistent canon, draft notes, and audio scene storage manager
├── data/
│   └── canon_db.json       # JSON database storing Story Bible, notes, and project metadata
├── static/
│   ├── app.js              # Client-side SPA router, reactive state, and Web Speech audio player
│   └── styles.css          # Writer's Atelier theme: Lora serif, wood, paperboard, ink palette
├── templates/
│   └── index.html          # Responsive single-page application layout with 6 workspaces
├── start_lorekeeper.bat    # Windows launcher script
└── README.md               # Complete documentation and setup guide
```
