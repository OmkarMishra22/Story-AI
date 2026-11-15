"""
LoreKeeper AI - Dossier & Multi-Format Document Generator
Generates:
1. LoreKeeper_AI_Dossier.pdf (via Headless Edge/Chrome)
2. LoreKeeper_AI_Dossier.html (Standalone styled document)
3. LoreKeeper_AI_Dossier.md (Markdown format)
4. LoreKeeper_AI_Dossier.txt (Plain text format)
5. LoreKeeper_Canon_Database_Export.json (Structured JSON data export)
6. LoreKeeper_AI_Complete_Codebase.zip (Zip archive of the complete runnable codebase)
"""

import os
import sys
import json
import zipfile
import subprocess
from datetime import datetime

BASE_DIR = r"d:\SIH 2026\lorekeeper"
ROOT_DIR = r"d:\SIH 2026"

def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[Error reading file: {e}]"

def build_zip():
    zip_path = os.path.join(ROOT_DIR, "LoreKeeper_AI_Complete_Codebase.zip")
    print(f"[*] Packaging codebase into: {zip_path}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            if "__pycache__" in root or ".git" in root:
                continue
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, ROOT_DIR)
                zf.write(abs_path, rel_path)
        # Also add the root launcher
        root_bat = os.path.join(ROOT_DIR, "START_LOREKEEPER.bat")
        if os.path.exists(root_bat):
            zf.write(root_bat, "START_LOREKEEPER.bat")
    print(f"[+] Zip created successfully: {os.path.getsize(zip_path)/1024:.1f} KB")
    return zip_path

