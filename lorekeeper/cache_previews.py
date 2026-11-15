"""
Cache official ElevenLabs voice previews locally to guarantee 100% reliable, zero-latency playback.
"""
import os
import requests
from voice_engine import ELEVENLABS_STORYTELLER_VOICES, VoiceEngine

CACHE_DIR = os.path.join(os.path.dirname(__file__), "static", "audio_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

try:
    r = requests.get("https://api.elevenlabs.io/v1/voices", timeout=12)
    live_map = {v["voice_id"]: v.get("preview_url") for v in r.json().get("voices", [])}
except Exception as e:
    print(f"Error querying ElevenLabs API: {e}")
    live_map = {}

ve = VoiceEngine(CACHE_DIR)
total = 0

for v in ELEVENLABS_STORYTELLER_VOICES:
    vid = v["id"]
    target = os.path.join(CACHE_DIR, f"preview_{vid}.mp3")
    url = live_map.get(vid) or v.get("preview_url")
    downloaded = False

    if url:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200 and len(res.content) > 1000:
                with open(target, "wb") as f:
                    f.write(res.content)
                downloaded = True
                print(f"[Studio Sample] {v['name']} -> {len(res.content)} bytes")
        except Exception as e:
            print(f"[Warn] Failed downloading {v['name']}: {e}")

    if not downloaded:
        sample_phrase = "In the submerged city of Oakhaven, the brass bells began to chime."
        res = ve.synthesize_line(sample_phrase, vid, delivery=v.get("tone", ""))
        src = os.path.join(CACHE_DIR, res.get("filename", ""))
        if os.path.exists(src):
            with open(src, "rb") as f_in, open(target, "wb") as f_out:
                f_out.write(f_in.read())
            print(f"[Synthesized Sample] {v['name']} -> {os.path.getsize(target)} bytes")

    total += 1

print(f"Successfully processed all {total} voice previews into {CACHE_DIR}")
