import re
import math

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Lowercase and clean alphanumeric
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    return re.sub(r'\s+', ' ', cleaned).strip()

def calculate_readability(text: str) -> dict:
    if not text:
        return {"score": 65.0, "level": "Standard", "wordCount": 0, "sentenceCount": 0}

    words = re.findall(r'\b[a-zA-Z]+\b', text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s for s in sentences if s.strip()]

    word_count = max(1, len(words))
    sentence_count = max(1, len(sentences))

    # Syllables estimation
    total_syllables = sum(count_syllables(w) for w in words)

    asl = word_count / sentence_count
    asw = total_syllables / word_count
    flesch = 206.835 - (1.015 * asl) - (84.6 * asw)
    score = round(max(0.0, min(100.0, flesch)), 1)

    level = "Standard Journalistic Style"
    if score >= 70:
        level = "Simple / Casual (High Readability)"
    elif score < 40:
        level = "Academic / Complex Synthesis"

    return {
        "score": score,
        "level": level,
        "wordCount": word_count,
        "sentenceCount": sentence_count
    }

def count_syllables(word: str) -> int:
    word = word.lower()
    if len(word) <= 3:
        return 1
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)
