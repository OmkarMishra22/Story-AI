"""
Story AL - Main Flask Application
Narrative World Engine & Cinematic Voice Studio
"""

import os
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from lore_store import LoreStore
from ai_engine import AIEngine
from voice_engine import VoiceEngine, VOICE_CATALOG

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(BASE_DIR, "templates")):
    alt_dir = os.path.join(os.getcwd(), "lorekeeper")
    if os.path.exists(os.path.join(alt_dir, "templates")):
        BASE_DIR = alt_dir

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")

# In serverless environments like Vercel, use /tmp for mutable cache
if os.environ.get("VERCEL") or not os.access(BASE_DIR, os.W_OK):
    AUDIO_CACHE_DIR = os.path.join("/tmp", "audio_cache")
else:
    AUDIO_CACHE_DIR = os.path.join(BASE_DIR, "static", "audio_cache")

try:
    os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
except Exception:
    pass

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
lore_store = LoreStore(data_dir=DATA_DIR)
ai_engine = AIEngine()
voice_engine = VoiceEngine(cache_dir=AUDIO_CACHE_DIR)

@app.route('/static/audio_cache/<path:filename>')
def custom_audio_cache_serve(filename):
    if os.path.exists(os.path.join(AUDIO_CACHE_DIR, filename)):
        return send_from_directory(AUDIO_CACHE_DIR, filename)
    default_dir = os.path.join(STATIC_DIR, "audio_cache")
    if os.path.exists(os.path.join(default_dir, filename)):
        return send_from_directory(default_dir, filename)
    abort(404)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Sample drafts for instant one-click testing
SAMPLE_DRAFTS = [
    {
        "id": "draft-contradiction-1",
        "title": "Double Contradiction: Bare Hand Aether & Library Cutlass",
        "description": "Tests Rule #1 (Contact Toxicity) and Rule #3 (Weapon Ban in Grand Library).",
        "text": (
            "Lyra plunged her bare hands into the cracked trench chest and seized the glowing raw Aether sphere, "
            "smiling as the soothing warmth pulsed gently through her unprotected skin without causing any harm. "
            "Moments later, arriving at the Grand Library of the Ivory Spire, she unsheathed her polished iron cutlass "
            "and brandished the blade at the high archivist, demanding access to the restricted catacombs."
        ),
        "expected": "Flags two contradictions: bare skin touching raw Aether (Rule #1) and drawing a metal cutlass inside the Grand Library (Rule #3)."
    },
    {
        "id": "draft-contradiction-2",
        "title": "Atmospheric Contradiction: Unprotected Trench Vapor",
        "description": "Tests Rule #2 (Atmospheric Toxicity below depth 400).",
        "text": (
            "Deep in the Obsidian Trench at depth 500, Captain Kaelen casually discarded his breathing mask onto the skiff's deck. "
            "He leaned over the railing and took deep, refreshing breaths of the misty vapor rising from the abyss, "
            "working comfortably for three hours without any protective gear while laughing at old Spire superstitions."
        ),
        "expected": "Flags one contradiction: breathing deep trench vapor without a mask violates Rule #2 (crystal-lung within 20 minutes)."
    },
    {
        "id": "draft-clean-1",
        "title": "Canon-Consistent Passage: Sound Navigation",
        "description": "Tests a lore-accurate scene that adheres to all world rules and character facts.",
        "text": (
            "Lyra carefully adjusted her lead-lined gauntlets and peered through her attuned catalyst lens before inspecting "
            "the dormant Sunstone casing. Beside her at the skiff's helm, Captain Kaelen double-checked the pressure seals on their "
            "charcoal-aether respirator masks as The Zephyr's Wake descended through the sapphire bioluminescent waters toward the Obsidian Trench."
        ),
        "expected": "Passes with zero contradictions detected. Respects gauntlet requirement, catalyst lens, and respirator mask rules."
    }
]

SAMPLE_QUESTIONS = [
    {
        "question": "What happens if someone touches raw Aether with their bare hands?",
        "type": "Rule Check (Rule #1)",
        "expected": "Grounded answer explaining instantaneous calcification into black glass."
    },
    {
        "question": "What protective gear is required to survive in the Obsidian Trench?",
        "type": "Place / Rule Check (Rule #2)",
        "expected": "Grounded answer explaining mandatory Aether-filter masks or pressure helmets."
    },
    {
        "question": "Why was Lyra Vance banished by Master Corvus and the Council?",
        "type": "Character / Event Lore",
        "expected": "Grounded answer describing her discovery of unauthorized deep-trench excavations."
    },
    {
        "question": "Can iron swords or weapons be drawn inside the Grand Library?",
        "type": "Rule Check (Rule #3)",
        "expected": "Grounded answer citing the weapon ban and activation of clockwork Brass Sentinels."
    },
    {
        "question": "Does Lyra have a pet dragon?",
        "type": "Unknown Canon Test (Negative Check)",
        "expected": "Explicitly states that canon does NOT specify a pet dragon and never hallucinates."
    }
]


