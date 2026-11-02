
"""
language_service.py
===================

Detects likely English, Hindi (Devanagari), Hinglish, and unknown or
mixed-script input for VeriNews AI 2.0.

IMPORTANT LIMITATIONS:
- The trained ML models were trained on English-language news data only.
- Predictions for Hindi and Hinglish may be unreliable.
- This service does not translate text.
- This is a lightweight script and vocabulary heuristic, not a
  comprehensive language identification model.
- Multilingual accuracy is not claimed without labeled evaluation data.
"""

import re
from typing import Dict, Any, Optional


_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")
_LATIN_RE = re.compile(r"[A-Za-z]")
_LATIN_WORD_RE = re.compile(r"\b[a-z]+\b", re.IGNORECASE)

_HINGLISH_MARKERS = frozenset([
    "kya", "hai", "bhai", "dekho", "aur", "nahi", "nahin",
    "hoga", "hogi", "karo", "karna", "mera", "meri", "tera",
    "teri", "lekin", "matlab", "abhi", "theek", "thik",
    "sahi", "bilkul", "zaroor", "wala", "wali", "phir",
    "uske", "unke", "humara", "hamara", "tumhara",
    "tumhe", "tumko", "yeh", "woh", "unhe", "inhe",
    "accha", "achha", "kaise", "kyun", "kyunki", "mein",
    "mujhe", "tujhe", "raha", "rahi", "rahe", "haii",
    "hain", "tha", "thi", "nhi", "krna", "bta",
])

_ML_LANGUAGE_WARNING = (
    "The trained ML models were trained on English-language news data. "
    "Predictions for Hindi or Hinglish input may be unreliable. "
    "This system does not automatically translate the input."
)


def _result(
    language: str,
    supported: bool,
    warning: Optional[str],
    devanagari_ratio: float,
    details: str,
) -> Dict[str, Any]:
    return {
        "detected_language": language,
        "is_ml_supported": supported,
        "warning": warning,
        "devanagari_ratio": devanagari_ratio,
        "details": details,
    }


def detect_language(text: str) -> Dict[str, Any]:
    """
    Estimate language/script from character composition and common
    Hinglish markers.

    Returns:
        detected_language:
            "English", "Hindi (Devanagari)", "Hinglish", or "Unknown"
        is_ml_supported:
            True only when the input appears to be English under
            these lightweight checks.
        warning:
            Warning when input is empty, mixed, or potentially unsupported.
        devanagari_ratio:
            Devanagari characters divided by non-whitespace characters.
        details:
            Short explanation of the detection.
    """

    if not isinstance(text, str) or not text.strip():
        return _result(
            language="Unknown",
            supported=False,
            warning="Input text is empty or invalid.",
            devanagari_ratio=0.0,
            details="No usable text was provided for language detection.",
        )

    non_whitespace_chars = [
        char for char in text if not char.isspace()
    ]

    if not non_whitespace_chars:
        return _result(
            language="Unknown",
            supported=False,
            warning="Input contains no usable text.",
            devanagari_ratio=0.0,
            details="No usable text was provided for language detection.",
        )

    devanagari_count = len(_DEVANAGARI_RE.findall(text))
    latin_count = len(_LATIN_RE.findall(text))

    total_chars = len(non_whitespace_chars)

    devanagari_ratio = round(
        devanagari_count / total_chars,
        3,
    )

    latin_ratio = latin_count / total_chars

    latin_words = [
        word.lower()
        for word in _LATIN_WORD_RE.findall(text)
    ]

    word_set = set(latin_words)
    hinglish_hits = word_set.intersection(_HINGLISH_MARKERS)

    # If there is meaningful Devanagari text, do not claim English support.
    if devanagari_ratio > 0.10:
        if latin_count > 0:
            language = "Hinglish"
            details = (
                f"Mixed Latin and Devanagari scripts detected; "
                f"{devanagari_ratio * 100:.1f}% of non-whitespace "
                f"characters are Devanagari."
            )
        else:
            language = "Hindi (Devanagari)"
            details = (
                f"{devanagari_ratio * 100:.1f}% of non-whitespace "
                f"characters are Devanagari."
            )

        return _result(
            language=language,
            supported=False,
            warning=_ML_LANGUAGE_WARNING,
            devanagari_ratio=devanagari_ratio,
            details=details,
        )

    # Any Devanagari characters indicate mixed-script input.
    if devanagari_count > 0:
        return _result(
            language="Hinglish",
            supported=False,
            warning=_ML_LANGUAGE_WARNING,
            devanagari_ratio=devanagari_ratio,
            details=(
                "A mixture of Latin and Devanagari script was detected. "
                "Language identification may be uncertain for short text."
            ),
        )

    # Common transliterated Hindi vocabulary suggests Hinglish.
    # Require at least 2 distinct markers to prevent false positives on isolated loanwords.
    if len(hinglish_hits) >= 2:
        markers = ", ".join(sorted(hinglish_hits)[:5])

        return _result(
            language="Hinglish",
            supported=False,
            warning=_ML_LANGUAGE_WARNING,
            devanagari_ratio=devanagari_ratio,
            details=f"Multiple Hinglish markers detected: {markers}.",
        )

    # Reject text with no meaningful Latin letters instead of
    # classifying numbers, punctuation, or symbols as English.
    if latin_count == 0:
        return _result(
            language="Unknown",
            supported=False,
            warning="Language could not be identified from the available text.",
            devanagari_ratio=devanagari_ratio,
            details="No Latin letters or Devanagari characters were detected.",
        )

    # A single isolated marker in an otherwise English text is treated as English
    # rather than disabling ML support, unless the input is very short (<= 3 words).
    if len(hinglish_hits) == 1:
        marker = next(iter(hinglish_hits))
        if len(latin_words) <= 3:
            return _result(
                language="Unknown",
                supported=False,
                warning=(
                    "The short input may contain transliterated Hindi. "
                    "Language detection is uncertain."
                ),
                devanagari_ratio=devanagari_ratio,
                details=f"One possible Hinglish marker detected: {marker}.",
            )

        return _result(
            language="English",
            supported=True,
            warning=None,
            devanagari_ratio=devanagari_ratio,
            details=f"English text detected with isolated marker '{marker}'.",
        )

    # Lightweight fallback: Latin script without detected Hinglish markers.
    # This is only an estimate, not a full language identification result.
    if latin_ratio > 0:
        return _result(
            language="English",
            supported=True,
            warning=None,
            devanagari_ratio=devanagari_ratio,
            details=(
                "Input uses Latin script and no configured Hinglish "
                "markers were detected. Other languages written in "
                "Latin script may be misclassified."
            ),
        )

    return _result(
        language="Unknown",
        supported=False,
        warning="Language could not be identified reliably.",
        devanagari_ratio=devanagari_ratio,
        details="Insufficient language indicators were detected.",
    )
