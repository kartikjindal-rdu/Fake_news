# VERITAS AI — REST API Specification

Base URL: `http://localhost:8000/api`

---

## Endpoints

### 1. `POST /analyze/text`
Analyzes news headline and content body.

**Request Body:**
```json
{
  "headline": "NASA James Webb Space Telescope discovers oldest known galaxy",
  "content": "Astronomers using NASA James Webb Space Telescope have identified...",
  "url": "https://www.nasa.gov"
}
```

**Response:**
```json
{
  "scanId": "VRT-A9F21D",
  "timestamp": "2026-09-08T18:30:00Z",
  "verdict": "VERIFIED REAL",
  "riskLevel": {
    "label": "LOW RISK",
    "color": "#10b981",
    "badgeBg": "bg-emerald-500/10 text-emerald-400"
  },
  "scores": {
    "fakeProbability": 5.2,
    "realProbability": 94.8,
    "aiConfidence": 97.2,
    "credibilityScore": 96.5,
    "riskScore": 8.4,
    "clickbaitScore": 0.0,
    "sensationalismScore": 0.0,
    "emotionalManipulationScore": 0.0,
    "sourceTrustScore": 95.0,
    "languageRiskScore": 0.0
  },
  "linguistic": {
    "emotionalTone": "Objective / Factual Journalism",
    "readabilityScore": 68.5,
    "readabilityLevel": "Standard Journalistic Style",
    "wordCount": 42,
    "sentenceCount": 2
  },
  "domain": {
    "name": "nasa.gov",
    "hasHttps": true,
    "trustScore": 98.0,
    "category": "National Aeronautics & Space Administration",
    "riskLevel": "LOW RISK"
  },
  "highlightedTriggers": {},
  "claims": [],
  "primaryFindings": ["Text exhibits balanced syntactic structure and objective vocabulary."],
  "recommendedAction": "Content appears relatively low-risk.",
  "factCheckUrl": "https://toolbox.google.com/factcheck/explorer/search/list:false;query:..."
}
```

---

### 2. `GET /scans`
Retrieves all historical audit records.

---

### 3. `GET /model/info`
Retrieves model architecture, accuracy, and confusion matrix parameters.

---

### 4. `GET /health`
Returns live system health and microservice status.
