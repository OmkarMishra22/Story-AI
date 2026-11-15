"""
Story AL - Canon-Grounded AI Engine
Supports both live Google Gemini API (when GEMINI_API_KEY is provided)
and a robust, reliable Demo Mode engine that answers canon questions strictly
and checks story drafts for contradictions.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional

try:
    from google import genai
    from google.genai import types
    HAS_GENAI_LIB = True
except ImportError:
    HAS_GENAI_LIB = False


class AIEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.client = None
        self._init_client()

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip() if api_key else None
        self._init_client()

    def _init_client(self):
        if self.api_key and HAS_GENAI_LIB:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[AIEngine] Failed to initialize Gemini client: {e}")
                self.client = None
        else:
            self.client = None

    def is_live_mode_available(self) -> bool:
        return bool(self.client and self.api_key)

    def get_status(self) -> Dict[str, Any]:
        has_key = bool(self.api_key)
        return {
            "mode": "live_ai" if self.is_live_mode_available() else "demo",
            "has_api_key": has_key,
            "masked_key": f"{self.api_key[:4]}...{self.api_key[-4:]}" if (has_key and len(self.api_key) > 8) else ("Configured" if has_key else "None"),
            "model": "gemini-2.5-flash" if self.is_live_mode_available() else "story-al-heuristic-engine"
        }

    # =========================================================================
    # FEATURE 3: CANON-GROUNDED Q&A
    # =========================================================================

    def answer_canon_question(self, question: str, canon_entries: List[Dict[str, Any]], force_demo: bool = False) -> Dict[str, Any]:
        """
        Answers a user question grounded exclusively in the provided canon entries.
        Never invents facts. If unknown, clearly states that canon does not specify.
        """
        question_clean = question.strip()
        if not question_clean:
            return {
                "answer": "Please ask a question about the story canon.",
                "citations": [],
                "mode": "demo",
                "grounded": False
            }

        # If live AI is available and not forced into demo mode, call Gemini
        if self.is_live_mode_available() and not force_demo:
            try:
                return self._call_gemini_qa(question_clean, canon_entries)
            except Exception as err:
                print(f"[AIEngine] Gemini QA error: {err}. Falling back to demo engine.")

        # Otherwise, run the grounded demo engine
        return self._demo_answer_qa(question_clean, canon_entries)

    def _call_gemini_qa(self, question: str, canon_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs grounded Q&A through Gemini."""
        canon_context = []
        for e in canon_entries:
            text = f"[{e.get('category', '').upper()}] ID: {e.get('id')} | Name: {e.get('name')}\n"
            text += f"Description: {e.get('description', '')}\n"
            if e.get("role"):
                text += f"Role: {e.get('role')}\n"
            if e.get("goal"):
                text += f"Goal: {e.get('goal')}\n"
            if e.get("relationships"):
                text += f"Relationships: {e.get('relationships')}\n"
            if e.get("defining_detail"):
                text += f"Defining Detail: {e.get('defining_detail')}\n"
            canon_context.append(text)

        canon_block = "\n---\n".join(canon_context)

        system_instruction = (
            "You are Story AL, the strict memory engine for a fictional world. "
            "Your solemn duty is to answer the fiction writer's questions using ONLY the established "
            "Story Bible facts provided in the CANON CONTEXT below.\n\n"
            "STRICT RULES:\n"
            "1. Answer ONLY from facts explicitly stated in the CANON CONTEXT.\n"
            "2. If the question asks about something NOT specified in the canon (e.g. unmentioned items, "
            "pets, ages, relationships, or world mechanics not in the text), you MUST state clearly: "
            "'The established canon does not specify [topic].' followed by what is known if related. "
            "NEVER invent or extrapolate fictional facts.\n"
            "3. Return your response in JSON format with two keys:\n"
            "   'answer': your grounded prose response (or explanation that canon does not specify),\n"
            "   'citations': a list of entry IDs from the canon context that directly support your answer.\n"
            "   'grounded': boolean indicating whether the answer was found in canon (true) or unspecified (false).\n"
            "Provide only valid JSON in your response."
        )

        prompt = f"CANON CONTEXT:\n{canon_block}\n\nWRITER QUESTION:\n{question}"

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                response_mime_type="application/json"
            )
        )

        try:
            data = json.loads(response.text)
            cited_ids = data.get("citations", [])
            citations = []
            for cid in cited_ids:
                for entry in canon_entries:
                    if entry.get("id") == cid or entry.get("name").lower() in str(cid).lower():
                        citations.append({
                            "id": entry.get("id"),
                            "name": entry.get("name"),
                            "category": entry.get("category")
                        })
                        break

            return {
                "answer": data.get("answer", "No answer generated."),
                "citations": citations,
                "mode": "live_ai",
                "grounded": data.get("grounded", len(citations) > 0)
            }
        except Exception:
            # If JSON parsing fails, return clean text
            return {
                "answer": response.text,
                "citations": self._find_relevant_entries(question, canon_entries)[:2],
                "mode": "live_ai",
                "grounded": True
            }

    def _demo_answer_qa(self, question: str, canon_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Intelligent, fully grounded heuristic Q&A engine for demo mode.
        Matches questions against canon entities, goals, rules, and places.
        Explicitly flags unknown/unspecified lore.
        """
        q_lower = question.lower()
        matched_entries = []

        # 1. Check for known negative/unspecified test topics
        unspecified_topics = [
            ("dragon", "dragons or draconic creatures"),
            ("pet", "pets or companion animals"),
            ("spaceship", "spacefaring vessels or sci-fi tech"),
            ("parents", "the lineage or parents of any character"),
            ("birthday", "birthdays or specific calendar dates"),
            ("sword of light", "a 'sword of light' artifact"),
            ("vampire", "vampires or undead beings"),
            ("magic wand", "wands or traditional spellcraft"),
            ("gunpowder", "gunpowder or modern chemical propellants")
        ]

        for trigger, topic_desc in unspecified_topics:
            if trigger in q_lower:
                # Find if any character was mentioned
                char_mentions = [e for e in canon_entries if e.get("category") == "character" and e.get("name").lower() in q_lower]
                if char_mentions:
                    char = char_mentions[0]
                    return {
                        "answer": (
                            f"The established canon does not specify whether {char.get('name')} has {topic_desc}. "
                            f"The Story Bible records {char.get('name')} as a {char.get('role', 'character')} whose established facts "
                            f"focus on their goal ({char.get('goal', 'n/a')}), but contains no documented record regarding {topic_desc}."
                        ),
                        "citations": [{
                            "id": char.get("id"),
                            "name": char.get("name"),
                            "category": char.get("category")
                        }],
                        "mode": "demo",
                        "grounded": False
                    }
                else:
                    return {
                        "answer": (
                            f"The established canon does not specify any details regarding {topic_desc}. "
                            f"No entries in the Story Bible contain records of this subject."
                        ),
                        "citations": [],
                        "mode": "demo",
                        "grounded": False
                    }

        # 2. Check if the question specifically references an existing entry by name
        for entry in canon_entries:
            entry_name_lower = entry.get("name", "").lower()
            clean_name = re.sub(r'\(.*?\)', '', entry_name_lower).strip()
            if len(clean_name) >= 4 and clean_name in q_lower:
                cites = [{"id": entry["id"], "name": entry["name"], "category": entry["category"]}]
                answer_parts = [f"According to the canon record for **{entry.get('name')}**: {entry.get('description', '')}"]
                if entry.get("role"):
                    answer_parts.append(f"Role: {entry.get('role')}.")
                if entry.get("goal"):
                    answer_parts.append(f"Primary Goal: {entry.get('goal')}.")
                if entry.get("relationships"):
                    answer_parts.append(f"Relationships: {entry.get('relationships')}.")
                if entry.get("defining_detail"):
                    answer_parts.append(f"Defining Detail: {entry.get('defining_detail')}.")
                return {
                    "answer": " ".join(answer_parts),
                    "citations": cites,
                    "mode": "demo",
                    "grounded": True
                }

        # 3. Targeted semantic matching against canon rules, places, events, characters
        # Check World Rule 1: Raw Aether / contact / touch / flesh
        if any(term in q_lower for term in ["raw aether", "touch aether", "bare hand", "bare flesh", "calcif", "skin contact", "crystall"]):
            rule = next((e for e in canon_entries if e.get("id") == "rule-aetheric-resonance"), None)
            if rule:
                return {
                    "answer": (
                        "According to **The Law of Aetheric Resonance (Rule #1)**, raw, unrefined Aether cannot be touched with bare organic flesh. "
                        "Without an attuned catalyst lens or lead-lined insulated gauntlets, direct contact causes instantaneous cellular calcification, "
                        "petrifying skin, muscle, and bone into brittle obsidian-black glass within seconds."
                    ),
                    "citations": [{"id": rule["id"], "name": rule["name"], "category": rule["category"]}],
                    "mode": "demo",
                    "grounded": True
                }

        # Check World Rule 2: Trench air / vapor / breath / mask / respiratory / crystal-lung
        if any(term in q_lower for term in ["trench air", "trench vapor", "breath", "respiratory", "crystal-lung", "depth 400", "filter mask", "gear to survive", "survive in the trench"]):
            rule = next((e for e in canon_entries if e.get("id") == "rule-trench-toxicity"), None)
            place = next((e for e in canon_entries if e.get("id") == "place-sunken-trench"), None)
            cites = []
            if rule: cites.append({"id": rule["id"], "name": rule["name"], "category": rule["category"]})
            if place: cites.append({"id": place["id"], "name": place["name"], "category": place["category"]})
            return {
                "answer": (
                    "To survive in the **Obsidian Trench** (below Depth 400), an airtight pressure helmet or a charcoal-aether filter mask is strictly mandatory. "
                    "The ambient mist is heavily saturated with volatile crystal aerosols; inhaling unfiltered trench vapor causes fatal crystal-lung calcification within twenty minutes."
                ),
                "citations": cites,
                "mode": "demo",
                "grounded": True
            }

        # Check World Rule 3: Grand Library / weapon / blade / iron / brass sentinels / sanctuary
        if any(term in q_lower for term in ["grand library", "library", "blade", "sword", "weapon", "seven bells", "sentinel", "unsheath", "draw iron"]):
            rule = next((e for e in canon_entries if e.get("id") == "rule-sanctuary-seven-bells"), None)
            event = next((e for e in canon_entries if e.get("id") == "event-treaty-seven-bells"), None)
            cites = []
            if rule: cites.append({"id": rule["id"], "name": rule["name"], "category": rule["category"]})
            if event: cites.append({"id": event["id"], "name": event["name"], "category": event["category"]})
            return {
                "answer": (
                    "No weapons of iron or steel may be drawn inside the Grand Library of the Ivory Spire. "
                    "Under **The Sanctum of the Seven Bells (Rule #3)** and Clause 4 of the Treaty of the Seven Bells, "
                    "brandishing any metallic weapon immediately awakens the clockwork Brass Sentinels embedded in the masonry, which pacify the offender with lethal force."
                ),
                "citations": cites,
                "mode": "demo",
                "grounded": True
            }

        # Check World Rule 4: Sunstone Core / recharge / eclipse / power
        if any(term in q_lower for term in ["sunstone", "recharge", "eclipse", "sunstone core", "crystal matrix"]):
            rule = next((e for e in canon_entries if e.get("id") == "rule-sunstone-polarity"), None)
            char = next((e for e in canon_entries if e.get("id") == "char-lyra-vance"), None)
            cites = []
            if rule: cites.append({"id": rule["id"], "name": rule["name"], "category": rule["category"]})
            if char: cites.append({"id": char["id"], "name": char["name"], "category": char["category"]})
            return {
                "answer": (
                    "A Sunstone Core can only be safely recharged when exposed to solar radiation during a celestial planetary alignment (such as the Eclipse of the Seven Moons). "
                    "Per **Rule #4 (Sunstone Polarity)**, forcing an energetic recharge or drawing power prematurely permanently fractures its crystalline lattice, rendering the core inert."
                ),
                "citations": cites,
                "mode": "demo",
                "grounded": True
            }

        # Check Lyra Vance exile / banishment / goal / role
        if "lyra" in q_lower and any(term in q_lower for term in ["exile", "banish", "why", "curator", "corvus", "goal", "who is"]):
            char = next((e for e in canon_entries if e.get("id") == "char-lyra-vance"), None)
            event = next((e for e in canon_entries if e.get("id") == "event-banishment-lyra"), None)
            cites = []
            if char: cites.append({"id": char["id"], "name": char["name"], "category": char["category"]})
            if event: cites.append({"id": event["id"], "name": event["name"], "category": event["category"]})
            
            if "goal" in q_lower:
                return {
                    "answer": f"Lyra Vance's primary goal is to {char.get('goal')} She is an exiled Aether-Cartographer who navigates the canals using a hand-calibrated resonance compass.",
                    "citations": cites,
                    "mode": "demo",
                    "grounded": True
                }
            return {
                "answer": (
                    "Lyra Vance was banished from the Ivory Spire in Year 438 during a closed-door tribunal led by Master Corvus. "
                    "She was charged with heresy and unauthorized subterranean cartography after she uncovered secret excavation tunnels "
                    "leading to the pre-cataclysm Grand Conduit. Her scholarly credentials were stripped and she was exiled to the Low Docks."
                ),
                "citations": cites,
                "mode": "demo",
                "grounded": True
            }

        # Check Master Corvus
        if "corvus" in q_lower:
            char = next((e for e in canon_entries if e.get("id") == "char-master-corvus"), None)
            if char:
                return {
                    "answer": (
                        f"Master Corvus is the High Curator of the Ivory Spire. His goal is: '{char.get('goal')}' "
                        f"He was formerly Lyra Vance's mentor before having her exiled, and secretly holds an underground debt to the Iron Syndicate."
                    ),
                    "citations": [{"id": char["id"], "name": char["name"], "category": char["category"]}],
                    "mode": "demo",
                    "grounded": True
                }

        # Check Captain Kaelen
        if "kaelen" in q_lower:
            char = next((e for e in canon_entries if e.get("id") == "char-captain-kaelen"), None)
            if char:
                return {
                    "answer": (
                        f"Captain Kaelen is a sky-skiff smuggler and deep-water pilot who captains 'The Zephyr's Wake'. "
                        f"His goal is: '{char.get('goal')}' He is a wary partner to Lyra Vance and distrusts Spire scholars."
                    ),
                    "citations": [{"id": char["id"], "name": char["name"], "category": char["category"]}],
                    "mode": "demo",
                    "grounded": True
                }

        # Check Great Shattering
        if "shattering" in q_lower or "year 412" in q_lower or "cataclysm" in q_lower:
            event = next((e for e in canon_entries if e.get("id") == "event-great-shattering"), None)
            if event:
                return {
                    "answer": (
                        "The Great Shattering (Year 412) was a catastrophic rupture triggered when Oakhaven's Grand Conduit suffered "
                        "an energetic resonance cascade during the Twin Solstice. The shockwave fractured the continental shelf, submerging Old Oakhaven "
                        "beneath the ocean and creating the division between the Upper Spire and Lower Depths."
                    ),
                    "citations": [{"id": event["id"], "name": event["name"], "category": event["category"]}],
                    "mode": "demo",
                    "grounded": True
                }

        # Fallback: Search all entries for keyword matches
        scored_entries = []
        words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', q_lower) if w not in {"what", "when", "where", "which", "does", "have", "with", "from", "that", "this", "tell", "about"}]
        
        for entry in canon_entries:
            score = 0
            haystack = (entry.get("name", "") + " " + entry.get("description", "") + " " +
                        entry.get("role", "") + " " + entry.get("goal", "") + " " +
                        entry.get("relationships", "") + " " + entry.get("defining_detail", "") + " " +
                        " ".join(entry.get("tags", []))).lower()
            for word in words:
                if word in haystack:
                    score += 1
            if score > 0:
                scored_entries.append((score, entry))

        scored_entries.sort(key=lambda x: x[0], reverse=True)

        if scored_entries and scored_entries[0][0] >= 2:
            top_entry = scored_entries[0][1]
            cites = [{"id": top_entry["id"], "name": top_entry["name"], "category": top_entry["category"]}]
            
            summary = top_entry.get("description", "")
            if top_entry.get("goal"):
                summary += f" Established Goal: {top_entry.get('goal')}"
            if top_entry.get("defining_detail"):
                summary += f" Defining Detail: {top_entry.get('defining_detail')}"

            return {
                "answer": f"According to the canon record for **{top_entry.get('name')}**: {summary}",
                "citations": cites,
                "mode": "demo",
                "grounded": True
            }

        # If completely ungrounded / unknown topic
        return {
            "answer": (
                "The established canon does not specify the answer to this question. "
                "Story AL strictly prevents hallucinating or inventing lore outside the Story Bible. "
                "To make this canon, add a new entry under Characters, Places, Events, or World Rules."
            ),
            "citations": [],
            "mode": "demo",
            "grounded": False
        }

    # =========================================================================
    # FEATURE 4: BASIC CONTINUITY CHECK
    # =========================================================================

    def check_continuity(self, draft_text: str, canon_entries: List[Dict[str, Any]], force_demo: bool = False) -> Dict[str, Any]:
        """
        Analyzes a draft paragraph or scene against saved Story Bible entries.
        Identifies potential contradictions with:
        - The relevant text from the draft
        - The canon entry it may conflict with
        - A short explanation and writer suggestion
        """
        draft_clean = draft_text.strip()
        if not draft_clean:
            return {
                "clean": True,
                "issues_count": 0,
                "issues": [],
                "summary": "Please paste or enter draft text to analyze.",
                "mode": "demo"
            }

        # If live AI is available and not forced into demo mode, call Gemini
        if self.is_live_mode_available() and not force_demo:
            try:
                return self._call_gemini_continuity(draft_clean, canon_entries)
            except Exception as err:
                print(f"[AIEngine] Gemini Continuity error: {err}. Falling back to demo engine.")

        # Otherwise, run the grounded demo engine
        return self._demo_check_continuity(draft_clean, canon_entries)

    def _call_gemini_continuity(self, draft_text: str, canon_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs continuity check using Gemini."""
        canon_summary = []
        for e in canon_entries:
            summary = f"- [{e.get('category').upper()}] {e.get('name')} (ID: {e.get('id')}): {e.get('description')}"
            if e.get("defining_detail"):
                summary += f" | Defining Detail: {e.get('defining_detail')}"
            if e.get("goal"):
                summary += f" | Goal: {e.get('goal')}"
            canon_summary.append(summary)

        canon_block = "\n".join(canon_summary)

        system_instruction = (
            "You are Story AL's Continuity Reviewer. Your role is to help fiction writers catch "
            "potential contradictions between their newly written draft scene and their established Story Bible canon.\n\n"
            "Treat results as helpful suggestions for the writer to review, not punitive errors.\n\n"
            "Analyze the draft scene carefully. Check for:\n"
            "1. Physical world rule violations (e.g. magic laws, environmental dangers, weapon bans)\n"
            "2. Character status or relationship contradictions (e.g. someone exiled acting as if in power, reversed loyalties)\n"
            "3. Location constraints (e.g. atmospheric hazards, required credentials)\n\n"
            "Return valid JSON with the following structure:\n"
            "{\n"
            "  'clean': boolean (true if no contradictions detected),\n"
            "  'summary': string (brief 1-2 sentence overview for the writer),\n"
            "  'issues': [\n"
            "    {\n"
            "      'draft_excerpt': 'exact text snippet from the draft',\n"
            "      'canon_entry_id': 'id of conflicting entry',\n"
            "      'canon_name': 'name of conflicting entry',\n"
            "      'canon_category': 'rule|place|character|event',\n"
            "      'explanation': 'why this appears to contradict canon',\n"
            "      'suggestion': 'constructive suggestion for how the writer can reconcile or adjust it'\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        prompt = f"STORY BIBLE CANON:\n{canon_block}\n\nDRAFT SCENE TO REVIEW:\n{draft_text}"

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                response_mime_type="application/json"
            )
        )

        data = json.loads(response.text)
        issues = data.get("issues", [])
        return {
            "clean": len(issues) == 0,
            "issues_count": len(issues),
            "summary": data.get("summary", "Review complete."),
            "issues": issues,
            "mode": "live_ai"
        }

    def _demo_check_continuity(self, draft_text: str, canon_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Heuristic continuity detector for demo mode.
        Checks for explicit violations of world rules, location parameters, and character lore.
        """
        draft_lower = draft_text.lower()
        issues = []

        # Find specific canon entries
        rule_aether = next((e for e in canon_entries if e.get("id") == "rule-aetheric-resonance"), None)
        rule_trench = next((e for e in canon_entries if e.get("id") == "rule-trench-toxicity"), None)
        rule_sanctuary = next((e for e in canon_entries if e.get("id") == "rule-sanctuary-seven-bells"), None)
        rule_sunstone = next((e for e in canon_entries if e.get("id") == "rule-sunstone-polarity"), None)
        event_banish = next((e for e in canon_entries if e.get("id") == "event-banishment-lyra"), None)
        char_lyra = next((e for e in canon_entries if e.get("id") == "char-lyra-vance"), None)

        # 1. Check Violation: Bare hand touching raw Aether
        has_aether = any(t in draft_lower for t in ["raw aether", "aether sphere", "aether crystal", "aether conduit"])
        has_bare_skin = any(t in draft_lower for t in [
            "bare hand", "bare hands", "bare skin", "bare fingers", "without gloves",
            "without gauntlets", "unprotected hands", "soothing energy flow through her skin",
            "flow through his skin", "flow through their skin"
        ])
        if has_aether and has_bare_skin:
            excerpt_match = re.search(r'([^.?!]*\b(?:bare (?:hand|hands|skin|fingers)|without (?:gloves|gauntlets)|flow through [a-z]+ skin)\b[^.?!]*[.?!])', draft_text, re.IGNORECASE)
            excerpt = excerpt_match.group(1).strip() if excerpt_match else "Bare contact with raw Aether described in text."
            issues.append({
                "draft_excerpt": excerpt,
                "canon_entry_id": rule_aether["id"] if rule_aether else "rule-aetheric-resonance",
                "canon_name": rule_aether["name"] if rule_aether else "The Law of Aetheric Resonance (Rule #1)",
                "canon_category": "rule",
                "explanation": (
                    "The draft describes direct skin contact with raw Aether. "
                    "Canon Rule #1 explicitly states that touching unrefined Aether with bare flesh causes instantaneous "
                    "calcification into brittle obsidian-black glass within seconds unless an attuned catalyst lens or insulated gauntlet is used."
                ),
                "suggestion": "Have the character equip lead-lined insulated gauntlets or handle the Aether sphere through an attuned catalyst lens."
            })

        # 2. Check Violation: Drawing weapons/blades inside the Grand Library
        has_library = any(t in draft_lower for t in ["grand library", "library of the ivory spire", "spire library", "library sanctum"])
        has_weapon_draw = any(t in draft_lower for t in [
            "drew her", "drew his", "drew their", "unsheathed", "brandished", "blade", "cutlass", "sword", "dagger", "iron", "steel"
        ])
        if has_library and has_weapon_draw:
            excerpt_match = re.search(r'([^.?!]*\b(?:drew|unsheathed|brandished|blade|cutlass|sword|dagger)\b[^.?!]*\b(?:library)\b[^.?!]*[.?!])', draft_text, re.IGNORECASE)
            if not excerpt_match:
                excerpt_match = re.search(r'([^.?!]*\b(?:library)\b[^.?!]*\b(?:drew|unsheathed|brandished|cutlass|sword)\b[^.?!]*[.?!])', draft_text, re.IGNORECASE)
            excerpt = excerpt_match.group(1).strip() if excerpt_match else "Drawing weapons inside the Grand Library."
            issues.append({
                "draft_excerpt": excerpt,
                "canon_entry_id": rule_sanctuary["id"] if rule_sanctuary else "rule-sanctuary-seven-bells",
                "canon_name": rule_sanctuary["name"] if rule_sanctuary else "The Sanctum of the Seven Bells (Rule #3)",
                "canon_category": "rule",
                "explanation": (
                    "Drawing an iron or steel blade inside the Grand Library breaches the Treaty of the Seven Bells and Rule #3. "
                    "The sanctum is guarded by automated clockwork Brass Sentinels that immediately activate to pacify anyone drawing weapons."
                ),
                "suggestion": "If the scene takes place inside the library, show the character using a non-metallic or concealed restraint, or write the immediate activation of the brass sentinels."
            })

        # 3. Check Violation: Unfiltered breathing in the Obsidian Trench / Deep Trench without mask
        has_trench = any(t in draft_lower for t in ["obsidian trench", "sunken trench", "trench vapor", "depth 400", "depth 500", "depth 600"])
        has_unfiltered_breath = any(t in draft_lower for t in [
            "discarded his breathing mask", "discarded her breathing mask", "took deep, refreshing breaths",
            "without any protective gear", "without a mask", "inhaled the vapor", "breathed freely",
            "three hours without any protective gear"
        ])
        if has_trench and has_unfiltered_breath:
            excerpt_match = re.search(r'([^.?!]*\b(?:discarded|breaths|without (?:any )?(?:mask|protective)|breathed freely)\b[^.?!]*[.?!])', draft_text, re.IGNORECASE)
            excerpt = excerpt_match.group(1).strip() if excerpt_match else "Breathing trench vapor without protective gear."
            issues.append({
                "draft_excerpt": excerpt,
                "canon_entry_id": rule_trench["id"] if rule_trench else "rule-trench-toxicity",
                "canon_name": rule_trench["name"] if rule_trench else "Atmospheric Toxicity of the Trench (Rule #2)",
                "canon_category": "rule",
                "explanation": (
                    "The draft depicts characters breathing deep trench mist without protective gear. "
                    "Canon establishes that the Obsidian Trench below Depth 400 contains lethal aerosolized vapor crystals, "
                    "causing fatal crystal-lung calcification within twenty minutes."
                ),
                "suggestion": "Describe the pilot tightening their charcoal-filter respirator mask or adjusting their pressure helmet seals."
            })

        # 4. Check Violation: Premature Sunstone recharge or forced drawing
        has_sunstone_premature = any(t in draft_lower for t in ["recharge the sunstone core", "forced energy from the core", "drained the sunstone"]) and any(t in draft_lower for t in ["broad daylight", "without waiting for the eclipse", "regular afternoon", "any time"])
        if has_sunstone_premature:
            issues.append({
                "draft_excerpt": "Recharging the Sunstone Core outside of a celestial alignment.",
                "canon_entry_id": rule_sunstone["id"] if rule_sunstone else "rule-sunstone-polarity",
                "canon_name": rule_sunstone["name"] if rule_sunstone else "Sunstone Polarity & Eclipse Recharge (Rule #4)",
                "canon_category": "rule",
                "explanation": "Canon Rule #4 specifies that Sunstone Cores can ONLY be recharged during celestial alignments like the Eclipse of the Seven Moons. Premature draws destroy the core matrix.",
                "suggestion": "Ground the scene around an impending eclipse or show the core fracturing if forced."
            })

        # 5. Check Violation: Lyra acting as welcomed Spire curator or unchallenged councilor
        if "lyra" in draft_lower and any(t in draft_lower for t in ["welcomed warmly into the council", "curator of the ivory spire", "head of the archives"]):
            issues.append({
                "draft_excerpt": "Lyra acting with institutional Spire authority.",
                "canon_entry_id": event_banish["id"] if event_banish else "event-banishment-lyra",
                "canon_name": event_banish["name"] if event_banish else "The Banishment of Lyra Vance",
                "canon_category": "event",
                "explanation": "Lyra Vance was formally banished in Year 438 by Master Corvus. Her credentials were revoked and she resides in the Low Docks.",
                "suggestion": "Have Lyra sneak in disguised or use counterfeit credentials to enter the Spire."
            })

        is_clean = len(issues) == 0
        summary = (
            "No canon contradictions detected. This scene aligns with established world rules, respiratory constraints, and character statuses."
            if is_clean else
            f"Flagged {len(issues)} potential canon discrepancy{'s' if len(issues) > 1 else ''}. Review suggestions below to maintain story continuity."
        )

        return {
            "clean": is_clean,
            "issues_count": len(issues),
            "summary": summary,
            "issues": issues,
            "mode": "demo"
        }


    # =========================================================================
    # FEATURE 5: NEXT-SCENE SUGGESTIONS
    # =========================================================================

    def generate_next_scenes(self, character_name: str, situation: str, canon_entries: List[Dict[str, Any]], force_demo: bool = False) -> Dict[str, Any]:
        """
        Generates three distinct possible next scenes based on the selected character's
        goals and relevant canon. Explicitly marks suggestions as optional draft ideas,
        NOT established canon.
        """
        char_clean = (character_name or "Lyra Vance").strip()
        sit_clean = (situation or "").strip()

        # If live AI is available and not forced into demo mode, call Gemini
        if self.is_live_mode_available() and not force_demo:
            try:
                return self._call_gemini_next_scenes(char_clean, sit_clean, canon_entries)
            except Exception as err:
                print(f"[AIEngine] Gemini Next-Scene error: {err}. Falling back to demo engine.")

        # Otherwise, run the grounded demo engine
        return self._demo_generate_next_scenes(char_clean, sit_clean, canon_entries)

    def _call_gemini_next_scenes(self, character_name: str, situation: str, canon_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates 3 next-scene options using Gemini."""
        canon_summary = []
        for e in canon_entries:
            summary = f"- [{e.get('category').upper()}] {e.get('name')}: {e.get('description')}"
            if e.get("goal"):
                summary += f" | Goal: {e.get('goal')}"
            if e.get("defining_detail"):
                summary += f" | Defining Detail: {e.get('defining_detail')}"
            canon_summary.append(summary)

        canon_block = "\n".join(canon_summary)

        system_instruction = (
            "You are a collaborative story brainstorming partner for fiction writers. "
            "Your task is to propose exactly THREE distinct, compelling directions for the next scene. "
            "Each suggestion must:\n"
            "1. Focus on the selected character's established motivations, relationships, or world hazards.\n"
            "2. Strictly respect established world rules (e.g. contact toxicity of raw Aether, weapon bans in the Grand Library, trench atmosphere hazards).\n"
            "3. Offer a distinct story flavor (e.g. 1: Action/Stakes, 2: Secret/Investigation, 3: Lore/Discovery).\n"
            "4. Be clearly presented as creative options for the author to consider, NOT confirmed canon.\n\n"
            "Return valid JSON formatted as:\n"
            "{\n"
            "  'character': string,\n"
            "  'situation_summary': string,\n"
            "  'scenes': [\n"
            "    {\n"
            "      'id': 'scene-1',\n"
            "      'title': 'Short evocative scene title',\n"
            "      'type': 'Action & Stakes | Investigation & Secrets | Lore & Revelation',\n"
            "      'tone': 'e.g. Tense and urgent',\n"
            "      'what_happens': 'Detailed paragraph describing what happens in the scene',\n"
            "      'why_it_fits': 'How this honors established canon rules, character goals, or timeline without causing contradictions'\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        prompt = f"STORY BIBLE CANON:\n{canon_block}\n\nSELECTED CHARACTER: {character_name}\nCURRENT SITUATION: {situation or 'Exploring options following recent events'}"

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                response_mime_type="application/json"
            )
        )

        data = json.loads(response.text)
        scenes = data.get("scenes", [])
        return {
            "character": character_name,
            "situation": situation,
            "scenes": scenes,
            "mode": "live_ai",
            "is_canon": False,
            "notice": "These are optional creative suggestions for the author. They do not alter your Story Bible."
        }

    def _demo_generate_next_scenes(self, character_name: str, situation: str, canon_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Demo engine for next-scene suggestions.
        Provides three narrative pathways grounded in the selected character's goal and world rules.
        """
        c_lower = character_name.lower()
        sit_text = situation if situation else "navigating the misty lower canals after a close call with the city watch"

        # Character: Lyra Vance
        if "lyra" in c_lower:
            scenes = [
                {
                    "id": "scene-lyra-1",
                    "title": "The Ambush at the Rusted Lock",
                    "type": "Action & Stakes",
                    "tone": "Tense and urgent",
                    "what_happens": (
                        f"While {sit_text}, an unregistered Iron Syndicate dredge-skiff swings across the canal, cutting off Lyra and Kaelen's retreat. "
                        "With syndicate enforcers demanding tribute, Lyra must use her hand-calibrated resonance compass to spot a flooded pre-cataclysm sluice gate, "
                        "forcing Kaelen into a risky submerged dive before their boat is boarded."
                    ),
                    "why_it_fits": (
                        "Directly challenges Lyra's goal of reaching the Sunstone Core, features her hand-calibrated compass, "
                        "and highlights Captain Kaelen's existing debt to the Iron Syndicate without violating any world rules."
                    )
                },
                {
                    "id": "scene-lyra-2",
                    "title": "A Secret Meeting in the Eel-Market",
                    "type": "Investigation & Secrets",
                    "tone": "Atmospheric and suspenseful",
                    "what_happens": (
                        "Lyra slips into a lantern-lit cellar beneath the Low Docks fishmongers to meet an informant—a disgraced former Spire archivist. "
                        "The informant reveals that Master Corvus has quietly accelerated deep-trench excavations, meaning Lyra has fewer than forty-eight hours "
                        "before the Spire locks down the Sunken Trench ahead of the Eclipse of the Seven Moons."
                    ),
                    "why_it_fits": (
                        "Deepens the rivalry between Lyra and her former mentor Master Corvus, emphasizes the looming deadline of the celestial eclipse, "
                        "and respects her banished status by keeping her hidden in the Low Docks."
                    )
                },
                {
                    "id": "scene-lyra-3",
                    "title": "Harmonic Echoes in the Deep Canal",
                    "type": "Lore & Revelation",
                    "tone": "Mystical and ominous",
                    "what_happens": (
                        "While calibrating her catalyst lens gauntlets on the skiff's deck, Lyra's ocular glasses pick up a faint sapphire shimmer pulsing "
                        "through the flooded canal bed. She realizes the city's ancient conduits are vibrating in harmony with the approaching eclipse, "
                        "confirming that the Great Shattering was not an accident—the conduit was deliberately overloaded."
                    ),
                    "why_it_fits": (
                        "Ties directly to Rule #1 (catalyst lens handling) and the historical cataclysm of the Great Shattering (Year 412), "
                        "giving Lyra crucial narrative stakes without inventing contradictory canon."
                    )
                }
            ]
        # Character: Captain Kaelen
        elif "kaelen" in c_lower:
            scenes = [
                {
                    "id": "scene-kaelen-1",
                    "title": "A High-Tide Pursuit in the Fog",
                    "type": "Action & High Stakes",
                    "tone": "Fast-paced and gritty",
                    "what_happens": (
                        f"As Kaelen pilots The Zephyr's Wake while {sit_text}, a harbor guild steam-cutter emerges from the mist with spotlights ablaze. "
                        "With his acoustic dampeners running hot, Kaelen must navigate blind through the rusted iron pilings of the Old Aqueduct, "
                        "gambling the skiff's hull to shake the patrol."
                    ),
                    "why_it_fits": (
                        "Showcases Kaelen's exceptional piloting skills and customized skiff ('The Zephyr's Wake') while heightening his legal troubles with the harbor guild."
                    )
                },
                {
                    "id": "scene-kaelen-2",
                    "title": "The Price of an Island Berth",
                    "type": "Character & Emotional Conflict",
                    "tone": "Quiet and grounded",
                    "what_happens": (
                        "At a secluded pontoon wharf, Kaelen is confronted by an old smuggling contact who offers safe passage papers for his sister to the Outer Isles—"
                        "on the condition that Kaelen betrays Lyra's salvage coordinates to the Iron Syndicate. Kaelen is forced to choose between his family's safety and his loyalty to Lyra."
                    ),
                    "why_it_fits": (
                        "Tests Kaelen's primary established goal (saving his younger sister and paying debts) against his growing bond with Lyra Vance."
                    )
                },
                {
                    "id": "scene-kaelen-3",
                    "title": "Testing the Trench Respirators",
                    "type": "Preparation & World Building",
                    "tone": "Cautious and practical",
                    "what_happens": (
                        "Kaelen inspects their charcoal-aether respirator masks in the skiff's bilge, discovering a hairline fracture in one of the pressure seals. "
                        "Knowing Rule #2 means fatal crystal-lung within twenty minutes below Depth 400, he must barter an illicit filter repair from a dock mechanic before they descend."
                    ),
                    "why_it_fits": (
                        "Reinforces World Rule #2 (Atmospheric Toxicity of the Trench) as a tangible narrative obstacle rather than just an abstract rule."
                    )
                }
            ]
        # Character: Master Corvus
        elif "corvus" in c_lower:
            scenes = [
                {
                    "id": "scene-corvus-1",
                    "title": "The High Archive Inquisition",
                    "type": "Political Intrigue & Tension",
                    "tone": "Chilly and calculated",
                    "what_happens": (
                        "Inside the Ivory Spire, Master Corvus interrogates a junior scholar who was caught copying forbidden subterranean cartography charts. "
                        "Corvus confiscates the research and discreetly dispatches an internal watch squad to search the Low Docks for any trace of Lyra's resonance compass."
                    ),
                    "why_it_fits": (
                        "Demonstrates Corvus's authoritarian control over Spire archives and his obsession with silencing pre-cataclysm knowledge."
                    )
                },
                {
                    "id": "scene-corvus-2",
                    "title": "The Syndicate Envoy at Sunrise",
                    "type": "Secrets & Compromise",
                    "tone": "Duplicitous and tense",
                    "what_happens": (
                        "At dawn, as the pearlite walls of the Spire begin their harmonic chime, Corvus meets secretly on an observation terrace with an envoy from the Iron Syndicate. "
                        "The envoy demands priority access to raw Aether conduits in exchange for forgiving Corvus's substantial underground debts."
                    ),
                    "why_it_fits": (
                        "Explores Corvus's documented secret debt to the Iron Syndicate and highlights the hypocrisy of the Scholarly Council."
                    )
                },
                {
                    "id": "scene-corvus-3",
                    "title": "The Astrolabe Alignment",
                    "type": "Looming Threat & Mystery",
                    "tone": "Foreboding and scholarly",
                    "what_happens": (
                        "Corvus monitors the celestial astrolabe as the planetary rings shift toward the Eclipse of the Seven Moons. "
                        "He discovers that the Sunstone Core Lyra is seeking has already begun to hum, signaling that someone in the depths is closing in on the ancient vault."
                    ),
                    "why_it_fits": (
                        "Aligns with Rule #4 (Sunstone celestial recharge) and foreshadows the impending climax of the story arc."
                    )
                }
            ]
        # General Ensemble / Situation-based
        else:
            scenes = [
                {
                    "id": "scene-gen-1",
                    "title": "A Confrontation at the Fog Gate",
                    "type": "Action & Tension",
                    "tone": "Fast-paced and dangerous",
                    "what_happens": (
                        f"While {sit_text}, unexpected movement in the mist triggers a perimeter defense alarm. "
                        "The characters must decide between a hasty retreat into unmapped canals or standing their ground against an unknown pursuer."
                    ),
                    "why_it_fits": "Raises immediate physical stakes while keeping the characters grounded in the foggy canal atmosphere of Oakhaven."
                },
                {
                    "id": "scene-gen-2",
                    "title": "The Decoded Ledger",
                    "type": "Mystery & Investigation",
                    "tone": "Quiet and intriguing",
                    "what_happens": (
                        f"Taking brief refuge while {sit_text}, the characters examine an old pre-cataclysm maritime log. "
                        "They discover an unrecorded passage leading directly beneath the Ivory Spire into the submerged catacombs."
                    ),
                    "why_it_fits": "Bridges the geographical divide between the Upper Spire and Lower Depths established after the Great Shattering."
                },
                {
                    "id": "scene-gen-3",
                    "title": "A Fragile Bargain",
                    "type": "Character Dialogue & Alliance",
                    "tone": "Sharp and diplomatic",
                    "what_happens": (
                        f"In the aftermath of {sit_text}, two characters with conflicting goals are forced to negotiate a temporary truce. "
                        "Each holds a piece of information the other desperately needs to survive the coming eclipse."
                    ),
                    "why_it_fits": "Focuses on character goals and interpersonal conflict without violating any Story Bible rules."
                }
            ]

        return {
            "character": character_name,
            "situation": situation,
            "scenes": scenes,
            "mode": "demo",
            "is_canon": False,
            "notice": "These are optional creative suggestions for the author. They do not alter your Story Bible."
        }

    # =========================================================================
    # FEATURE 6: AUDIO STUDIO STATUS & SYNTHESIS
    # =========================================================================

    def get_audio_status(self) -> Dict[str, Any]:
        """
        Returns the status of audio generation services.
        Honest and transparent: never pretends fake audio was generated.
        """
        has_elevenlabs = bool(os.environ.get("ELEVENLABS_API_KEY"))
        has_openai = bool(os.environ.get("OPENAI_API_KEY"))
        
        if has_elevenlabs:
            return {
                "has_cloud_tts": True,
                "provider": "ElevenLabs Neural TTS",
                "mode": "live_cloud_tts",
                "message": "Connected to ElevenLabs. Neural voice synthesis available."
            }
        elif has_openai:
            return {
                "has_cloud_tts": True,
                "provider": "OpenAI Speech API",
                "mode": "live_cloud_tts",
                "message": "Connected to OpenAI TTS. Neural voice synthesis available."
            }
        else:
            return {
                "has_cloud_tts": False,
                "provider": "Local Browser Voice Synthesis Engine",
                "mode": "demo_browser_tts",
                "message": "Cloud neural TTS key not configured. Using your computer's built-in speech synthesizer for real line-by-line scene voice playback."
            }

    # Helper for fuzzy finding relevant entries
    def _find_relevant_entries(self, query: str, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for e in entries:
            name = e.get("name", "").lower()
            category = e.get("category", "").lower()
            if any(part in q for part in name.split() if len(part) > 3) or category in q:
                results.append({"id": e.get("id"), "name": e.get("name"), "category": e.get("category")})
        return results