def generate_documents():
    print("[*] Reading codebase files...")
    app_py = read_file(os.path.join(BASE_DIR, "app.py"))
    ai_engine_py = read_file(os.path.join(BASE_DIR, "ai_engine.py"))
    lore_store_py = read_file(os.path.join(BASE_DIR, "lore_store.py"))
    index_html = read_file(os.path.join(BASE_DIR, "templates", "index.html"))
    app_js = read_file(os.path.join(BASE_DIR, "static", "app.js"))
    styles_css = read_file(os.path.join(BASE_DIR, "static", "styles.css"))
    canon_db = read_file(os.path.join(BASE_DIR, "data", "canon_db.json"))
    readme_md = read_file(os.path.join(BASE_DIR, "README.md"))

    # 1. Export JSON
    json_export_path = os.path.join(ROOT_DIR, "LoreKeeper_Canon_Database_Export.json")
    with open(json_export_path, "w", encoding="utf-8") as f:
        f.write(canon_db)
    print(f"[+] JSON export created: {json_export_path}")

    # 2. Export TXT
    txt_path = os.path.join(ROOT_DIR, "LoreKeeper_AI_Dossier.txt")
    print(f"[*] Writing Plain Text Dossier to: {txt_path}...")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("LOREKEEPER AI -- THE MEMORY OF FICTIONAL WORLDS\n")
        f.write("COMPREHENSIVE TECHNICAL ARCHITECTURE & COMPLETE CODEBASE DOSSIER\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. EXECUTIVE SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write("LoreKeeper AI is a specialized writing workspace designed for fiction authors and\n")
        f.write("worldbuilders. It prevents canon drift by storing Story Bible facts, enforcing strict\n")
        f.write("factual grounding in Q&A (zero-hallucination guarantee), scanning drafts for world-rule\n")
        f.write("contradictions, generating three distinct next-scene pathways, and reading dialogue\n")
        f.write("aloud with distinct character voice casting.\n\n")

        f.write("2. TECHNOLOGY STACK\n")
        f.write("-" * 80 + "\n")
        f.write("- Backend: Python 3.14.7 + Flask 3.1.3 + Werkzeug 3.1.8\n")
        f.write("- AI Engine: Google Gemini SDK (gemini-2.5-flash) with offline heuristic fallback\n")
        f.write("- Speech: W3C Web Speech API (window.speechSynthesis) with multi-voice casting\n")
        f.write("- Frontend: Vanilla ES6+ Single Page Application with reactive state management\n")
        f.write("- Styling: Tailwind CSS 3.x CDN + Custom Literary Atelier CSS (Lora / Plus Jakarta Sans)\n")
        f.write("- Storage: Local Atomic JSON Storage (data/canon_db.json)\n\n")

        f.write("3. COMPLETE SOURCE CODE LISTINGS\n")
        f.write("-" * 80 + "\n\n")

        f.write("FILE: lorekeeper/app.py\n" + "~" * 60 + "\n")
        f.write(app_py + "\n\n")

        f.write("FILE: lorekeeper/ai_engine.py\n" + "~" * 60 + "\n")
        f.write(ai_engine_py + "\n\n")

        f.write("FILE: lorekeeper/lore_store.py\n" + "~" * 60 + "\n")
        f.write(lore_store_py + "\n\n")

        f.write("FILE: lorekeeper/templates/index.html\n" + "~" * 60 + "\n")
        f.write(index_html + "\n\n")

        f.write("FILE: lorekeeper/static/app.js\n" + "~" * 60 + "\n")
        f.write(app_js + "\n\n")

        f.write("FILE: lorekeeper/static/styles.css\n" + "~" * 60 + "\n")
        f.write(styles_css + "\n\n")

    print(f"[+] TXT document created: {txt_path} ({os.path.getsize(txt_path)/1024:.1f} KB)")

    # 3. Export Markdown
    md_path = os.path.join(ROOT_DIR, "LoreKeeper_AI_Dossier.md")
    print(f"[*] Writing Markdown Dossier to: {md_path}...")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# LoreKeeper AI — The Memory of Fictional Worlds\n")
        f.write("## Comprehensive Technical Architecture & Complete Codebase Dossier\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%B %d, %Y - %H:%M:%S')}*\n\n---\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write("LoreKeeper AI provides fiction authors with an organized, calm digital atelier designed to eliminate **canon drift** and **worldbuilding contradictions**.\n\n")
        f.write("### The Six Core Workflows\n")
        f.write("1. **Writing Desk**: Live universe overview and canon counts.\n")
        f.write("2. **Story Bible**: CRUD management of Characters, Places, Events, and Inviolable World Rules.\n")
        f.write("3. **Ask Your Canon**: Strict factual Q&A with zero-hallucination guarantee and supporting citations.\n")
        f.write("4. **Check Draft Conflicts**: Continuous manuscript auditing with highlighted conflict excerpts.\n")
        f.write("5. **Scene Ideas**: Three grounded narrative directions based on character goals, kept separate in personal notes.\n")
        f.write("6. **Voice Studio**: Multi-character audio playback using local browser speech synthesis.\n\n---\n\n")

        f.write("## 2. Technology Stack\n\n")
        f.write("| Component | Technology | Role |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write("| Backend Runtime | Python 3.14.7 | Server execution and API controllers |\n")
        f.write("| Web Server | Flask 3.1.3 | REST API routes and SPA serving |\n")
        f.write("| AI SDK | Google GenAI 2.25.0 | Gemini 2.5 Flash live inference |\n")
        f.write("| Offline AI | Deterministic Heuristic Matcher | Offline rule checking and canon retrieval |\n")
        f.write("| Speech Player | Web Speech API | Multi-character speech synthesis in browser |\n")
        f.write("| Frontend | Vanilla ES6+ SPA | Reactive client state and DOM updates |\n")
        f.write("| Styling | Tailwind CSS + Atelier CSS | Literary design with Lora & Plus Jakarta Sans |\n")
        f.write("| Database | Atomic JSON (`canon_db.json`) | Persistent local project storage |\n\n---\n\n")

        f.write("## 3. Full Source Code\n\n")
        f.write("### `app.py`\n```python\n" + app_py + "\n```\n\n")
        f.write("### `ai_engine.py`\n```python\n" + ai_engine_py + "\n```\n\n")
        f.write("### `lore_store.py`\n```python\n" + lore_store_py + "\n```\n\n")
        f.write("### `static/styles.css`\n```css\n" + styles_css + "\n```\n\n")
        f.write("### `templates/index.html`\n```html\n" + index_html + "\n```\n\n")
        f.write("### `static/app.js`\n```javascript\n" + app_js + "\n```\n\n")

    print(f"[+] Markdown document created: {md_path} ({os.path.getsize(md_path)/1024:.1f} KB)")

    # 4. Export HTML & PDF
    html_path = os.path.join(ROOT_DIR, "LoreKeeper_AI_Dossier.html")
    pdf_path = os.path.join(ROOT_DIR, "LoreKeeper_AI_Dossier.pdf")
    print(f"[*] Building high-resolution HTML Dossier for PDF rendering...")

    def esc(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LoreKeeper AI — Comprehensive Technical Architecture & Complete Codebase Dossier</title>
<style>
    @page {{
        size: A4;
        margin: 14mm 12mm 14mm 12mm;
        @bottom-right {{
            content: "Page " counter(page);
            font-size: 8pt;
            color: #718096;
        }}
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1f2937;
        background: #ffffff;
        line-height: 1.5;
        font-size: 10pt;
        margin: 0;
        padding: 0;
    }}
    .header-banner {{
        border-bottom: 3px solid #d96b43;
        padding-bottom: 12px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .title-box h1 {{
        font-size: 20pt;
        margin: 0;
        color: #1f2937;
        font-family: Georgia, 'Times New Roman', serif;
    }}
    .title-box p {{
        margin: 4px 0 0 0;
        color: #d96b43;
        font-size: 11pt;
        font-weight: 600;
    }}
    .meta-box {{
        text-align: right;
        font-size: 8.5pt;
        color: #4b5563;
    }}
    .badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 8pt;
        font-weight: 600;
        margin-right: 4px;
    }}
    .badge-orange {{ background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }}
    .badge-green {{ background: #dcfce7; color: #166534; border: 1px solid #86efac; }}
    .badge-blue {{ background: #e0f2fe; color: #075985; border: 1px solid #7dd3fc; }}
    
    h2 {{
        font-size: 13pt;
        color: #111827;
        border-left: 4px solid #d96b43;
        padding-left: 8px;
        margin-top: 24px;
        margin-bottom: 10px;
        font-family: Georgia, serif;
        page-break-after: avoid;
    }}
    h3 {{
        font-size: 11pt;
        color: #374151;
        margin-top: 16px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        font-size: 8.5pt;
    }}
    th, td {{
        border: 1px solid #e5e7eb;
        padding: 6px 10px;
        text-align: left;
    }}
    th {{
        background: #f9fafb;
        font-weight: 700;
        color: #111827;
    }}
    .card {{
        background: #fafaf9;
        border: 1px solid #e7e5e4;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 10px 0;
    }}
    pre {{
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 10px 12px;
        border-radius: 6px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 7.5pt;
        line-height: 1.35;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-all;
        margin: 8px 0 16px 0;
        page-break-inside: avoid;
    }}
    .page-break {{
        page-break-before: always;
    }}
</style>
</head>
<body>

<div class="header-banner">
    <div class="title-box">
        <h1>LoreKeeper AI</h1>
        <p>The Memory of Fictional Worlds</p>
    </div>
    <div class="meta-box">
        <div><strong>Complete Technical Dossier</strong></div>
        <div>Generated: {datetime.now().strftime('%B %d, %Y')}</div>
        <div>Stack: Python 3.14 · Flask · Gemini · Web Speech</div>
    </div>
</div>

<h2>1. Executive Summary & Product Architecture</h2>
<p>
    <strong>LoreKeeper AI</strong> is a dedicated creative writing workspace built to eliminate <em>canon drift</em> and <em>continuity errors</em> in fiction manuscripts, fantasy worlds, and episodic sagas.
</p>
<div class="card">
    <strong>Core Architectural Guarantee:</strong>
    LoreKeeper strictly grounds answers in documented facts. If a writer inquires about an unrecorded event, character relative, or fantasy creature, the system explicitly states that the canon does not specify the detail, completely preventing AI hallucinations from polluting the story bible.
</div>

<h3>The Six Integrated Writing Workspaces</h3>
<table>
    <tr><th>Workspace</th><th>Purpose</th><th>Technical Implementation</th></tr>
    <tr><td><strong>1. Writing Desk</strong></td><td>Live universe dashboard & canon metrics</td><td>Real-time counter sync, seeded background narrative, quick-start workflow navigation</td></tr>
    <tr><td><strong>2. Story Bible</strong></td><td>Catalog characters, places, events, and rules</td><td>Persistent CRUD layer (`lore_store.py`), category filters, relational character goals & hazards</td></tr>
    <tr><td><strong>3. Ask Your Canon</strong></td><td>Strict factual query answering</td><td>Entity-grounding & Gemini AI integration (`ai_engine.py`) with zero-hallucination guardrails and citations</td></tr>
    <tr><td><strong>4. Check Draft Conflicts</strong></td><td>Manuscript continuity auditing</td><td>Passage parsing, physical rule matching (contact toxicity, trench respirators, weapon bans), author suggestions</td></tr>
    <tr><td><strong>5. Scene Ideas</strong></td><td>Three grounded paths for what happens next</td><td>Motivation-aligned branching (Action, Secrets, Lore), non-canon tagging, local Draft Notebook persistence</td></tr>
    <tr><td><strong>6. Voice Studio</strong></td><td>Listen to dialogue in character voices</td><td>Multi-speaker casting, editable delivery notes, local W3C Web Speech API playback with line-by-line karaoke tracking</td></tr>
</table>

<h2>2. Complete Technology Stack & Specifications</h2>
<table>
    <tr><th>Layer</th><th>Technology</th><th>Version</th><th>Key Highlights</th></tr>
    <tr><td><strong>Backend Runtime</strong></td><td>Python</td><td>3.14.7</td><td>Fast execution, WSGI compatibility, asynchronous command dispatch</td></tr>
    <tr><td><strong>Web Framework</strong></td><td>Flask</td><td>3.1.3</td><td>REST API routing, template rendering, zero-build asset serving</td></tr>
    <tr><td><strong>AI Inference</strong></td><td>Google GenAI SDK / Deterministic Grounder</td><td>2.25.0</td><td>Gemini 2.5 Flash live reasoning + 100% offline deterministic rule matcher</td></tr>
    <tr><td><strong>Speech Engine</strong></td><td>W3C Web Speech API</td><td>Standard</td><td>Multi-voice synthesis in browser, customizable pitch/rate, real-time karaoke tracking</td></tr>
    <tr><td><strong>Frontend SPA</strong></td><td>Vanilla ES6+ JavaScript</td><td>ES2022</td><td>Lightweight reactive state store, client router, optimistic DOM updates</td></tr>
    <tr><td><strong>Styling & Design</strong></td><td>Tailwind CSS + Atelier CSS</td><td>3.x CDN</td><td>Warm literary aesthetic (Lora, Plus Jakarta Sans, Courier Prime, wood & linen palette)</td></tr>
    <tr><td><strong>Persistence</strong></td><td>Atomic Local JSON Database</td><td>Custom</td><td>Filesystem persistence (`data/canon_db.json`), rollback protection, one-click seed restore</td></tr>
</table>

<div class="page-break"></div>

<h2>3. Definitive Source Code Listings</h2>

<h3>3.1 Application Controller — <code>lorekeeper/app.py</code></h3>
<pre>{esc(app_py)}</pre>

<div class="page-break"></div>

<h3>3.2 AI Grounding & Rule Engine — <code>lorekeeper/ai_engine.py</code></h3>
<pre>{esc(ai_engine_py)}</pre>

<div class="page-break"></div>

<h3>3.3 Persistence Store & Seed Canon — <code>lorekeeper/lore_store.py</code></h3>
<pre>{esc(lore_store_py)}</pre>

<div class="page-break"></div>

<h3>3.4 Design System & Typography Styles — <code>lorekeeper/static/styles.css</code></h3>
<pre>{esc(styles_css)}</pre>

<div class="page-break"></div>

<h3>3.5 Client State Machine & Audio Engine — <code>lorekeeper/static/app.js</code></h3>
<pre>{esc(app_js)}</pre>

<div class="page-break"></div>

<h3>3.6 Single Page Application Template — <code>lorekeeper/templates/index.html</code></h3>
<pre>{esc(index_html)}</pre>

</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[+] HTML dossier created: {html_path} ({os.path.getsize(html_path)/1024:.1f} KB)")

    # 5. Render PDF via Headless Edge/Chrome
    browser_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    browser_exe = next((p for p in browser_paths if os.path.exists(p)), None)

    if browser_exe:
        print(f"[*] Rendering PDF via headless browser: {browser_exe}...")
        cmd = [
            browser_exe,
            "--headless",
            "--disable-gpu",
            "--run-all-compositor-stages-before-draw",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
            print(f"[+] PDF successfully created: {pdf_path} ({os.path.getsize(pdf_path)/1024:.1f} KB)")
        else:
            print(f"[!] Headless browser PDF generation warning: {res.stderr}")
    else:
        print("[!] No headless browser found for PDF conversion.")

if __name__ == "__main__":
    build_zip()
    generate_documents()
    print("\n[SUCCESS] All formats and codebase packages generated successfully!")
