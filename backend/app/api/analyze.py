
import hashlib
import logging
import re
import urllib.parse
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.schemas.analysis import (
    NewsTextRequest,
    UrlRequest,
    AnalysisResponse,
    ScoreBreakdown,
    MLPredictionResult,
    MLModelVote,
    ExplainabilityResult,
    ExplainabilityFeature,
    EvidenceResult,
    EvidenceItem,
    LanguageDetectionResult,
)

from app.services.nlp_service import calculate_readability
from app.services.heuristic_service import analyze_heuristics
from app.services.domain_service import analyze_domain
from app.services.claim_service import extract_claims
from app.services import ml_prediction_service
from app.services.explainability_service import get_influential_features
from app.services.evidence_service import retrieve_evidence
from app.services.language_service import detect_language
from app.api.scans import add_scan

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_ml_result(raw: dict) -> MLPredictionResult:
    """Convert trained-model output into the API response schema."""

    if not isinstance(raw, dict) or not raw.get("available"):
        return MLPredictionResult(
            available=False,
            error=(
                raw.get("error", "ML models are unavailable.")
                if isinstance(raw, dict)
                else "ML prediction returned an invalid response."
            ),
            note=(
                "No trained-model prediction is available. "
                "Heuristic analysis is not a substitute for ML output."
            ),
        )

    final_prediction = raw.get("final") or raw.get("final_prediction")

    if not final_prediction:
        return MLPredictionResult(
            available=False,
            error="The ML service did not return a final prediction.",
            note="No trained-model verdict is available.",
        )

    # Build Transformer vote if available
    trans_raw = raw.get("transformer")
    trans_vote = None
    if isinstance(trans_raw, dict):
        trans_vote = MLModelVote(
            model_name="Semantic Transformer (BERT/RoBERTa)",
            prediction=str(trans_raw.get("prediction", "UNKNOWN")),
            features_used="Contextual attention embeddings (512 tokens max)",
            confidence=trans_raw.get("confidence"),
            raw_score=trans_raw.get("fake_prob"),
            details=trans_raw,
        )

    return MLPredictionResult(
        available=True,
        architecture=raw.get("architecture", "Hybrid Traditional ML + Semantic Transformer"),
        hybrid_strategy=raw.get("hybrid_strategy"),
        lr=MLModelVote(
            model_name="Logistic Regression",
            prediction=str(raw.get("lr", "UNKNOWN")),
            features_used="TF-IDF vectorizer; full feature set",
        ),
        svm=MLModelVote(
            model_name="Linear SVM",
            prediction=str(raw.get("svm", "UNKNOWN")),
            features_used="TF-IDF vectorizer; full feature set",
        ),
        rf=MLModelVote(
            model_name="Random Forest",
            prediction=str(raw.get("rf", "UNKNOWN")),
            features_used="First 5,000 TF-IDF features",
        ),
        transformer=trans_vote,
        traditional_prediction=raw.get("traditional_prediction"),
        transformer_prediction=raw.get("transformer_prediction"),
        transformer_available=bool(raw.get("transformer_available", False)),
        fallback_active=bool(raw.get("fallback_active", False)),
        fallback_reason=raw.get("fallback_reason"),
        final_prediction=str(final_prediction).upper(),
        fake_votes=raw.get("fake_votes"),
        real_votes=raw.get("real_votes"),
        model_agreement=raw.get("model_agreement"),
        fake_probability=raw.get("fake_probability"),
        real_probability=raw.get("real_probability"),
        traditional_fake_prob=raw.get("traditional_fake_prob"),
        transformer_fake_prob=raw.get("transformer_fake_prob"),
        weights_used=raw.get("weights_used"),
        uncertainty_status=raw.get(
            "uncertainty_status",
            "NOT_CALCULATED",
        ),
        note=raw.get(
            "note",
            "Predictions reflect statistical patterns learned from training data. "
            "Model agreement does not prove factual correctness.",
        ),
    )


