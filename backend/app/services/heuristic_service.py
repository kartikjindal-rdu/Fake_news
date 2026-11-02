import re
from typing import Tuple, Dict

CLICKBAIT_PATTERNS = [
    "you won't believe", "you wont believe", "will blow your mind",
    "this one trick", "what happens next", "doctors hate this",
    "shocking truth", "secret cure", "banned from tv", "before it is deleted",
    "miracle remedy", "illuminati", "urgent share", "100% guaranteed"
]

SENSATIONAL_WORDS = [
    "shocking", "miracle", "unbelievable", "mind-blowing", "revolutionary",
    "cure-all", "catastrophic", "forbidden", "exposed", "terrifying",
    "doomsday", "apocalyptic", "magic", "conspiracy", "corrupt", "traitor"
]

FEAR_WORDS = ["deadly", "fatal", "toxic", "destroy", "panic", "disaster", "nightmare", "danger", "threat", "apocalypse"]
OUTRAGE_WORDS = ["evil", "scandal", "disgrace", "shameful", "treason", "liar", "criminals", "theft", "tyranny", "fraud"]
URGENCY_WORDS = ["urgent", "immediately", "hurry", "warning", "alert", "breaking", "forward this", "act now"]

def analyze_heuristics(headline: str, body: str) -> Tuple[float, float, float, str, Dict[str, str]]:
    combined = f"{headline or ''} {body or ''}".strip()
    lower = combined.lower()
    triggers = {}

    # 1. Clickbait
    clickbait_score = 0.0
    for pattern in CLICKBAIT_PATTERNS:
        if pattern in lower:
            clickbait_score += 25.0
            triggers[pattern.upper()] = "Clickbait / Viral Trigger: Designed to induce reflexive clicks rather than factual reading."

    caps_letters = len(re.findall(r'[A-Z]', combined))
    total_letters = len(re.findall(r'[a-zA-Z]', combined))
    if total_letters > 20 and (caps_letters / total_letters) > 0.35:
        clickbait_score += 30.0
        triggers["EXCESSIVE UPPERCASE"] = "Visual Emphasis Marker: Over 35% uppercase text used to manufacture excitement."

    punct_clusters = len(re.findall(r'[!?]{2,}', combined))
    if punct_clusters > 0:
        clickbait_score += min(punct_clusters * 15.0, 30.0)
        triggers["DRAMATIC PUNCTUATION"] = "Punctuation Clustering: Repeated exclamation or question marks."

    clickbait_score = min(100.0, clickbait_score)

    # 2. Sensationalism
    sensationalism_score = 0.0
    for word in SENSATIONAL_WORDS:
        matches = len(re.findall(rf'\b{word}\b', lower))
        if matches > 0:
            sensationalism_score += min(matches * 15.0, 35.0)
            triggers[word.upper()] = "Sensationalist Hyperbole: Word engineered to polarize emotional response."

    sensationalism_score = min(100.0, sensationalism_score)

    # 3. Emotion
    fear_count = sum(1 for w in FEAR_WORDS if w in lower)
    outrage_count = sum(1 for w in OUTRAGE_WORDS if w in lower)
    urgency_count = sum(1 for w in URGENCY_WORDS if w in lower)

    total_emotion = fear_count + outrage_count + urgency_count
    emotion_score = min(100.0, total_emotion * 18.0)

    tone = "Objective / Factual Journalism"
    if fear_count > outrage_count and fear_count > 0:
        tone = "Fear & Panic Induction"
    elif outrage_count >= fear_count and outrage_count > 0:
        tone = "High Outrage & Aggression"
    elif urgency_count > 0:
        tone = "High Urgency / Viral Prompt"

    return clickbait_score, sensationalism_score, emotion_score, tone, triggers
