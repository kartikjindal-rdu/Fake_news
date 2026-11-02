# FastAPI Endpoint Verification Report — VeriNews AI 2.0

**Base URL:** `http://localhost:8000`  
**API Router Definitions:** `backend/app/api/`  
**FastAPI Entrypoint:** `backend/main.py`

---

## 1. Verified Endpoints & Request/Response Contracts

### A. POST `/api/analyze/text`
- **Purpose:** Primary news article analysis route.
- **Request Body (`NewsTextRequest`):**
  ```json
  {
    "headline": "Economic Stabilization Committee Convenes in Geneva",
    "content": "Finance ministers from twenty nations met to formalize international trade agreements on Monday.",
    "url": "https://www.example.com/news"
  }
  ```
- **Response Structure (`AnalysisResponse`):**
  - `scanId`: Unique UUID tracking string.
  - `timestamp`: UTC ISO timestamp.
  - `verdict`: Final composite verdict (`"REAL"`, `"LIKELY REAL"`, `"UNVERIFIED"`, `"LIKELY FAKE"`, `"FAKE"`).
  - `riskLevel`: Composite 4-tier risk classification (`label`, `color`, `badgeBg`, `basis`).
  - `scores`: `ScoreBreakdown` containing `fakeProbability`, `realProbability`, `aiConfidence`, `credibilityScore`, `sensationalismScore`, `clickbaitScore`, `emotionalManipulationScore`, `riskScore`.
  - `mlPrediction`: `MLPredictionResult` containing `architecture`, `hybrid_strategy`, `available`, `fallback_active`, `final_prediction`, `model_agreement`, `fake_probability`, `real_probability`, `lr`, `svm`, `rf`, `transformer`, `uncertainty_status`, `note`.
  - `explainability`: Influential vocabulary words, direction (`FAKE`/`REAL`), and contribution scores.
  - `evidence`: Search-retrieved corroborating/refuting evidence snippets or `NOT_CONFIGURED` status.
  - `languageDetection`: Detected language, support flag, and Hinglish warnings.

### B. GET `/api/model/info`
- **Purpose:** Model metadata, benchmark results, and architecture breakdown.
- **Output:**
  - `available`: `true`
  - `architecture`: `"Two-Branch Hybrid (Lexical TF-IDF Ensemble + Semantic Transformer Encoder)"`
  - `models`: Array of model descriptors including Logistic Regression, Linear SVM, Random Forest, Semantic Transformer, and Hybrid Ensemble.
  - `benchmark`: ISOT held-out test split metrics (98.79% accuracy, 98.73% F1).
  - `limitations`: Explicit statement of source-neutral bounds and linguistic scope.

### C. POST `/api/model/diagnostics`
- **Purpose:** Real-time dry run inference and pipeline latency benchmark.
- **Output:**
  - `status`: `"HEALTHY"`
  - `models_verified`: `["Logistic Regression", "Linear SVM", "Random Forest", "TF-IDF Vectorizer"]`
  - `transformer_branch`: Availability, device, fallback mode status.
  - `diagnostic_inference`: Latency in milliseconds, strategy string, model votes, and ensemble verdict.

### D. GET `/api/model/drift`
- **Purpose:** Real-time drift monitoring and inference telemetry.
- **Output:**
  - Total inferences tracked.
  - Population Stability Index (PSI).
  - Distribution shift alerts and average inference latency.

---

## 2. Boundary and Robustness Verification

| Test Scenario | Input Sent | Expected Status | Response Behavior |
|:---|:---|:---:|:---|
| **Valid News Text** | High-credibility journalistic assertion | `200 OK` | Evaluates all tiers, returns `verdict="REAL"`, high credibility score. |
| **Sensational Text** | Clickbait assertion with hyperbole | `200 OK` | Triggers clickbait heuristic, returns `verdict="FAKE"` or `"LIKELY FAKE"`. |
| **Empty Text** | `headline=""`, `content=""`, `url=""` | `400 Bad Request` | Returns clear validation message: `"At least one input (headline, content, or URL) must be provided."` |
| **Excessively Long Input** | $>200,000$ characters | `200 OK` | Safely truncated to configured maximum length without server exhaustion. |
| **Non-Latin Input** | Pure Devanagari script (Hindi) | `200 OK` | Language service flags `language="Hindi"`, `is_ml_supported=false`, and adds warning banner. |
| **Transformer Offline** | Local Transformer checkpoint omitted | `200 OK` | Seamless fallback to source-neutral 3-model ensemble; `fallback_active=true`. |