def _build_explainability(text: str) -> ExplainabilityResult:
    """Build a safe explainability response."""

    try:
        raw = get_influential_features(text, top_n=10)

        if not isinstance(raw, dict):
            raise ValueError("Invalid explainability response")

        features = [
            ExplainabilityFeature(
                word=item["word"],
                direction=item["direction"],
                contribution_score=float(item["contribution_score"]),
            )
            for item in raw.get("features", [])
            if isinstance(item, dict)
            and "word" in item
            and "direction" in item
            and "contribution_score" in item
        ]

        return ExplainabilityResult(
            status=raw.get("status", "unavailable"),
            reason=raw.get("reason"),
            features=features,
            disclaimer=raw.get(
                "disclaimer",
                "Model explanations are statistical associations, not factual evidence.",
            ),
        )

    except Exception:
        logger.exception("Explainability calculation failed")
        return ExplainabilityResult(
            status="unavailable",
            reason="The explanation service could not process this input.",
            features=[],
            disclaimer=(
                "Model explanations are statistical associations, "
                "not factual evidence."
            ),
        )


def _build_evidence(headline: str, content: str) -> EvidenceResult:
    """Retrieve evidence without inventing sources or search results."""

    claim_text = (headline or "").strip() or (content or "")[:120].strip()

    if not claim_text:
        return EvidenceResult(
            status="NO_RESULTS",
            message="No claim text was available for evidence retrieval.",
            items=[],
            note="No external evidence was retrieved.",
        )

    try:
        raw = retrieve_evidence(claim_text, max_results=5)

        if not isinstance(raw, dict):
            raise ValueError("Invalid evidence service response")

        items = [
            EvidenceItem(
                snippet=item["snippet"],
                source_title=item["source_title"],
                url=item["url"],
                retrieved_at=item["retrieved_at"],
                evidence_status=item["evidence_status"],
                note=item["note"],
            )
            for item in raw.get("items", [])
            if isinstance(item, dict)
            and all(
                key in item
                for key in (
                    "snippet",
                    "source_title",
                    "url",
                    "retrieved_at",
                    "evidence_status",
                    "note",
                )
            )
        ]

        return EvidenceResult(
            status=raw.get("status", "ERROR"),
            message=raw.get(
                "message",
                "Evidence retrieval did not provide a status message.",
            ),
            provider=raw.get("provider"),
            items=items,
            retrieved_at=raw.get("retrieved_at"),
            note=raw.get(
                "note",
                "Retrieved material requires independent evaluation.",
            ),
        )

    except Exception:
        logger.exception("Evidence retrieval failed")
        return EvidenceResult(
            status="ERROR",
            message="Evidence retrieval failed.",
            items=[],
            note="No evidence is claimed because retrieval did not complete.",
        )


def _build_language_detection(text: str) -> LanguageDetectionResult:
    """Build language information with a safe fallback."""

    try:
        raw = detect_language(text)

        return LanguageDetectionResult(
            detected_language=raw.get("detected_language", "UNKNOWN"),
            is_ml_supported=bool(raw.get("is_ml_supported", False)),
            warning=raw.get("warning"),
            devanagari_ratio=float(raw.get("devanagari_ratio", 0.0)),
            details=raw.get("details", "Language detection completed."),
        )

    except Exception:
        logger.exception("Language detection failed")
        return LanguageDetectionResult(
            detected_language="UNKNOWN",
            is_ml_supported=False,
            warning="Language detection failed; ML language support is unknown.",
            devanagari_ratio=0.0,
            details="Language could not be reliably identified.",
        )


def _safe_domain_info(url: str) -> dict:
    """Call domain analysis safely and normalize expected fields."""

    if not url.strip():
        return {
            "name": "Unknown",
            "category": "Not provided",
            "trustScore": 0,
            "status": "URL_NOT_PROVIDED",
        }

    try:
        result = analyze_domain(url)

        if not isinstance(result, dict):
            raise ValueError("Invalid domain service response")

        result = dict(result)
        result.setdefault("name", "Unknown")
        result.setdefault("category", "Unknown")
        result.setdefault("trustScore", 0)
        return result

    except Exception:
        logger.exception("Domain analysis failed")

        try:
            hostname = urllib.parse.urlparse(url).hostname or "Unknown"
        except Exception:
            hostname = "Unknown"

        return {
            "name": hostname,
            "category": "Unknown",
            "trustScore": 0,
            "status": "NOT_VERIFIED",
            "note": "Domain reputation could not be checked.",
        }


