"""
Story AL - Persistent Lore Database Store
Handles Story Bible CRUD operations, saved scene draft notes,
and Audio Studio sample scenes with persistent JSON storage.
"""

import json
import os
import uuid
import copy
from typing import Dict, List, Optional, Any

DEFAULT_PROJECT = {
    "id": "proj-aethermoor-01",
    "title": "The Aethermoor Chronicles: The Shattered Citadel",
    "tagline": "A quiet, reliable companion for fiction writers — keep your world rules straight, ask questions about your lore, and test fresh scene ideas without losing your thread.",
    "genre": "Aetherpunk / Literary Fantasy",
    "summary": "In the submerged canals of Oakhaven, exiled cartographers and wary boat pilots navigate ancient aether conduits beneath a towering citadel of scholars.",
    "created_at": "Year 440 Post-Shattering"
}

SEED_NOTES = [
    {
        "id": "note-seed-01",
        "title": "Idea: The Ambush at the Rusted Sluice",
        "character": "Lyra Vance",
        "category": "Scene Idea",
        "text": "As Lyra and Kaelen slip under the Low Docks aqueduct, an unregistered dredge-skiff blocks the canal. Lyra must use her resonance compass to spot a flooded drainage pipe before their skiff is boarded.",
        "why_it_fits": "Tests Lyra's navigation skills and raises the stakes of escaping the Spire watch without violating Trench safety rules.",
        "created_at": "Today"
    },
    {
        "id": "note-seed-02",
        "title": "Dialogue snippet: Kaelen's warning about the mist",
        "character": "Captain Kaelen",
        "category": "Dialogue Note",
        "text": "'Don't let the water fool you, scholar. Down here, even the barnacles know when a Spire coat is trying to act like a canal rat.'",
        "why_it_fits": "Captures Kaelen's dry humor and establishes his distrust of anyone trained in the Ivory Spire.",
        "created_at": "Yesterday"
    }
]

DEFAULT_AUDIO_SCENE = {
    "title": "The Hearth at Whisper Cove",
    "location": "The Fireside Snug, Old Harbor Tavern",
    "engine": "elevenlabs",
    "narrator_voice": {
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "label": "George — Captivating Storyteller",
        "tone": "Warm, measured, and atmospheric storytelling",
        "pitch": 1.0,
        "rate": 1.0
    },
    "characters": {
        "Lyra Vance": {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",
            "label": "Rachel — Calm Narrative Heroine",
            "tone": "Gentle, thoughtful, and curious",
            "pitch": 1.0,
            "rate": 1.0
        },
        "Captain Kaelen": {
            "voice_id": "N2lVS1w4EtoT3dr4eOWO",
            "label": "Callum — Husky Rogue Smuggler",
            "tone": "Warm, friendly rasp with quiet confidence",
            "pitch": 1.0,
            "rate": 1.0
        }
    },
    "lines": [
        {
            "id": "line-1",
            "speaker": "Narrator",
            "text": "A warm golden fire crackled in the stone hearth as rain whispered against the frosted tavern windows.",
            "delivery": "Warm, measured, and atmospheric storytelling"
        },
        {
            "id": "line-2",
            "speaker": "Lyra Vance",
            "text": "Did you manage to find the ancient star chart, Kaelen? The archivists said it was lost centuries ago.",
            "delivery": "Gentle, thoughtful, and curious"
        },
        {
            "id": "line-3",
            "speaker": "Captain Kaelen",
            "text": "Safe in my coat, scholar. Intact, dry, and glowing just like the old legends promised.",
            "delivery": "Warm, friendly rasp with quiet confidence"
        },
        {
            "id": "line-4",
            "speaker": "Lyra Vance",
            "text": "Then the stories were true. Tomorrow at dawn, our real journey begins.",
            "delivery": "Hopeful wonder, a quiet smile"
        },
        {
            "id": "line-5",
            "speaker": "Captain Kaelen",
            "text": "Drink your warm tea and rest, Lyra. The open horizon waits for no one.",
            "delivery": "Gentle grin, raising an earthen mug"
        }
    ]
}