@app.route("/")
def index():
    project = lore_store.get_project()
    stats = lore_store.get_stats()
    status = ai_engine.get_status()
    try:
        return render_template("index.html", project=project, stats=stats, status=status)
    except Exception as e:
        tpl_path = os.path.join(TEMPLATES_DIR, "index.html")
        if os.path.exists(tpl_path):
            from jinja2 import Template
            with open(tpl_path, "r", encoding="utf-8") as f:
                t = Template(f.read())
            return t.render(project=project, stats=stats, status=status)
        return f"<h2>Story AL — Template Lookup Notice</h2><p>Could not locate index.html in: {TEMPLATES_DIR}</p><pre>{e}</pre>", 500


@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "status": "online",
        "project": lore_store.get_project(),
        "stats": lore_store.get_stats(),
        "ai": ai_engine.get_status()
    })


@app.route("/api/canon", methods=["GET"])
def api_get_canon():
    category = request.args.get("category", "all")
    entries = lore_store.get_all_entries(category=category)
    return jsonify({
        "category": category,
        "count": len(entries),
        "entries": entries
    })


@app.route("/api/canon/<entry_id>", methods=["GET"])
def api_get_entry(entry_id):
    entry = lore_store.get_entry_by_id(entry_id)
    if not entry:
        return jsonify({"error": "Lore entry not found"}), 404
    return jsonify(entry)


@app.route("/api/canon", methods=["POST"])
def api_add_entry():
    data = request.get_json() or {}
    if not data.get("name") or not data.get("category"):
        return jsonify({"error": "Fields 'name' and 'category' are required."}), 400

    new_entry = lore_store.add_entry(data)
    return jsonify({
        "message": "Canon entry created successfully.",
        "entry": new_entry,
        "stats": lore_store.get_stats()
    }), 201


@app.route("/api/canon/<entry_id>", methods=["PUT"])
def api_update_entry(entry_id):
    data = request.get_json() or {}
    updated = lore_store.update_entry(entry_id, data)
    if not updated:
        return jsonify({"error": "Canon entry not found."}), 404
    return jsonify({
        "message": "Canon entry updated successfully.",
        "entry": updated,
        "stats": lore_store.get_stats()
    })


@app.route("/api/canon/<entry_id>", methods=["DELETE"])
def api_delete_entry(entry_id):
    success = lore_store.delete_entry(entry_id)
    if not success:
        return jsonify({"error": "Canon entry not found."}), 404
    return jsonify({
        "message": "Canon entry deleted.",
        "deleted_id": entry_id,
        "stats": lore_store.get_stats()
    })