def _number(value, default=0.0) -> float:
    """Convert a value to a finite numeric score."""

    try:
        number = float(value)
        if number != number or number in (float("inf"), float("-inf")):
            return default
        return max(0.0, min(100.0, number))
    except (TypeError, ValueError):
        return default


def _make_claims(headline: str, content: str, risk_score: float):
    """Extract claims using the project's existing service."""

    try:
        claims = extract_claims(headline, content, risk_score)
        return claims if isinstance(claims, list) else []
    except Exception:
        logger.exception("Claim extraction failed")

        text = content.strip() or headline.strip()
        sentences = re.split(r"(?<=[.!?])\s+", text)

        return [
            {
                "id": f"CLM-{index}",
                "text": sentence[:500],
                "importance": "Medium",
                "riskLevel": "Unknown",
                "verificationStatus": "UNVERIFIED",
            }
            for index, sentence in enumerate(sentences[:5], start=1)
            if len(sentence.strip()) >= 20
        ]


@router.post("/text", response_model=AnalysisResponse)
def analyze_news_text(req: NewsTextRequest):
    headline = (req.headline or "").strip()
    content = (req.content or "").strip()
    url = (req.url or "").strip()
    combined = f"{headline} {content}".strip()

    if not combined:
        raise HTTPException(
            status_code=400,
            detail="Headline or content must be provided.",
        )

    if len(combined) > 200000:
        raise HTTPException(
            status_code=413,
            detail="Text exceeds the maximum length of 200,000 characters.",
        )

    scan_id = f"VERITAS-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now(timezone.utc).isoformat()
    sha256_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()

    lower = combined.lower()
    words = combined.split()

    # 1. Readability analysis
    try:
        readability = calculate_readability(combined)
        if not isinstance(readability, dict):
            readability = {}
    except Exception:
        logger.exception("Readability calculation failed")
        readability = {}

    # 2. Language and writing heuristics
    try:
        (
            clickbait_score,
            sensationalism_score,
            emotion_score,
            emotional_tone,
            triggers,
        ) = analyze_heuristics(headline, content)
    except Exception:
        logger.exception("Heuristic analysis failed")
        clickbait_score = 0.0
        sensationalism_score = 0.0
        emotion_score = 0.0
        emotional_tone = "Unknown"
        triggers = {}

    clickbait_score = _number(clickbait_score)
    sensationalism_score = _number(sensationalism_score)
    emotion_score = _number(emotion_score)

    if not isinstance(triggers, dict):
        triggers = {}

    # 3. Domain analysis
    domain_info = _safe_domain_info(url)
    domain_trust = _number(domain_info.get("trustScore", 0))

    # 4. Language detection
    lang_detection = _build_language_detection(combined)

    # 5. Trained ML predictions
    try:
        ml_raw = ml_prediction_service.predict(combined)
    except Exception:
        logger.exception("Trained-model prediction failed")
        ml_raw = {
            "available": False,
            "error": "The trained-model prediction service failed.",
        }

    ml_result = _build_ml_result(ml_raw)

    # 6. Explainability
    try:
        cleaned_text = ml_prediction_service._clean_text(combined)
    except Exception:
        cleaned_text = combined

    explainability = _build_explainability(cleaned_text)

    # 7. External evidence retrieval
    evidence = _build_evidence(headline, content)

    # 8. Composite risk scores and probabilities
    # Integrates ML ensemble predictions with linguistic & domain heuristics.
    language_risk = (
        clickbait_score * 0.35
        + sensationalism_score * 0.35
        + emotion_score * 0.30
    )

    if ml_result.available and ml_raw.get("fake_probability") is not None:
        # Genuine ML ensemble probability directly from the trained classifiers.
        # This eliminates artificial clamping artifacts (e.g. 50.1%/49.9%) and ensures
        # mathematical harmony between the ML voting verdict and the reported probabilities.
        raw_fake = float(ml_raw["fake_probability"])
        fake_probability = round(max(2.0, min(98.0, raw_fake)), 1)
        real_probability = round(100.0 - fake_probability, 1)

        # AI Confidence: combination of voting agreement and probability margin
        agreement = ml_result.model_agreement or 66.7
        prob_margin = abs(fake_probability - 50.0) * 2.0  # 0 to 100 scale
        ai_confidence = round(
            min(99.0, max(50.0, agreement * 0.50 + prob_margin * 0.35 + 15.0)),
            1,
        )
    else:
        # Heuristic-only fallback when ML models are unavailable
        heuristic_fake = (
            language_risk * 0.70
            + (100.0 - domain_trust) * 0.30
        )
        fake_probability = round(max(2.0, min(98.0, heuristic_fake)), 1)
        real_probability = round(100.0 - fake_probability, 1)

        ai_confidence = round(
            min(95.0, max(40.0, max(fake_probability, real_probability) * 0.65 + 15.0)),
            1,
        )

    # Multi-factor composite risk index:
    # Integrates statistical ML risk (50%), linguistic manipulation indicators (30%),
    # and domain untrustworthiness (20%).
    domain_risk = max(0.0, 100.0 - domain_trust)
    risk_score = round(
        fake_probability * 0.50
        + language_risk * 0.30
        + domain_risk * 0.20,
        1,
    )

    if risk_score <= 25:
        risk_label = "LOW RISK"
        risk_color = "#10b981"
        risk_badge = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
    elif risk_score <= 50:
        risk_label = "MODERATE RISK"
        risk_color = "#f59e0b"
        risk_badge = "bg-amber-500/10 text-amber-400 border-amber-500/30"
    elif risk_score <= 75:
        risk_label = "HIGH RISK"
        risk_color = "#f97316"
        risk_badge = "bg-orange-500/10 text-orange-400 border-orange-500/30"
    else:
        risk_label = "CRITICAL RISK"
        risk_color = "#ef4444"
        risk_badge = "bg-rose-500/10 text-rose-400 border-rose-500/30"

    risk_level = {
        "label": risk_label,
        "color": risk_color,
        "badgeBg": risk_badge,
        "basis": "Composite ML and heuristic indicators; not factual verification.",
    }

    credibility_score = round(
        real_probability * 0.70 + domain_trust * 0.30,
        1,
    )

    # 9. Verdict
    # A model classification is not a fact-check.
    if ml_result.available and ml_result.final_prediction:
        prediction = ml_result.final_prediction.upper()

        if prediction == "FAKE":
            verdict = "ML PREDICTS FAKE — NOT FACT-CHECKED"
        elif prediction == "REAL":
            verdict = "ML PREDICTS REAL — NOT FACT-CHECKED"
        else:
            verdict = "ML RESULT UNCERTAIN — VERIFY INDEPENDENTLY"
    else:
        verdict = "ML UNAVAILABLE — HEURISTIC ANALYSIS ONLY"

    # 10. Claims
    claims = _make_claims(headline, content, risk_score)

    # 11. Primary findings
    primary_findings = [
        (
            "Elevated sensationalism or emotional-language indicators detected."
            if fake_probability > 60
            else "Fewer sensational-language indicators were detected by the heuristics."
        ),
        (
            "Hyperbolic-language indicators detected."
            if sensationalism_score > 30
            else "No strong configured hyperbolic-language indicators detected."
        ),
        (
            f"Source domain '{domain_info.get('name', 'Unknown')}' "
            f"was assessed as '{domain_info.get('category', 'Unknown')}'."
            if url
            else "Text-only scan performed; no source URL was provided."
        ),
        "Heuristic scores are not factual verification or calibrated probabilities.",
    ]

    if not ml_result.available:
        primary_findings.append(
            "Trained ML models are unavailable for this scan."
        )

    if lang_detection.warning:
        primary_findings.append(
            f"Language warning: {lang_detection.warning}"
        )

    if evidence.status == "NOT_CONFIGURED":
        primary_findings.append(
            "External evidence retrieval is not configured."
        )
    elif evidence.status in ("ERROR", "NO_RESULTS"):
        primary_findings.append(
            "No usable external evidence was retrieved for this scan."
        )

    # 12. Headline consistency
    head_tokens = set(re.findall(r"\b[a-z]{3,}\b", headline.lower()))
    body_tokens = set(re.findall(r"\b[a-z]{3,}\b", content.lower()))
    overlap = len(head_tokens.intersection(body_tokens))

    consistency_score = (
        round(overlap / max(1, len(head_tokens)) * 100.0, 1)
        if head_tokens
        else 100.0
    )

    if consistency_score >= 65:
        consistency_rating = "HIGH CONSISTENCY"
    elif consistency_score >= 35:
        consistency_rating = "MODERATE CONSISTENCY"
    else:
        consistency_rating = "LOW CONSISTENCY"

    headline_consistency = {
        "score": consistency_score,
        "rating": consistency_rating,
        "possibleHeadlineExaggeration": (
            consistency_score < 40 and clickbait_score > 30
        ),
        "explanation": (
            "Higher keyword overlap between headline and body."
            if consistency_score >= 60
            else "Lower keyword overlap; manual review is recommended."
        ),
    }

    # 13. Writing manipulation indicators
    caps_count = sum(
        1 for word in words if word.isupper() and len(word) > 2
    )
    caps_percentage = round(
        caps_count / max(1, len(words)) * 100.0,
        1,
    )

    repeated_exclamations = len(re.findall(r"!{2,}", combined))
    repeated_questions = len(re.findall(r"\?{2,}", combined))

    writing_score = round(
        min(
            100.0,
            caps_percentage * 2.0
            + repeated_exclamations * 15.0
            + repeated_questions * 15.0,
        ),
        1,
    )

    writing_manipulation = {
        "score": writing_score,
        "capsPercentage": caps_percentage,
        "excessivePunctuationCount": (
            repeated_exclamations + repeated_questions
        ),
        "repeatedExclamationCount": repeated_exclamations,
        "repeatedQuestionCount": repeated_questions,
        "emojiCount": len(
            re.findall(r"[\U00010000-\U0010ffff]", combined)
        ),
    }

    # 14. Duplicate sentences
    duplicate_phrases = []
    sentences = [
        sentence.strip().lower()
        for sentence in re.split(r"[.!?]+", content)
        if len(sentence.strip()) > 15
    ]

    sentence_counts = {}
    for sentence in sentences:
        sentence_counts[sentence] = sentence_counts.get(sentence, 0) + 1

    for phrase, frequency in sentence_counts.items():
        if frequency > 1:
            duplicate_phrases.append({
                "phrase": phrase,
                "frequency": frequency,
                "riskContribution": frequency * 15,
            })

    # 15. Paragraph-level heuristic heatmap
    paragraphs = [
        paragraph.strip()
        for paragraph in content.splitlines()
        if len(paragraph.strip()) > 10
    ]

    heatmap = []

    for index, paragraph in enumerate(paragraphs, start=1):
        paragraph_lower = paragraph.lower()
        paragraph_risk = 0
        signals = []

        if any(
            word in paragraph_lower
            for word in ["shocking", "miracle", "secret", "exposed", "cure"]
        ):
            paragraph_risk += 35
            signals.append("Sensational keywords")

        if any(
            phrase in paragraph_lower
            for phrase in [
                "urgent",
                "immediately",
                "share now",
                "before it gets deleted",
            ]
        ):
            paragraph_risk += 35
            signals.append("Artificial urgency")

        if "!" in paragraph:
            paragraph_risk += 15
            signals.append("Exclamation mark")

        paragraph_risk = min(100, paragraph_risk)

        if paragraph_risk >= 70:
            paragraph_level = "CRITICAL RISK"
        elif paragraph_risk >= 45:
            paragraph_level = "HIGH RISK"
        elif paragraph_risk >= 20:
            paragraph_level = "MODERATE RISK"
        else:
            paragraph_level = "LOW RISK"

        heatmap.append({
            "index": index,
            "text": paragraph,
            "riskScore": paragraph_risk,
            "riskLevel": paragraph_level,
            "signals": signals,
            "explanation": (
                "Configured language indicators were detected."
                if signals
                else "No configured paragraph-level trigger was detected."
            ),
        })

    # 16. Keyword indicators
    keyword_cloud = []

    for term in [
        "shocking",
        "miracle",
        "secret",
        "exposed",
        "urgent",
        "immediately",
        "share this",
        "devastating",
        "conspiracy",
    ]:
        count = lower.count(term)

        if count > 0:
            keyword_cloud.append({
                "word": term,
                "category": (
                    "Sensational"
                    if term in ["shocking", "miracle", "conspiracy"]
                    else "Urgency"
                ),
                "weight": min(5, 2 + count),
                "count": count,
            })

    # 17. Heuristic risk breakdown
    risk_breakdown = {
        "Sensationalism & Clickbait": int(sensationalism_score * 0.30),
        "Emotional Outrage Bias": int(emotion_score * 0.25),
        "Artificial Urgency": (
            20 if "urgent" in lower or "immediately" in lower else 5
        ),
        "Typographical Manipulation": int(writing_score * 0.20),
        "Viral Push Pressure": (
            25 if "share" in lower or "forward" in lower else 0
        ),
    }

    # 18. Trust indicators: indicators only, not proof
    trust_signals = []

    if fake_probability < 35:
        trust_signals.append(
            "Lower heuristic risk indicators were observed; "
            "this does not establish factual accuracy."
        )

    if url.lower().startswith("https://"):
        trust_signals.append(
            "The supplied URL uses HTTPS; this alone does not establish reliability."
        )

    if len(words) > 50:
        trust_signals.append(f"Text length: {len(words)} words.")

    viral_manipulation = {
        "risk": (
            75.0
            if "share this" in lower or "forward this" in lower
            else 10.0
        ),
        "triggers": [
            trigger
            for trigger in [
                "share this immediately",
                "forward this",
                "before it gets deleted",
            ]
            if trigger in lower
        ],
    }

    # 19. Numerical claims
    numerical_matches = re.findall(
        r"(\b\d+(?:\.\d+)?%|\b\d+\s*(?:billion|million|thousand|crore)\b|\$\d+)",
        combined,
        flags=re.IGNORECASE,
    )

    numerical_claims = [
        {
            "number": number,
            "statement": f"Assertion containing numeric figure {number}",
            "verificationRecommended": True,
        }
        for number in dict.fromkeys(numerical_matches[:5])
    ]

    # 20. Named-entity keyword indicators
    entities = []

    for organization in [
        "NASA",
        "WHO",
        "CDC",
        "FDA",
        "Reuters",
        "BBC",
        "White House",
        "Supreme Court",
    ]:
        if organization.lower() in lower:
            entities.append({
                "name": organization,
                "type": "ORGANIZATION",
            })

    # 21. Uncertainty language
    uncertainty_signals = [
        word
        for word in [
            "allegedly",
            "reportedly",
            "unconfirmed",
            "may",
            "might",
            "claims",
        ]
        if re.search(rf"\b{re.escape(word)}\b", lower)
    ]

    uncertainty_language = {
        "signals": uncertainty_signals,
        "explanation": (
            "Hedging language detected: "
            + ", ".join(uncertainty_signals)
            + ". This can indicate qualification or uncertainty."
            if uncertainty_signals
            else "No configured speculative hedging markers were detected."
        ),
    }

    # 22. Source citation indicators
    source_citations = {
        "urlCount": 1 if url else 0,
        "namedSourcesCount": len(entities),
        "quoteCount": len(re.findall(r'"([^"]*)"', combined)),
        "detected": (
            [f"Source Domain: {domain_info.get('name', 'Unknown')}"]
            if url
            else []
        ),
    }

    # 23. Multilingual information
    multilingual = {
        "language": lang_detection.detected_language,
        "isSupported": lang_detection.is_ml_supported,
        "notice": (
            lang_detection.warning or lang_detection.details
        ),
    }

    # 24. Construct final response
    response = AnalysisResponse(
        scanId=scan_id,
        timestamp=timestamp,
        verdict=verdict,
        riskLevel=risk_level,
        scores=ScoreBreakdown(
            fakeProbability=fake_probability,
            realProbability=real_probability,
            aiConfidence=ai_confidence,
            credibilityScore=credibility_score,
            riskScore=risk_score,
            clickbaitScore=clickbait_score,
            sensationalismScore=sensationalism_score,
            emotionalManipulationScore=emotion_score,
            sourceTrustScore=domain_trust,
            languageRiskScore=round(language_risk, 1),
        ),
        linguistic={
            "emotionalTone": emotional_tone,
            "readability": readability,
            "sensationalWordsCount": int(sensationalism_score / 15),
            "dominantBias": (
                "Outrage / Alarmist"
                if emotion_score > 40
                else "Neutral / Balanced"
            ),
        },
        domain=domain_info,
        highlightedTriggers=triggers,
        claims=claims,
        primaryFindings=primary_findings,
        recommendedAction=(
            "Review language indicators and verify important claims "
            "against independent, reliable sources."
        ),
        factCheckUrl=(
            "https://toolbox.google.com/factcheck/explorer/search/"
            + urllib.parse.quote((headline or content[:60]).strip())
            + "?hl=en"
        ),
        headlineConsistency=headline_consistency,
        writingManipulation=writing_manipulation,
        duplicatePhrases=duplicate_phrases,
        readability=readability,
        writingStyle=(
            "Urgent"
            if "urgent" in lower
            else (
                "Sensational"
                if sensationalism_score > 40
                else "Neutral"
            )
        ),
        heatmap=heatmap,
        keywordCloud=keyword_cloud,
        fingerprint={
            "scanId": scan_id,
            "sha256": sha256_hash,
            "timestamp": timestamp,
        },
        riskBreakdown=risk_breakdown,
        positiveTrustSignals=trust_signals,
        viralManipulation=viral_manipulation,
        numericalClaims=numerical_claims,
        entities=entities,
        uncertaintyLanguage=uncertainty_language,
        sourceCitations=source_citations,
        multilingual=multilingual,
        mlPrediction=ml_result,
        explainability=explainability,
        evidence=evidence,
        languageDetection=lang_detection,
        sourceMetadata={
            "publisher": req.publisher,
            "source_type": req.source_type,
            "content_availability": req.content_availability,
        } if (req.publisher or req.source_type or req.content_availability) else None,
    )

    # Save the actual analysis result in the in-memory scan history.
    try:
        # Pydantic v2 uses model_dump(); v1 uses dict().
        dump = getattr(response, "model_dump", None)
        scan_data = dump() if dump else response.dict()
        add_scan(scan_data)
    except Exception:
        logger.exception("Failed to save scan history")

    return response