SEED_CANON: List[Dict[str, Any]] = [
    # CHARACTERS
    {
        "id": "char-lyra-vance",
        "category": "character",
        "name": "Lyra Vance",
        "role": "Exiled Aether-Cartographer",
        "description": "A sharp-witted cartographer expelled from the Ivory Spire for questioning Council secrecy. She wears brass-framed ocular lenses and carries a hand-calibrated resonance compass that hums near energy fissures.",
        "goal": "Recover the lost Sunstone Core from the Obsidian Trench to reignite Oakhaven's fading perimeter ward before the Eclipse of the Seven Moons.",
        "relationships": "Estranged former apprentice to Master Corvus (deep mutual distrust); wary ally and partner to smuggler Captain Kaelen.",
        "tags": ["Protagonist", "Scholar", "Exile", "Aether-Cartography"]
    },
    {
        "id": "char-master-corvus",
        "category": "character",
        "name": "Master Corvus",
        "role": "High Curator of the Ivory Spire",
        "description": "An austere elder scholar draped in heavy indigo robes threaded with silver conductive filaments. He commands the Archives and believes mortal minds are fragile vessels that must be shielded from dangerous ancient truths.",
        "goal": "Preserve the Spire's exclusive monopoly on pre-cataclysm knowledge and prevent anyone from meddling with the Grand Conduit beneath the city.",
        "relationships": "Lyra Vance's former mentor who orchestrated her council banishment; maintains a discreet underground debt to the Iron Syndicate.",
        "tags": ["Scholar", "Archivist", "Antagonist", "Ivory Spire"]
    },
    {
        "id": "char-captain-kaelen",
        "category": "character",
        "name": "Captain Kaelen",
        "role": "Sky-Skiff Smuggler & Deep-Water Pilot",
        "description": "A pragmatic, cynical sky-skiff pilot who knows every thermal vent and flooded canal in Oakhaven. His custom skiff, 'The Zephyr's Wake', is equipped with illicit acoustic dampeners.",
        "goal": "Earn enough aether-coin to buy safe passage for his younger sister to the Outer Archipelago and clear his bounties with the harbor guild.",
        "relationships": "Reluctant partner to Lyra Vance; harbours intense contempt for Ivory Spire scholars; owes gambling debts to the Iron Syndicate.",
        "tags": ["Pilot", "Smuggler", "Ally", "The Low Docks"]
    },

    # PLACES
    {
        "id": "place-sunken-trench",
        "category": "place",
        "name": "The Obsidian Trench",
        "description": "A fractured abyss three miles beneath the flooded ruins of Old Oakhaven. Lit only by bioluminescent abyssal kelp and sapphire thermal steam vents. Pre-cataclysm glass domes provide fragile atmospheric pockets amidst extreme pressures.",
        "defining_detail": "The atmosphere below depth 400 is saturated with corrosive vapor crystals. Inhaling unfiltered Trench vapor causes fatal crystal-lung calcification within twenty minutes; sealed breathing gear or resonance helmets are strictly mandatory.",
        "tags": ["Submerged", "Hazardous", "Ruins", "Abyss"]
    },
    {
        "id": "place-ivory-spire",
        "category": "place",
        "name": "The Ivory Spire",
        "description": "A thousand-foot crystalline citadel towering above New Oakhaven, carved from light-absorbing pearlite stone that vibrates with a faint harmonic chime every sunrise. It houses the Grand Library, the Astrolabe Observatory, and the High Council Chambers.",
        "defining_detail": "Entry past the outer colonnade requires a minted Brass Signet. The Grand Library in the upper tier operates under strict neutrality enforced by clockwork Brass Sentinels.",
        "tags": ["Citadel", "Scholars", "Upper City", "Sanctuary"]
    },
    {
        "id": "place-low-docks",
        "category": "place",
        "name": "The Low Docks",
        "description": "A sprawling network of barnacle-crusted timber walkways, pontoon shanties, and rusted iron sluice gates resting beneath the city's elevated aqueducts. The air smells of salt brine, fried fish, and burnt mineral oil.",
        "defining_detail": "The primary haven for black-market aether salvage, untaxed cargo exchanges, and skiff pilots seeking off-the-record repairs.",
        "tags": ["Harbor", "Underbelly", "Canals", "Waterfront"]
    },

    # EVENTS
    {
        "id": "event-great-shattering",
        "category": "event",
        "name": "The Great Shattering (Year 412)",
        "description": "A catastrophic rupture triggered when the city's primary Grand Conduit suffered an energetic resonance cascade during the Twin Solstice. The shockwave cracked the continental shelf, plunging Old Oakhaven into the ocean and permanently dividing the metropolis into the Upper Spire and the flooded Lower Depths.",
        "tags": ["Cataclysm", "History", "Origin", "Geological"]
    },
    {
        "id": "event-treaty-seven-bells",
        "category": "event",
        "name": "The Treaty of the Seven Bells (Year 425)",
        "description": "A landmark peace agreement signed by the Scholarly Enclave and the Merchant Fleet Guild following a brutal five-month supply blockade. The treaty guaranteed dock trade autonomy while declaring the Ivory Spire Grand Library inviolate neutral territory.",
        "tags": ["Treaty", "Law", "Diplomacy", "Grand Library"]
    },
    {
        "id": "event-banishment-lyra",
        "category": "event",
        "name": "The Banishment of Lyra Vance (Year 438)",
        "description": "A closed-door tribunal convened by the Scholarly Council. Master Corvus brought charges of heresy and unauthorized subterranean cartography after Lyra discovered unrecorded excavation tunnels leading toward the dormant pre-cataclysm reactor.",
        "tags": ["Tribunal", "Exile", "Secret", "Recent"]
    },

    # WORLD RULES
    {
        "id": "rule-aetheric-resonance",
        "category": "rule",
        "name": "The Law of Aetheric Resonance (Rule #1 - Contact Toxicity)",
        "description": "Raw, unrefined Aether cannot be touched with bare organic flesh. Without an attuned catalyst lens or lead-lined insulated gauntlets, direct contact causes instantaneous cellular calcification, turning skin, muscle, and bone into brittle obsidian-black glass within seconds.",
        "tags": ["Magic System", "Physical Law", "Lethal", "Aether"]
    },
    {
        "id": "rule-trench-toxicity",
        "category": "rule",
        "name": "Atmospheric Toxicity of the Trench (Rule #2 - Respiratory Hazard)",
        "description": "Ambient mist in the Obsidian Trench below Depth 400 is heavily saturated with volatile crystal aerosols. Anyone who breathes the unfiltered trench air contracts rapid crystal-lung, causing respiratory failure within twenty minutes. Airtight pressure helmets or charcoal-aether filters are non-negotiable.",
        "tags": ["Environment", "Survival", "Medical", "Trench"]
    },
    {
        "id": "rule-sanctuary-seven-bells",
        "category": "rule",
        "name": "The Sanctum of the Seven Bells (Rule #3 - Weapon Prohibition)",
        "description": "Drawing, unsheathing, or brandishing any metallic blade, firearm, or armed projectile inside the Grand Library of the Ivory Spire immediately triggers the dormant clockwork Brass Sentinels embedded in the masonry. Sentinels will pacify the offender with lethal force.",
        "tags": ["Sanctuary", "Law", "Weapons", "Grand Library"]
    },
    {
        "id": "rule-sunstone-polarity",
        "category": "rule",
        "name": "Sunstone Polarity & Eclipse Recharge (Rule #4 - Energy Limits)",
        "description": "A Sunstone Core can only be safely recharged when exposed to solar radiation during a celestial planetary alignment. Forcing an energetic recharge or drawing power from a depleted core shatters its crystalline lattice, permanently destroying the core.",
        "tags": ["Artifacts", "Energy", "Limits", "Celestial"]
    }
]


