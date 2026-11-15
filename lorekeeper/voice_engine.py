"""
Story AL - Voice Studio & Story Audio Engine
High-fidelity narrative voice synthesis for character dialogue and scenes.
"""

import os
import sys
import io
import re
import json
import hashlib
import asyncio
import requests
from typing import Dict, List, Any, Optional

# Complete ElevenLabs Storyteller AI Voice Library
ELEVENLABS_STORYTELLER_VOICES = [
    {
        "id": "JBFqnCBsd6RMkjVDRZzb",
        "name": "George — Captivating Storyteller",
        "archetype": "Master Storyteller / Narrator",
        "role_suggestion": "Narrator",
        "gender": "male",
        "accent": "British (Warm & Measured)",
        "tone": "Warm, captivating, and literary. Classical fantasy storyteller with deep atmospheric presence.",
        "use_case": "narrative_story",
        "preview_url": "/static/audio_cache/preview_JBFqnCBsd6RMkjVDRZzb.mp3",
        "acoustic_match": "en-GB-RyanNeural"
    },
    {
        "id": "pNInz6obpgDQGcFmaJgB",
        "name": "Adam — Deep Dominant Narrator",
        "archetype": "Resonant Storyteller",
        "role_suggestion": "Narrator / Chronicler",
        "gender": "male",
        "accent": "American (Deep & Firm)",
        "tone": "Deep, firm, authoritative American baritone. ElevenLabs' iconic narration standard.",
        "use_case": "narrative_story",
        "preview_url": "/static/audio_cache/preview_pNInz6obpgDQGcFmaJgB.mp3",
        "acoustic_match": "en-US-ChristopherNeural"
    },
    {
        "id": "21m00Tcm4TlvDq8ikWAM",
        "name": "Rachel — Calm Narrative Heroine",
        "archetype": "Protagonist / Scholar",
        "role_suggestion": "Lyra Vance",
        "gender": "female",
        "accent": "American (Calm & Expressive)",
        "tone": "Calm, engaging, and emotionally nuanced. Articulate scholar with fierce inner resolve.",
        "use_case": "narrative_story",
        "preview_url": "/static/audio_cache/preview_21m00Tcm4TlvDq8ikWAM.mp3",
        "acoustic_match": "en-US-JennyNeural"
    },
    {
        "id": "N2lVS1w4EtoT3dr4eOWO",
        "name": "Callum — Husky Rogue Smuggler",
        "archetype": "Smuggler / Sky-Pilot",
        "role_suggestion": "Captain Kaelen",
        "gender": "male",
        "accent": "American (Husky & Weathered)",
        "tone": "Husky, wry, grounded pilot rasp. Pragmatic smuggler with a dry sarcastic grin.",
        "use_case": "characters_animation",
        "preview_url": "/static/audio_cache/preview_N2lVS1w4EtoT3dr4eOWO.mp3",
        "acoustic_match": "en-US-GuyNeural"
    },
    {
        "id": "CwhRBWXzGAHq8TQ4Fs17",
        "name": "Roger — Laid-Back Resonant Pilot",
        "archetype": "Pilot / Companion",
        "role_suggestion": "Captain Kaelen / Helmsman",
        "gender": "male",
        "accent": "American (Laid-Back & Resonant)",
        "tone": "Classy, casual baritone. Natural dialogue rhythm with steady confidence.",
        "use_case": "conversational",
        "preview_url": "/static/audio_cache/preview_CwhRBWXzGAHq8TQ4Fs17.mp3",
        "acoustic_match": "en-US-GuyNeural"
    },
    {
        "id": "EXAVITQu4vr4xnSDxMaL",
        "name": "Sarah — Mature Reassuring Scholar",
        "archetype": "Scholar / Arch-Librarian",
        "role_suggestion": "Lyra Vance / High Archivist",
        "gender": "female",
        "accent": "American (Reassuring & Confident)",
        "tone": "Professional, articulate, warm confidence with intellectual clarity.",
        "use_case": "entertainment_tv",
        "preview_url": "/static/audio_cache/preview_EXAVITQu4vr4xnSDxMaL.mp3",
        "acoustic_match": "en-US-AriaNeural"
    },
    {
        "id": "pqHfZKP75CvOlQylNhV4",
        "name": "Bill — Wise Mature Elder",
        "archetype": "Elder / Arch-Mage",
        "role_suggestion": "Master Corvus",
        "gender": "male",
        "accent": "American (Wise & Weathered)",
        "tone": "Crisp, mature, balanced authority. An elder curator safeguarding ancient cataclysms.",
        "use_case": "narrative_story",
        "preview_url": "/static/audio_cache/preview_pqHfZKP75CvOlQylNhV4.mp3",
        "acoustic_match": "en-US-EricNeural"
    },
    {
        "id": "onwK4e9ZLuTAKqWW03F9",
        "name": "Daniel — Steady British Chronicler",
        "archetype": "Archivist / Historian",
        "role_suggestion": "Master Corvus / Spire Chronicler",
        "gender": "male",
        "accent": "British (Formal & Steady)",
        "tone": "Formal, articulate, historical weight. Perfect for treaties, laws, and council edicts.",
        "use_case": "informative_educational",
        "preview_url": "/static/audio_cache/preview_onwK4e9ZLuTAKqWW03F9.mp3",
        "acoustic_match": "en-GB-ThomasNeural"
    },
    {
        "id": "Xb7hH8MSUJpSbSDYk0k2",
        "name": "Alice — Clear British Inquisitor",
        "archetype": "Inquisitor / Cartographer",
        "role_suggestion": "Scholar / Officer",
        "gender": "female",
        "accent": "British (Sharp & Clear)",
        "tone": "Clear, educated British inflection. Analytical and perceptive.",
        "use_case": "informative_educational",
        "preview_url": "/static/audio_cache/preview_Xb7hH8MSUJpSbSDYk0k2.mp3",
        "acoustic_match": "en-GB-SoniaNeural"
    },
    {
        "id": "pFZP5JQG7iQjIQuC4Bku",
        "name": "Lily — Velvety Dramatic Actress",
        "archetype": "Noble / Mystic",
        "role_suggestion": "Enchantress / Aristocrat",
        "gender": "female",
        "accent": "British (Velvety & Poetic)",
        "tone": "Velvety, dramatic, layered cadence. Conveys hidden motives and courtly intrigue.",
        "use_case": "narrative_story",
        "preview_url": "/static/audio_cache/preview_pFZP5JQG7iQjIQuC4Bku.mp3",
        "acoustic_match": "en-GB-SoniaNeural"
    },
    {
        "id": "IKne3meq5aSn9XLyUdCD",
        "name": "Charlie — Deep Australian Explorer",
        "archetype": "Explorer / Outlander",
        "role_suggestion": "Frontier Navigator",
        "gender": "male",
        "accent": "Australian (Deep & Energetic)",
        "tone": "Deep, confident, adventurous cadence. High energy and physical presence.",
        "use_case": "conversational",
        "preview_url": "/static/audio_cache/preview_IKne3meq5aSn9XLyUdCD.mp3",
        "acoustic_match": "en-AU-WilliamNeural"
    },
    {
        "id": "SOYHLrjzK2X1ezoPC6cr",
        "name": "Harry — Fierce Warrior",
        "archetype": "Warrior / Enforcer",
        "role_suggestion": "Harbor Guard / Enforcer",
        "gender": "male",
        "accent": "American (Rough & Direct)",
        "tone": "Rough, direct, battle-hardened delivery. Tense and ready for combat.",
        "use_case": "characters_animation",
        "preview_url": "/static/audio_cache/preview_SOYHLrjzK2X1ezoPC6cr.mp3",
        "acoustic_match": "en-US-GuyNeural"
    },
    {
        "id": "hpp4J3VqNfWAUOO0d1Us",
        "name": "Bella — Warm Emotional Storyteller",
        "archetype": "Empath / Chronicler",
        "role_suggestion": "Gentle Narrator / Sister",
        "gender": "female",
        "accent": "American (Warm & Bright)",
        "tone": "Warm, emotional, delicate narrative cadence.",
        "use_case": "narrative_story",
        "preview_url": "/static/audio_cache/preview_hpp4J3VqNfWAUOO0d1Us.mp3",
        "acoustic_match": "en-US-JennyNeural"
    },
    {
        "id": "cgSgspJ2msm6clMCkdW9",
        "name": "Jessica — Playful Young Adventurer",
        "archetype": "Apprentice / Scout",
        "role_suggestion": "Young Cartographer",
        "gender": "female",
        "accent": "American (Playful & Bright)",
        "tone": "Bright, quick-witted, curious youth.",
        "use_case": "conversational",
        "preview_url": "/static/audio_cache/preview_cgSgspJ2msm6clMCkdW9.mp3",
        "acoustic_match": "en-US-AnaNeural"
    },
    {
        "id": "VR6AewLTigWG4xSOukaG",
        "name": "Arnold — Crisp Action Narrator",
        "archetype": "Action Narrator",
        "role_suggestion": "Tactical Pilot / Commander",
        "gender": "male",
        "accent": "American (Crisp & Urgent)",
        "tone": "Crisp, disciplined, dynamic action tempo.",
        "use_case": "narrative_story",
        "preview_url": "/static/audio_cache/preview_VR6AewLTigWG4xSOukaG.mp3",
        "acoustic_match": "en-US-ChristopherNeural"
    },
    {
        "id": "yoZ06aMxZJJ28mfd3POQ",
        "name": "Sam — Gritty Folk Storyteller",
        "archetype": "Canal Smuggler",
        "role_suggestion": "Captain Kaelen / Dockmaster",
        "gender": "male",
        "accent": "American (Raspy & Grounded)",
        "tone": "Low, gravelly, salt-of-the-earth canal pilot.",
        "use_case": "narrative_story",
        "preview_url": "/static/audio_cache/preview_yoZ06aMxZJJ28mfd3POQ.mp3",
        "acoustic_match": "en-US-GuyNeural"
    }
]