@app.route("/api/canon/reset", methods=["POST"])
def api_reset_canon():
    lore_store.reset_to_seed()
    return jsonify({
        "message": "Reset to default seeded canon successfully.",
        "entries": lore_store.get_all_entries(),
        "stats": lore_store.get_stats()
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    force_demo = data.get("force_demo", False)

    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    canon_entries = lore_store.get_all_entries()
    result = ai_engine.answer_canon_question(question, canon_entries, force_demo=force_demo)
    return jsonify(result)


@app.route("/api/continuity", methods=["POST"])
def api_continuity():
    data = request.get_json() or {}
    draft = data.get("draft", "").strip()
    force_demo = data.get("force_demo", False)

    if not draft:
        return jsonify({"error": "Draft text cannot be empty."}), 400

    canon_entries = lore_store.get_all_entries()
    result = ai_engine.check_continuity(draft, canon_entries, force_demo=force_demo)
    return jsonify(result)


@app.route("/api/samples", methods=["GET"])
def api_samples():
    return jsonify({
        "drafts": SAMPLE_DRAFTS,
        "questions": SAMPLE_QUESTIONS
    })


@app.route("/api/config", methods=["POST"])
def api_config():
    data = request.get_json() or {}
    gemini_key = data.get("gemini_api_key")
    if gemini_key is not None:
        ai_engine.set_api_key(gemini_key)
    elevenlabs_key = data.get("elevenlabs_api_key")
    if elevenlabs_key is not None:
        voice_engine.set_api_key(elevenlabs_key)
    return jsonify({
        "message": "Configuration updated successfully.",
        "status": ai_engine.get_status(),
        "audio_status": voice_engine.get_status()
    })


# =============================================================================
# FEATURE 5: NEXT SCENE SUGGESTIONS & DRAFT NOTES
# =============================================================================

@app.route("/api/next_scene", methods=["POST"])
def api_next_scene():
    data = request.get_json() or {}
    character = data.get("character", "Lyra Vance")
    situation = data.get("situation", "")
    force_demo = data.get("force_demo", False)

    canon_entries = lore_store.get_all_entries()
    result = ai_engine.generate_next_scenes(character, situation, canon_entries, force_demo=force_demo)
    return jsonify(result)


@app.route("/api/notes", methods=["GET"])
def api_get_notes():
    return jsonify({
        "notes": lore_store.get_notes(),
        "count": len(lore_store.get_notes())
    })


@app.route("/api/notes", methods=["POST"])
def api_add_note():
    data = request.get_json() or {}
    new_note = lore_store.add_note(data)
    return jsonify({
        "message": "Draft note saved to your notebook.",
        "note": new_note,
        "notes": lore_store.get_notes(),
        "stats": lore_store.get_stats()
    }), 201


@app.route("/api/notes/<note_id>", methods=["DELETE"])
def api_delete_note(note_id):
    success = lore_store.delete_note(note_id)
    if not success:
        return jsonify({"error": "Note not found."}), 404
    return jsonify({
        "message": "Draft note removed.",
        "deleted_id": note_id,
        "notes": lore_store.get_notes(),
        "stats": lore_store.get_stats()
    })


# =============================================================================
# FEATURE 6: AUDIO STUDIO
# =============================================================================

@app.route("/api/audio/scene", methods=["GET"])
def api_get_audio_scene():
    scene = lore_store.get_audio_scene()
    try:
        expressiveness = float(scene.get("expressiveness", 0.75))
        playlist = voice_engine.synthesize_scene(scene=scene, expressiveness=expressiveness)
        scene["playlist"] = playlist.get("lines", [])
    except Exception as e:
        print(f"[VoiceEngine] Warning synthesizing initial scene playlist: {e}")
        scene["playlist"] = []
    return jsonify(scene)


@app.route("/api/audio/scene", methods=["PUT"])
def api_update_audio_scene():
    data = request.get_json() or {}
    updated = lore_store.update_audio_scene(data)
    return jsonify({
        "message": "Audio scene configuration updated.",
        "scene": updated
    })


@app.route("/api/audio/status", methods=["GET"])
def api_get_audio_status():
    return jsonify(voice_engine.get_status())


@app.route("/api/audio/voices", methods=["GET"])
def api_get_audio_voices():
    return jsonify(VOICE_CATALOG)


@app.route("/api/audio/preview/<voice_id>", methods=["GET"])
def api_audio_preview_voice(voice_id):
    return jsonify(voice_engine.get_voice_preview_audio(voice_id))


@app.route("/api/audio/synthesize_line", methods=["POST"])
def api_audio_synthesize_line():
    data = request.get_json() or {}
    text = data.get("text", "")
    voice_id = data.get("voice_id", "JBFqnCBsd6RMkjVDRZzb")
    rate = float(data.get("rate", 1.0))
    pitch = float(data.get("pitch", 1.0))
    delivery = data.get("delivery", "")
    expressiveness = float(data.get("expressiveness", 0.75))

    result = voice_engine.synthesize_line(
        text=text,
        voice_id=voice_id,
        rate=rate,
        pitch=pitch,
        delivery=delivery,
        expressiveness=expressiveness
    )
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/api/audio/synthesize_scene", methods=["POST"])
def api_audio_synthesize_scene():
    data = request.get_json() or {}
    scene = data.get("scene") or lore_store.get_audio_scene()
    expressiveness = float(data.get("expressiveness", scene.get("expressiveness", 0.75)))
    playlist = voice_engine.synthesize_scene(scene=scene, expressiveness=expressiveness)
    return jsonify(playlist)


@app.route("/api/audio/synthesize", methods=["POST"])
def api_audio_synthesize():
    data = request.get_json() or {}
    if "text" in data:
        return api_audio_synthesize_line()
    return api_audio_synthesize_scene()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5055))
    print(f"[Story AL] Starting server on http://localhost:{port} (Network: http://0.0.0.0:{port}) ...")
    app.run(host="0.0.0.0", port=port, debug=True)