class LoreStore:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        try:
            os.makedirs(data_dir, exist_ok=True)
        except Exception:
            pass
        self.file_path = os.path.join(data_dir, "canon_db.json")
        try:
            self._ensure_initialized()
        except Exception:
            pass

    def _ensure_initialized(self):
        if not os.path.exists(self.file_path):
            self.reset_to_seed()
        else:
            # Upgrade existing DB to ensure notes and audio_scene exist
            data = self.load_data()
            modified = False
            if "notes" not in data:
                data["notes"] = copy.deepcopy(SEED_NOTES)
                modified = True
            if "audio_scene" not in data or data.get("audio_scene", {}).get("engine") != "elevenlabs":
                data["audio_scene"] = copy.deepcopy(DEFAULT_AUDIO_SCENE)
                modified = True
            if modified:
                self.save_data(data)

    def load_data(self) -> Dict[str, Any]:
        # Prefer serverless mutable /tmp copy if available
        tmp_path = os.path.join("/tmp", "canon_db.json")
        if os.path.exists(tmp_path):
            try:
                with open(tmp_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception:
            alt_path = os.path.join(os.getcwd(), "lorekeeper", "data", "canon_db.json")
            if os.path.exists(alt_path):
                try:
                    with open(alt_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
            return self.reset_to_seed()

    def save_data(self, data: Dict[str, Any]):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (OSError, IOError, PermissionError):
            # Serverless fallback (e.g. Vercel read-only filesystem)
            tmp_path = os.path.join("/tmp", "canon_db.json")
            try:
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

    def reset_to_seed(self) -> Dict[str, Any]:
        data = {
            "project": copy.deepcopy(DEFAULT_PROJECT),
            "entries": copy.deepcopy(SEED_CANON),
            "notes": copy.deepcopy(SEED_NOTES),
            "audio_scene": copy.deepcopy(DEFAULT_AUDIO_SCENE)
        }
        self.save_data(data)
        return data

    def get_project(self) -> Dict[str, Any]:
        data = self.load_data()
        return data.get("project", DEFAULT_PROJECT)

    def get_all_entries(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self.load_data()
        entries = data.get("entries", [])
        if category and category != "all":
            return [e for e in entries if e.get("category") == category]
        return entries

    def get_entry_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        data = self.load_data()
        for e in data.get("entries", []):
            if e.get("id") == entry_id:
                return e
        return None

    def add_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self.load_data()
        entry_id = entry_data.get("id") or f"{entry_data.get('category', 'entry')}-{uuid.uuid4().hex[:8]}"
        
        # Format tags
        tags = entry_data.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        new_entry = {
            "id": entry_id,
            "category": entry_data.get("category", "rule"),
            "name": entry_data.get("name", "Untitled Lore Entry").strip(),
            "description": entry_data.get("description", "").strip(),
            "tags": tags
        }

        # Optional fields based on category
        if entry_data.get("category") == "character":
            if entry_data.get("role"):
                new_entry["role"] = entry_data.get("role").strip()
            if entry_data.get("goal"):
                new_entry["goal"] = entry_data.get("goal").strip()
            if entry_data.get("relationships"):
                new_entry["relationships"] = entry_data.get("relationships").strip()
        elif entry_data.get("category") == "place":
            if entry_data.get("defining_detail"):
                new_entry["defining_detail"] = entry_data.get("defining_detail").strip()

        data["entries"].append(new_entry)
        self.save_data(data)
        return new_entry

    def update_entry(self, entry_id: str, entry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = self.load_data()
        target_idx = None
        for i, e in enumerate(data.get("entries", [])):
            if e.get("id") == entry_id:
                target_idx = i
                break

        if target_idx is None:
            return None

        current = data["entries"][target_idx]
        tags = entry_data.get("tags", current.get("tags", []))
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        updated_entry = {
            "id": entry_id,
            "category": entry_data.get("category", current.get("category")),
            "name": entry_data.get("name", current.get("name")).strip(),
            "description": entry_data.get("description", current.get("description")).strip(),
            "tags": tags
        }

        # Handle category-specific fields
        if updated_entry["category"] == "character":
            updated_entry["role"] = entry_data.get("role", current.get("role", ""))
            updated_entry["goal"] = entry_data.get("goal", current.get("goal", ""))
            updated_entry["relationships"] = entry_data.get("relationships", current.get("relationships", ""))
        elif updated_entry["category"] == "place":
            updated_entry["defining_detail"] = entry_data.get("defining_detail", current.get("defining_detail", ""))

        data["entries"][target_idx] = updated_entry
        self.save_data(data)
        return updated_entry

    def delete_entry(self, entry_id: str) -> bool:
        data = self.load_data()
        original_len = len(data.get("entries", []))
        data["entries"] = [e for e in data.get("entries", []) if e.get("id") != entry_id]
        if len(data["entries"]) < original_len:
            self.save_data(data)
            return True
        return False

    # Notes & Draft Ideas Management (Separate from confirmed canon)
    def get_notes(self) -> List[Dict[str, Any]]:
        data = self.load_data()
        return data.get("notes", [])

    def add_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self.load_data()
        if "notes" not in data:
            data["notes"] = []
        note_id = note_data.get("id") or f"note-{uuid.uuid4().hex[:8]}"
        new_note = {
            "id": note_id,
            "title": note_data.get("title", "Untitled Draft Note").strip(),
            "character": note_data.get("character", "General"),
            "category": note_data.get("category", "Scene Idea"),
            "text": note_data.get("text", "").strip(),
            "why_it_fits": note_data.get("why_it_fits", ""),
            "created_at": "Saved recently"
        }
        data["notes"].insert(0, new_note)
        self.save_data(data)
        return new_note

    def delete_note(self, note_id: str) -> bool:
        data = self.load_data()
        original_len = len(data.get("notes", []))
        data["notes"] = [n for n in data.get("notes", []) if n.get("id") != note_id]
        if len(data["notes"]) < original_len:
            self.save_data(data)
            return True
        return False

    # Audio Studio Scene Management
    def get_audio_scene(self) -> Dict[str, Any]:
        data = self.load_data()
        return data.get("audio_scene", DEFAULT_AUDIO_SCENE)

    def update_audio_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self.load_data()
        data["audio_scene"] = scene_data
        self.save_data(data)
        return scene_data

    def get_stats(self) -> Dict[str, int]:
        entries = self.get_all_entries()
        notes = self.get_notes()
        return {
            "total": len(entries),
            "characters": sum(1 for e in entries if e.get("category") == "character"),
            "places": sum(1 for e in entries if e.get("category") == "place"),
            "events": sum(1 for e in entries if e.get("category") == "event"),
            "rules": sum(1 for e in entries if e.get("category") == "rule"),
            "notes": len(notes)
        }