@router.post("/url", response_model=AnalysisResponse)
def analyze_news_url(req: UrlRequest):
    """
    Fetch content from a URL and analyse it.

    Uses requests + BeautifulSoup to extract visible text, then delegates
    to the same analysis pipeline as /text.  Falls back gracefully if
    fetching or parsing fails.
    """
    url = (req.url or "").strip()

    if not url:
        raise HTTPException(status_code=400, detail="URL must be provided.")

    headline = ""
    content = ""

    try:
        import requests as http_requests
        from bs4 import BeautifulSoup

        resp = http_requests.get(url, timeout=12, headers={
            "User-Agent": "VeriNewsBot/2.0 (research project)"
        })
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Try to extract a headline from common tags
        title_tag = soup.find("h1") or soup.find("title")
        if title_tag:
            headline = title_tag.get_text(strip=True)[:500]

        # Extract body text from paragraphs
        paragraphs = soup.find_all("p")
        content = "\n".join(
            p.get_text(strip=True)
            for p in paragraphs
            if len(p.get_text(strip=True)) > 20
        )[:100_000]

        if not content.strip():
            # Fallback: use all visible text
            content = soup.get_text(separator="\n", strip=True)[:100_000]

    except Exception:
        logger.exception("Failed to fetch or parse URL: %s", url)
        # Still run analysis on the URL string itself so the endpoint
        # doesn't simply error out.
        headline = "URL Scan"
        content = f"Content could not be retrieved from {url}"

    # Delegate to the /text analysis pipeline
    text_req = NewsTextRequest(headline=headline, content=content, url=url)
    return analyze_news_text(text_req)