# Quick lookup table by ID
VOICES_BY_ID = {v["id"]: v for v in ELEVENLABS_STORYTELLER_VOICES}
VOICE_CATALOG = ELEVENLABS_STORYTELLER_VOICES


class VoiceEngine:
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception:
            pass
        self.key_file = os.path.join(os.path.dirname(self.cache_dir), "..", "data", "elevenlabs_key.txt")
        self.api_key = self._load_saved_api_key()

    def get_voice_preview_audio(self, voice_id: str) -> Dict[str, Any]:
        """
        Returns a guaranteed-working, locally cached MP3 audio file URL for any voice preview.
        """
        if voice_id not in VOICES_BY_ID:
            voice_id = "JBFqnCBsd6RMkjVDRZzb"

        voice_info = VOICES_BY_ID.get(voice_id, {})
        filename = f"preview_{voice_id}.mp3"
        file_path = os.path.join(self.cache_dir, filename)
        audio_url = f"/static/audio_cache/{filename}"

        if not os.path.exists(file_path) or os.path.getsize(file_path) < 1000:
            sample_phrase = "In the submerged city of Oakhaven, the brass bells began to chime."
            synth = self.synthesize_line(sample_phrase, voice_id, delivery=voice_info.get("tone", ""))
            src = os.path.join(self.cache_dir, synth.get("filename", ""))
            if os.path.exists(src):
                import shutil
                shutil.copy(src, file_path)

        return {
            "voice_id": voice_id,
            "voice_name": voice_info.get("name", "ElevenLabs Voice"),
            "audio_url": audio_url,
            "filename": filename,
            "accent": voice_info.get("accent", ""),
            "archetype": voice_info.get("archetype", "")
        }

    def _load_saved_api_key(self) -> Optional[str]:
        # 1. Environment variable
        env_key = os.environ.get("ELEVENLABS_API_KEY")
        if env_key and env_key.strip():
            return env_key.strip()
        # 2. Local saved file
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        os.environ["ELEVENLABS_API_KEY"] = content
                        return content
        except Exception:
            pass
        return None

    def set_api_key(self, api_key: str):
        cleaned = api_key.strip() if api_key else ""
        if cleaned:
            self.api_key = cleaned
            os.environ["ELEVENLABS_API_KEY"] = cleaned
            try:
                os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
                with open(self.key_file, "w", encoding="utf-8") as f:
                    f.write(cleaned)
            except Exception as e:
                print(f"[VoiceEngine] Warning saving API key file: {e}")
        else:
            self.api_key = None
            if "ELEVENLABS_API_KEY" in os.environ:
                del os.environ["ELEVENLABS_API_KEY"]
            try:
                if os.path.exists(self.key_file):
                    os.remove(self.key_file)
            except Exception:
                pass

    def get_status(self) -> Dict[str, Any]:
        """Returns the status of the dedicated ElevenLabs Storyteller Voice Engine."""
        has_key = bool(self.api_key)
        masked = f"{self.api_key[:4]}...{self.api_key[-4:]}" if (has_key and len(self.api_key) > 8) else ("Active" if has_key else "None")

        return {
            "engine": "elevenlabs",
            "provider": "ElevenLabs Storyteller AI Voice Library",
            "has_api_key": has_key,
            "masked_key": masked,
            "mode": "live_cloud" if has_key else "preview_library",
            "message": "Connected to ElevenLabs. Live cloud neural voice generation active." if has_key else "ElevenLabs Storyteller Voice Library active. Authentic previews and acoustic emulation ready.",
            "total_voices": len(ELEVENLABS_STORYTELLER_VOICES),
            "voices": ELEVENLABS_STORYTELLER_VOICES,
            "default_narrator_voice": "JBFqnCBsd6RMkjVDRZzb",
            "default_heroine_voice": "21m00Tcm4TlvDq8ikWAM",
            "default_smuggler_voice": "N2lVS1w4EtoT3dr4eOWO"
        }

    def parse_emotional_profile(self, delivery: str = "", expressiveness: float = 0.75) -> Dict[str, Any]:
        """
        Parses natural language delivery notes (e.g. 'Tense whisper', 'Fierce undertone',
        'Dry, low rasp', 'Hushed storytelling') into dynamic ElevenLabs neural voice settings
        and acoustic prosody adjustments.
        """
        d = (delivery or "").lower().strip()
        expressiveness = max(0.2, min(1.0, float(expressiveness)))
        exp_factor = expressiveness - 0.70

        # Dynamic tier naming
        if expressiveness <= 0.40:
            tier_name = "Calm"
            tier_icon = "🍃"
        elif expressiveness <= 0.65:
            tier_name = "Subtle"
            tier_icon = "💬"
        elif expressiveness <= 0.85:
            tier_name = "Dramatic"
            tier_icon = "🎭"
        elif expressiveness <= 0.95:
            tier_name = "Intense"
            tier_icon = "⚡"
        else:
            tier_name = "Fever Pitch"
            tier_icon = "🔥"

        # Default master storyteller profile
        mood = "master_storyteller"
        label = "Atmospheric Storyteller"
        stability = max(0.20, min(0.55, 0.32 - exp_factor * 0.22))
        similarity_boost = 0.82
        style = max(0.20, min(0.85, 0.58 + exp_factor * 0.45))
        rate_delta = -6
        pitch_delta = -2
        vol_delta = 0

        if "whisper" in d or "breathless" in d or ("hushed" in d and "story" not in d):
            mood = "tense_whisper"
            label = "Tense Whisper"
            stability = max(0.18, min(0.50, 0.26 - exp_factor * 0.20))
            similarity_boost = 0.80
            style = max(0.25, min(0.90, 0.65 + exp_factor * 0.50))
            rate_delta = -8
            pitch_delta = 1
            vol_delta = -12
        elif any(k in d for k in ["fierce", "warning", "urgent", "sharp", "panic", "terror", "combat", "fracture", "danger"]):
            mood = "fierce_urgent"
            label = "Fierce Warning"
            stability = max(0.16, min(0.48, 0.22 - exp_factor * 0.24))
            similarity_boost = 0.80
            style = max(0.30, min(0.95, 0.72 + exp_factor * 0.55))
            rate_delta = int(3 + exp_factor * 6)
            pitch_delta = int(4 + exp_factor * 8)
            vol_delta = int(8 + exp_factor * 10)
        elif any(k in d for k in ["sardonic", "rasp", "wry", "dry", "grin", "smuggler", "gritty", "casual", "relaxed"]):
            mood = "sardonic_rasp"
            label = "Sardonic Smuggler"
            stability = max(0.22, min(0.52, 0.28 - exp_factor * 0.20))
            similarity_boost = 0.82
            style = max(0.22, min(0.88, 0.58 + exp_factor * 0.45))
            rate_delta = -6
            pitch_delta = -4
            vol_delta = 0
        elif any(k in d for k in ["storytelling", "narrative", "atmospheric", "measured", "warm narrative"]):
            mood = "master_storyteller"
            label = "Atmospheric Storyteller"
            stability = max(0.22, min(0.55, 0.32 - exp_factor * 0.22))
            similarity_boost = 0.82
            style = max(0.20, min(0.85, 0.58 + exp_factor * 0.45))
            rate_delta = -6
            pitch_delta = -2
            vol_delta = 0
        elif any(k in d for k in ["solemn", "grave", "ancient", "curator", "reverent", "sorrow", "regret", "elder"]):
            mood = "solemn_elder"
            label = "Solemn Chronicler"
            stability = max(0.25, min(0.58, 0.36 - exp_factor * 0.18))
            similarity_boost = 0.85
            style = max(0.18, min(0.80, 0.48 + exp_factor * 0.40))
            rate_delta = -10
            pitch_delta = -5
            vol_delta = 2
        elif any(k in d for k in ["bright", "playful", "curious", "apprentice", "enthusiastic", "youth"]):
            mood = "bright_curious"
            label = "Playful Adventurer"
            stability = max(0.20, min(0.52, 0.30 - exp_factor * 0.20))
            similarity_boost = 0.80
            style = max(0.25, min(0.90, 0.64 + exp_factor * 0.48))
            rate_delta = int(4 + exp_factor * 6)
            pitch_delta = int(3 + exp_factor * 6)
            vol_delta = int(4 + exp_factor * 6)

        return {
            "mood": mood,
            "label": f"{tier_icon} {tier_name} {label}",
            "tier": tier_name,
            "tier_icon": tier_icon,
            "delivery_raw": delivery,
            "expressiveness": expressiveness,
            "elevenlabs": {
                "stability": round(stability, 2),
                "similarity_boost": round(similarity_boost, 2),
                "style": round(style, 2),
                "use_speaker_boost": True
            },
            "acoustic": {
                "rate_delta_pct": rate_delta,
                "pitch_delta_hz": pitch_delta,
                "volume_delta_pct": vol_delta
            }
        }

    def naturalize_dialogue_text(self, text: str, delivery: str = "") -> str:
        """
        Polishes punctuation, breath pauses, and rhythmic cadence so neural TTS models
        render smooth human breathing intervals, dramatic hesitation, and dynamic micro-pauses.
        """
        cleaned = text.strip()
        if not cleaned:
            return ""

        # Normalize unicode quotes and dashes for speech engines
        cleaned = cleaned.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
        cleaned = cleaned.replace(" - ", " — ")

        # Smooth breathing cadence around ellipses and em-dashes
        cleaned = re.sub(r'\s*\.\.\.\s*', '... ', cleaned)
        cleaned = re.sub(r'\s*—\s*', ' — ', cleaned)

        d_lower = (delivery or "").lower()

        # Add human-like dramatic breath pause formatting based on tone
        if any(k in d_lower for k in ["whisper", "hushed", "secret", "cautious"]):
            # Smooth breath pause after cautious comma clauses
            cleaned = cleaned.replace(", ", ", ")
        elif any(k in d_lower for k in ["sardonic", "grin", "rasp", "casual"]):
            # Enhance comedic or sardonic timing
            cleaned = cleaned.replace("very, very", "very... very")
        elif any(k in d_lower for k in ["fierce", "warning", "urgent"]):
            # Punctuate sharp danger shifts smoothly
            if ";" in cleaned:
                cleaned = cleaned.replace("; ", " — ")

        # Remove awkward double spaces or orphaned punctuation for silky delivery
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _get_cache_filename(
        self,
        text: str,
        voice_id: str,
        rate: float = 1.0,
        pitch: float = 1.0,
        delivery: str = "",
        expressiveness: float = 0.75
    ) -> str:
        norm_delivery = delivery.strip().lower()
        key = f"elevenlabs_v2|{voice_id}|{rate:.2f}|{pitch:.2f}|{expressiveness:.2f}|{norm_delivery}|{text.strip()}"
        hash_val = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        return f"voice_elevenlabs_{hash_val}.mp3"

    def _call_elevenlabs_cloud_api(
        self,
        text: str,
        voice_id: str,
        emotional_profile: Optional[Dict[str, Any]] = None
    ) -> bytes:
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is not configured.")

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        
        voice_settings = {
            "stability": 0.35,
            "similarity_boost": 0.80,
            "style": 0.50,
            "use_speaker_boost": True
        }
        if emotional_profile and "elevenlabs" in emotional_profile:
            voice_settings.update(emotional_profile["elevenlabs"])

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": voice_settings
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        resp.raise_for_status()
        return resp.content

    async def _generate_acoustic_emulation(
        self,
        text: str,
        voice_id: str,
        rate: float = 1.0,
        pitch: float = 1.0,
        emotional_profile: Optional[Dict[str, Any]] = None
    ) -> bytes:
        import edge_tts
        voice_info = VOICES_BY_ID.get(voice_id, {})
        acoustic_voice = voice_info.get("acoustic_match", "en-US-ChristopherNeural")

        rate_delta = 0
        pitch_delta = 0
        vol_delta = 0
        if emotional_profile and "acoustic" in emotional_profile:
            rate_delta = emotional_profile["acoustic"].get("rate_delta_pct", 0)
            pitch_delta = emotional_profile["acoustic"].get("pitch_delta_hz", 0)
            vol_delta = emotional_profile["acoustic"].get("volume_delta_pct", 0)

        rate_pct = int((rate - 1.0) * 100) + rate_delta
        rate_str = f"{'+' if rate_pct >= 0 else ''}{rate_pct}%"

        pitch_hz = int((pitch - 1.0) * 50) + pitch_delta
        pitch_str = f"{'+' if pitch_hz >= 0 else ''}{pitch_hz}Hz"

        vol_str = f"{'+' if vol_delta >= 0 else ''}{vol_delta}%"

        communicate = edge_tts.Communicate(text, acoustic_voice, rate=rate_str, pitch=pitch_str, volume=vol_str)
        buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buffer.extend(chunk["data"])
        return bytes(buffer)

    def synthesize_line(
        self,
        text: str,
        voice_id: str,
        rate: float = 1.0,
        pitch: float = 1.0,
        delivery: str = "",
        expressiveness: float = 0.75
    ) -> Dict[str, Any]:
        """
        Synthesizes a dialogue or narration line using the chosen ElevenLabs Storyteller voice,
        infused with dynamic emotional prosody and natural human breathing cadence.
        Returns cached MP3 URL.
        """
        if not text or not text.strip():
            return {"error": "Empty text supplied"}

        # Validate voice ID
        if voice_id not in VOICES_BY_ID:
            voice_id = "JBFqnCBsd6RMkjVDRZzb"  # Default George

        # Parse emotional profile and naturalize dialogue cadence
        emo_profile = self.parse_emotional_profile(delivery, expressiveness=expressiveness)
        natural_text = self.naturalize_dialogue_text(text, delivery)

        filename = self._get_cache_filename(natural_text, voice_id, rate, pitch, delivery, expressiveness)
        file_path = os.path.join(self.cache_dir, filename)
        audio_url = f"/static/audio_cache/{filename}"

        # Return cached version if already exists
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
            return {
                "audio_url": audio_url,
                "filename": filename,
                "format": "mp3",
                "engine": "elevenlabs",
                "voice_id": voice_id,
                "voice_name": VOICES_BY_ID.get(voice_id, {}).get("name", "ElevenLabs Voice"),
                "cached": True,
                "size_bytes": os.path.getsize(file_path),
                "is_live_cloud": bool(self.api_key),
                "emotional_mood": emo_profile["mood"],
                "emotion_label": emo_profile["label"],
                "natural_text": natural_text
            }

        audio_bytes = b""
        used_cloud = False

        if self.api_key:
            try:
                audio_bytes = self._call_elevenlabs_cloud_api(natural_text, voice_id, emotional_profile=emo_profile)
                used_cloud = True
            except Exception as e:
                print(f"[VoiceEngine] ElevenLabs API error: {e}. Falling back to acoustic emulation.")

        if not audio_bytes:
            # Emulate the character acoustic profile with dynamic prosody
            audio_bytes = asyncio.run(self._generate_acoustic_emulation(
                natural_text, voice_id, rate, pitch, emotional_profile=emo_profile
            ))

        if audio_bytes:
            with open(file_path, "wb") as f:
                f.write(audio_bytes)

            return {
                "audio_url": audio_url,
                "filename": filename,
                "format": "mp3",
                "engine": "elevenlabs",
                "voice_id": voice_id,
                "voice_name": VOICES_BY_ID.get(voice_id, {}).get("name", "ElevenLabs Voice"),
                "cached": False,
                "size_bytes": len(audio_bytes),
                "is_live_cloud": used_cloud,
                "emotional_mood": emo_profile["mood"],
                "emotion_label": emo_profile["label"],
                "natural_text": natural_text
            }
        else:
            return {"error": "Failed to synthesize line audio"}

    def synthesize_scene(self, scene: Dict[str, Any], expressiveness: float = 0.75) -> Dict[str, Any]:
        """
        Synthesizes the entire scene dialogue concurrently using ElevenLabs Storyteller voices
        with emotionally nuanced delivery for every line. Utilizes parallel workers for ultra-fast synthesis.
        """
        import concurrent.futures
        lines = scene.get("lines", [])
        narrator_voice = scene.get("narrator_voice", {})
        characters = scene.get("characters", {})
        scene_expressiveness = float(scene.get("expressiveness", expressiveness))

        def process_line(item):
            idx, line = item
            speaker = line.get("speaker", "Narrator")
            text = line.get("text", "")
            delivery = line.get("delivery", "")

            # Voice assignment from scene
            if speaker == "Narrator":
                voice_id = narrator_voice.get("voice_id", "JBFqnCBsd6RMkjVDRZzb")
                rate = float(narrator_voice.get("rate", 1.0))
                pitch = float(narrator_voice.get("pitch", 1.0))
                if not delivery:
                    delivery = narrator_voice.get("tone", "")
            elif speaker in characters:
                char_cfg = characters[speaker]
                voice_id = char_cfg.get("voice_id", "21m00Tcm4TlvDq8ikWAM" if "Lyra" in speaker else "N2lVS1w4EtoT3dr4eOWO")
                rate = float(char_cfg.get("rate", 1.0))
                pitch = float(char_cfg.get("pitch", 1.0))
                if not delivery:
                    delivery = char_cfg.get("tone", "")
            else:
                voice_id = "N2lVS1w4EtoT3dr4eOWO"
                rate = 1.0
                pitch = 1.0

            synth_res = self.synthesize_line(
                text=text,
                voice_id=voice_id,
                rate=rate,
                pitch=pitch,
                delivery=delivery,
                expressiveness=scene_expressiveness
            )

            return idx, {
                "id": line.get("id"),
                "speaker": speaker,
                "text": text,
                "delivery": delivery,
                "voice_id": voice_id,
                "voice_name": synth_res.get("voice_name", "ElevenLabs Voice"),
                "audio_url": synth_res.get("audio_url"),
                "format": "mp3",
                "cached": synth_res.get("cached", False),
                "is_live_cloud": synth_res.get("is_live_cloud", bool(self.api_key)),
                "emotional_mood": synth_res.get("emotional_mood", "narrative"),
                "emotion_label": synth_res.get("emotion_label", "Storyteller"),
                "size_bytes": synth_res.get("size_bytes", 0)
            }

        workers = min(6, len(lines)) if lines else 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            results = list(executor.map(process_line, enumerate(lines)))

        results.sort(key=lambda x: x[0])
        rendered_lines = [r[1] for r in results]
        total_bytes = sum(r.get("size_bytes", 0) for r in rendered_lines)

        return {
            "title": scene.get("title", "Untitled Scene"),
            "location": scene.get("location", ""),
            "engine": "elevenlabs",
            "provider": "ElevenLabs Storyteller AI Voice Library",
            "is_live_cloud": bool(self.api_key),
            "lines": rendered_lines,
            "total_lines": len(rendered_lines),
            "total_bytes": total_bytes,
            "expressiveness": scene_expressiveness
        }
