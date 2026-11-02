
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class NewsTextRequest(BaseModel):
    headline: Optional[str] = Field(
        default="",
        description="News article headline"
    )
    content: Optional[str] = Field(
        default="",
        description="Full text body or assertion statement"
    )
    url: Optional[str] = Field(
        default="",
        description="Optional source URL"
    )
    publisher: Optional[str] = Field(
        default=None,
        description="Optional publisher name"
    )
    source_type: Optional[str] = Field(
        default=None,
        description="Source type (rss, api, youtube, official, factcheck)"
    )
    content_availability: Optional[str] = Field(
        default=None,
        description="Content availability level (headline-only, summary-only, full-text)"
    )


class UrlRequest(BaseModel):
    url: str = Field(..., description="Target news article URL")


class ClaimItem(BaseModel):
    id: str
    text: str
    importance: str
    riskLevel: str
    verificationStatus: str


class ScoreBreakdown(BaseModel):
    # -----------------------------------------------------------------------
    # IMPORTANT: The scores below represent statistical model outputs and
    # multi-factor heuristic evaluations. They are NOT calibrated posterior
    # probabilities of real-world factual truth or a certified fact-check.
    # -----------------------------------------------------------------------
    fakeProbability: float       # ML ensemble fake probability (0–100) or heuristic fallback
    realProbability: float       # 100 − fakeProbability (credibility likelihood)
    aiConfidence: float          # Model agreement and probability margin estimate (0–100)
    credibilityScore: float      # Source & textual credibility index
    riskScore: float             # Multi-factor composite risk index (ML + language + domain)
    clickbaitScore: float        # Clickbait & formatting manipulation score
    sensationalismScore: float   # Sensationalism & hyperbole score
    emotionalManipulationScore: float # Emotional tone & outrage score
    sourceTrustScore: float      # Domain trust score (0–100)
    languageRiskScore: float     # Linguistic risk index


# ============================================================
# VERINEWS AI 2.0 — MACHINE LEARNING SCHEMAS
# ============================================================

class MLModelVote(BaseModel):
    """Prediction from one trained classifier."""
    model_name: str
    prediction: str
    features_used: str
    confidence: Optional[float] = None
    raw_score: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class MLPredictionResult(BaseModel):
    """
    Output from the VeriNews AI 2.0 Hybrid Architecture (Traditional ML + Transformer).

    Model agreement measures voting consensus only.
    It is not a probability of factual correctness.
    """
    available: bool
    error: Optional[str] = None

    architecture: Optional[str] = "Hybrid Traditional ML + Semantic Transformer"
    hybrid_strategy: Optional[str] = None

    # Individual classifier outputs
    lr: Optional[MLModelVote] = None
    svm: Optional[MLModelVote] = None
    rf: Optional[MLModelVote] = None
    transformer: Optional[MLModelVote] = None

    # Sub-branch outputs
    traditional_prediction: Optional[str] = None
    transformer_prediction: Optional[str] = None
    transformer_available: bool = False
    fallback_active: bool = False
    fallback_reason: Optional[str] = None

    # Fused predictions
    final_prediction: Optional[str] = None
    fake_votes: Optional[int] = None
    real_votes: Optional[int] = None
    model_agreement: Optional[float] = None
    fake_probability: Optional[float] = None
    real_probability: Optional[float] = None
    traditional_fake_prob: Optional[float] = None
    transformer_fake_prob: Optional[float] = None
    weights_used: Optional[Dict[str, float]] = None

    # Expected values: MODEL_CONSENSUS, MODEL_MAJORITY, MODEL_DISAGREEMENT
    uncertainty_status: Optional[str] = None

    note: Optional[str] = None


# ============================================================
# EXPLAINABLE AI
# ============================================================

class ExplainabilityFeature(BaseModel):
    word: str
    direction: str
    contribution_score: float


class ExplainabilityResult(BaseModel):
    status: str
    reason: Optional[str] = None

    features: List[ExplainabilityFeature] = Field(
        default_factory=list
    )

    disclaimer: str = (
        "Influential words reflect patterns learned by the model. "
        "They are not factual evidence that a claim is true or false."
    )


# ============================================================
# EVIDENCE RETRIEVAL
# ============================================================

class EvidenceItem(BaseModel):
    snippet: str
    source_title: str
    url: str
    retrieved_at: str

    # Must describe actual evidence assessment, not model prediction.
    evidence_status: str
    note: str


class EvidenceResult(BaseModel):
    # Expected values: NOT_CONFIGURED, OK, NO_RESULTS, ERROR
    status: str
    message: str

    provider: Optional[str] = None

    items: List[EvidenceItem] = Field(
        default_factory=list
    )

    retrieved_at: Optional[str] = None
    note: str = (
        "Retrieved sources do not automatically establish factual truth. "
        "Review the source and supporting context."
    )


# ============================================================
# LANGUAGE DETECTION
# ============================================================

class LanguageDetectionResult(BaseModel):
    detected_language: str
    is_ml_supported: bool

    warning: Optional[str] = None
    devanagari_ratio: float
    details: str


# ============================================================
# MAIN ANALYSIS RESPONSE
# Existing fields are preserved for compatibility.
# ============================================================

class AnalysisResponse(BaseModel):
    scanId: str
    timestamp: str
    verdict: str

    riskLevel: Dict[str, Any]
    scores: ScoreBreakdown
    linguistic: Dict[str, Any]
    domain: Dict[str, Any]
    highlightedTriggers: Dict[str, str]

    claims: List[ClaimItem]
    primaryFindings: List[str]
    recommendedAction: str
    factCheckUrl: str

    # Existing forensic modules
    headlineConsistency: Optional[Dict[str, Any]] = None
    writingManipulation: Optional[Dict[str, Any]] = None
    duplicatePhrases: Optional[List[Dict[str, Any]]] = None
    readability: Optional[Dict[str, Any]] = None
    writingStyle: Optional[str] = None
    heatmap: Optional[List[Dict[str, Any]]] = None
    keywordCloud: Optional[List[Dict[str, Any]]] = None
    fingerprint: Optional[Dict[str, Any]] = None
    riskBreakdown: Optional[Dict[str, Any]] = None
    positiveTrustSignals: Optional[List[str]] = None
    viralManipulation: Optional[Dict[str, Any]] = None
    numericalClaims: Optional[List[Dict[str, Any]]] = None
    entities: Optional[List[Dict[str, Any]]] = None
    uncertaintyLanguage: Optional[Dict[str, Any]] = None
    sourceCitations: Optional[Dict[str, Any]] = None
    multilingual: Optional[Dict[str, Any]] = None

    # New VeriNews AI 2.0 fields
    mlPrediction: Optional[MLPredictionResult] = None
    explainability: Optional[ExplainabilityResult] = None
    evidence: Optional[EvidenceResult] = None
    languageDetection: Optional[LanguageDetectionResult] = None
    sourceMetadata: Optional[Dict[str, Any]] = None
