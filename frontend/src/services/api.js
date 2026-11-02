import axios from 'axios';
import { RISK_LEVELS } from '../utils/constants';

const API_BASE_URL = '/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Client-side heuristic analysis engine (works standalone & as fallback)
export const performClientAnalysis = (headline, content, url = '') => {
  const combined = `${headline || ''} ${content || ''}`.trim();
  const lower = combined.toLowerCase();
  const wordCount = combined.split(/\s+/).filter(Boolean).length;
  const sentenceCount = Math.max(1, combined.split(/[.!?]+/).filter(Boolean).length);

  // 1. Clickbait Heuristics
  const clickbaitPhrases = [
    "you won't believe", "you wont believe", "will blow your mind",
    "this one trick", "what happens next", "doctors hate this",
    "shocking truth", "secret cure", "banned from tv", "before it is deleted",
    "miracle remedy", "illuminati", "urgent share", "100% guaranteed"
  ];
  let clickbaitScore = 0;
  const highlightedTriggers = {};

  clickbaitPhrases.forEach(phrase => {
    if (lower.includes(phrase)) {
      clickbaitScore += 25;
      highlightedTriggers[phrase.toUpperCase()] = "Clickbait / Viral Trigger: Designed to induce reflexive sharing rather than factual reading.";
    }
  });

  // Caps Ratio
  const capsLetters = (combined.match(/[A-Z]/g) || []).length;
  const totalLetters = (combined.match(/[a-zA-Z]/g) || []).length;
  const capsRatio = totalLetters > 0 ? capsLetters / totalLetters : 0;
  if (capsRatio > 0.35 && totalLetters > 20) {
    clickbaitScore += 30;
    highlightedTriggers["EXCESSIVE UPPERCASE"] = "Visual Emphasis Marker: Over 35% uppercase text used to manufacture excitement.";
  }

  // Punctuation Clusters (!!!, ???)
  const punctClusters = (combined.match(/[!?]{2,}/g) || []).length;
  if (punctClusters > 0) {
    clickbaitScore += Math.min(punctClusters * 15, 30);
    highlightedTriggers["DRAMATIC PUNCTUATION"] = "Punctuation Clustering: Repeated exclamation or question marks.";
  }
  clickbaitScore = Math.min(100, clickbaitScore);

  // 2. Sensationalism & Hyperbole
  const sensationalWords = [
    "shocking", "miracle", "unbelievable", "mind-blowing", "revolutionary",
    "cure-all", "catastrophic", "forbidden", "exposed", "terrifying",
    "doomsday", "apocalyptic", "magic", "conspiracy", "corrupt", "traitor"
  ];
  let sensationalismScore = 0;
  sensationalWords.forEach(w => {
    const regex = new RegExp(`\\b${w}\\b`, 'gi');
    const matches = (combined.match(regex) || []).length;
    if (matches > 0) {
      sensationalismScore += Math.min(matches * 15, 35);
      highlightedTriggers[w.toUpperCase()] = "Sensationalist Hyperbole: Word engineered to polarize emotional response.";
    }
  });
  sensationalismScore = Math.min(100, sensationalismScore);

  // 3. Emotional Manipulation & Tone
  const fearWords = ["deadly", "fatal", "toxic", "destroy", "panic", "disaster", "nightmare", "danger", "threat", "apocalypse"];
  const outrageWords = ["evil", "scandal", "disgrace", "shameful", "treason", "liar", "criminals", "theft", "tyranny", "fraud"];
  const urgencyWords = ["urgent", "immediately", "hurry", "warning", "alert", "breaking", "forward this", "act now"];

  let fearCount = 0, outrageCount = 0, urgencyCount = 0;
  fearWords.forEach(w => { if (lower.includes(w)) fearCount++; });
  outrageWords.forEach(w => { if (lower.includes(w)) outrageCount++; });
  urgencyWords.forEach(w => { if (lower.includes(w)) urgencyCount++; });

  const totalEmotion = fearCount + outrageCount + urgencyCount;
  const emotionScore = Math.min(100, totalEmotion * 18);
  let emotionalTone = "Objective / Factual Journalism";
  if (fearCount > outrageCount && fearCount > 0) emotionalTone = "Fear & Panic Induction";
  else if (outrageCount >= fearCount && outrageCount > 0) emotionalTone = "High Outrage & Aggression";
  else if (urgencyCount > 0) emotionalTone = "High Urgency / Clickbait Prompt";

  // 4. Domain Trust
  let sourceTrust = 50;
  let domainCategory = "Independent / Unregistered Domain";
  let domainName = url ? url.replace(/^(https?:\/\/)?(www\.)?/, '').split('/')[0] : '';

  if (domainName.includes('nasa.gov') || domainName.includes('who.int') || domainName.includes('nature.com') || domainName.includes('reuters.com') || domainName.includes('apnews.com')) {
    sourceTrust = 95;
    domainCategory = "Verified Authoritative News / Scientific Institution";
  } else if (domainName.includes('infowars') || domainName.includes('naturalnews') || domainName.includes('.xyz') || domainName.includes('.top') || domainName.includes('.click')) {
    sourceTrust = 15;
    domainCategory = "Cataloged Hoax / Suspicious TLD / Disinformation Outlet";
  }

  // 5. ML Fake Probability Simulation & Multi-Factor Ensemble
  const langManip = (clickbaitScore * 0.35) + (sensationalismScore * 0.35) + (emotionScore * 0.30);
  let fakeProbability = (langManip * 0.65) + ((100 - sourceTrust) * 0.35);

  if (lower.includes("nasa") || lower.includes("peer-reviewed") || lower.includes("who released") || lower.includes("clinical guidelines")) {
    fakeProbability = Math.max(4.0, fakeProbability * 0.2);
  }

  fakeProbability = Math.round(Math.max(2.0, Math.min(98.0, fakeProbability)) * 10) / 10;
  const realProbability = Math.round((100 - fakeProbability) * 10) / 10;

  // Composite Risk Score
  const riskScore = Math.round(((fakeProbability * 0.45) + (sensationalismScore * 0.20) + (clickbaitScore * 0.20) + (emotionScore * 0.15)) * 10) / 10;
  let riskLevel = RISK_LEVELS.LOW;
  if (riskScore > 75) riskLevel = RISK_LEVELS.CRITICAL;
  else if (riskScore > 50) riskLevel = RISK_LEVELS.HIGH;
  else if (riskScore > 25) riskLevel = RISK_LEVELS.MODERATE;

  // AI Confidence — heuristic estimate only, no artificial floor
  const aiConfidence = Math.round(Math.min(99.0, (Math.max(fakeProbability, realProbability) * 0.7) + (wordCount > 30 ? 25 : 15)) * 10) / 10;
  const credibilityScore = Math.round(((realProbability * 0.7) + (sourceTrust * 0.3)) * 10) / 10;

  // Verdict — offline fallback; never claim verified real without ML
  let verdict = "HEURISTIC ONLY — NOT VERIFIED";
  if (fakeProbability >= 65) verdict = "HIGH RISK (HEURISTIC)";
  else if (fakeProbability >= 45) verdict = "UNCERTAIN (HEURISTIC)";

  // Claims Extraction
  const sentences = combined.split(/(?<=[.!?])\s+/).filter(s => s.length > 20);
  const claims = sentences.slice(0, 3).map((text, idx) => ({
    id: `claim-${idx + 1}`,
    text,
    importance: idx === 0 ? "Primary Assertion" : "Supporting Claim",
    riskLevel: riskScore > 50 ? "HIGH" : (riskScore > 25 ? "MODERATE" : "LOW"),
    verificationStatus: fakeProbability > 65 ? "Conflicting Evidence" : (realProbability > 65 ? "Supported Evidence" : "Requires Verification")
  }));

  // Primary Findings
  const primaryFindings = [
    fakeProbability > 60 ? "High concentration of emotional manipulation and sensationalist assertion patterns detected." : "Text exhibits balanced syntactic structure and objective journalistic vocabulary.",
    sensationalismScore > 30 ? "Hyperbolic and unverified claims detected in main clause." : "No extreme hyperbolic language detected in primary headline.",
    url ? `Source domain '${domainName}' evaluated (${domainCategory}).` : "Text-only scan performed; source URL not specified."
  ];

  return {
    scanId: `VRT-${Math.random().toString(36).substring(2, 9).toUpperCase()}`,
    timestamp: new Date().toISOString(),
    verdict,
    riskLevel,
    scores: {
      fakeProbability,
      realProbability,
      aiConfidence,
      credibilityScore,
      riskScore,
      clickbaitScore,
      sensationalismScore,
      emotionalManipulationScore: emotionScore,
      sourceTrustScore: sourceTrust,
      languageRiskScore: Math.round(langManip * 10) / 10
    },
    linguistic: {
      emotionalTone,
      readabilityScore: 68.5,
      readabilityLevel: "Standard Journalistic Style",
      wordCount,
      sentenceCount
    },
    domain: {
      name: domainName || "Direct Input",
      hasHttps: (url || '').startsWith("https://"),
      trustScore: sourceTrust,
      category: domainCategory
    },
    highlightedTriggers,
    claims,
    primaryFindings,
    recommendedAction: riskLevel?.recommendation || "Backend is offline. This analysis uses client-side heuristics only.",
    factCheckUrl: `https://toolbox.google.com/factcheck/explorer/search/${encodeURIComponent(headline || (content || '').slice(0, 60))}?hl=en`,
    // Mark as offline fallback so the UI can render appropriately
    mlPrediction: { available: false, error: "Backend is offline. Client-side heuristics only." },
    evidence: { status: "NOT_CONFIGURED", message: "Evidence retrieval requires the backend.", items: [], note: "No evidence retrieved." },
    languageDetection: null,
    explainability: null,
  };
};

// API Methods
export const api = {
  analyzeText: async (payload) => {
    try {
      const res = await client.post('/analyze/text', payload);
      return res.data;
    } catch (e) {
      // Graceful offline local fallback
      return performClientAnalysis(payload.headline, payload.content, payload.url);
    }
  },
  analyzeUrl: async (url) => {
    try {
      const res = await client.post('/analyze/url', { url });
      return res.data;
    } catch (e) {
      return performClientAnalysis("URL Scan Analysis", `Content retrieved from ${url}`, url);
    }
  },
  getScans: async () => {
    try {
      const res = await client.get('/scans');
      const backendScans = Array.isArray(res.data) ? res.data : [];
      let saved = [];
      try {
        saved = JSON.parse(localStorage.getItem('veritas_scan_history') || '[]');
      } catch (_) {}
      
      const seen = new Set(backendScans.map(s => s.scanId));
      const combined = [...backendScans];
      for (const item of saved) {
        if (item && item.scanId && !seen.has(item.scanId)) {
          seen.add(item.scanId);
          combined.push(item);
        }
      }
      return combined;
    } catch (e) {
      // Return localStorage history
      try {
        const saved = localStorage.getItem('veritas_scan_history');
        return saved ? JSON.parse(saved) : [];
      } catch (_) {
        return [];
      }
    }
  },
  deleteScan: async (scanId) => {
    try {
      const res = await client.delete(`/scans/${scanId}`);
      return res.data;
    } catch (e) {
      return { status: "local_only", deleted: scanId };
    }
  },
  getModelInfo: async () => {
    try {
      const res = await client.get('/model/info');
      return res.data;
    } catch (e) {
      return {
        modelName: "VeriNews AI 2.0 — Three-Model Ensemble",
        version: "2.0.0",
        algorithm: "TF-IDF + Logistic Regression + Linear SVM + Random Forest",
        status: "Unavailable",
        available: false,
        metrics: null,
        metricsNote: "Backend is offline. Connect to the backend to load trained models.",
        message: "Cannot reach the backend API.",
      };
    }
  },
  getHealth: async () => {
    try {
      const res = await client.get('/health');
      return res.data;
    } catch (e) {
      return { status: "Local In-Browser Mode", mlEngine: "Client Heuristic Suite", database: "Browser IndexedStore" };
    }
  },
  getNewsFeed: async (params = {}) => {
    try {
      const res = await client.get('/news/feed', { params });
      return res.data;
    } catch (e) {
      console.warn("Could not fetch news feed from backend:", e);
      return {
        articles: [],
        total: 0,
        page: 1,
        limit: 12,
        total_pages: 1,
        sources: [],
        categories: ["World", "Health", "Science", "Technology"],
        cached: false,
        last_updated: new Date().toISOString(),
        error: e.response?.data?.detail || "Could not reach live news feed service. Please confirm the backend is running."
      };
    }
  },
  getNewsSources: async () => {
    try {
      const res = await client.get('/news/sources');
      return res.data;
    } catch (e) {
      return [];
    }
  },
  toggleNewsSource: async (sourceId, enabled) => {
    try {
      const res = await client.post(`/news/sources/${encodeURIComponent(sourceId)}/toggle`, { enabled });
      return res.data;
    } catch (e) {
      throw new Error(e.response?.data?.detail || "Failed to update source state.");
    }
  },
  addNewsSource: async (sourceData) => {
    try {
      const res = await client.post('/news/sources/add', sourceData);
      return res.data;
    } catch (e) {
      throw new Error(e.response?.data?.detail || "Failed to add source endpoint.");
    }
  },
  getYoutubeTranscript: async (videoId) => {
    try {
      const res = await client.post('/news/youtube/transcript', { video_id: videoId });
      return res.data;
    } catch (e) {
      return {
        video_id: videoId,
        has_transcript: false,
        note: "Failed to query YouTube transcript API."
      };
    }
  },
  fetchArticleContent: async (url) => {
    try {
      const res = await client.post('/news/fetch-article', { url });
      return res.data;
    } catch (e) {
      return {
        url,
        has_full_text: false,
        note: "Failed to extract full article text from publisher."
      };
    }
  },
  verifyClaim: async (claim) => {
    try {
      const res = await client.post('/claims/verify', { claim });
      return res.data;
    } catch (e) {
      return {
        claim,
        status: "INSUFFICIENT_EVIDENCE",
        status_label: "Backend Offline or No Evidence Found",
        explanation: "Could not query external open evidence sources. Please ensure backend is running.",
        evidence_sources: [],
        sources_count: 0,
        retrieved_at: new Date().toISOString(),
        limitations_disclaimer: "Offline fallback mode: external evidence search unavailable."
      };
    }
  },
  extractClaims: async (text, maxClaims = 5) => {
    try {
      const res = await client.post('/claims/extract', { text, max_claims: maxClaims });
      return res.data;
    } catch (e) {
      // Simple client-side fallback claim extraction
      const sentences = text.split(/(?<=[.!?])\s+/).filter(s => s.length > 25);
      return {
        text_length: text.length,
        claims_extracted: Math.min(sentences.length, maxClaims),
        claims: sentences.slice(0, maxClaims).map((s, idx) => ({
          id: `C-${101 + idx}`,
          claim: s,
          importance: "Primary Statement",
          status: "UNVERIFIED",
          evidence_sources: []
        }))
      };
    }
  },
  getModelDiagnostics: async () => {
    try {
      const res = await client.post('/model/diagnostics');
      return res.data;
    } catch (e) {
      return {
        status: "FAIL",
        available: false,
        error: "Backend diagnostic endpoint unreachable.",
        elapsed_ms: 0
      };
    }
  },
  getNewsTimeline: async (q = "election OR health", limit = 15) => {
    try {
      const res = await client.get('/news/timeline', { params: { q, limit } });
      return res.data;
    } catch (e) {
      return {
        query: q,
        total_articles: 0,
        publishers_count: 0,
        publishers: [],
        has_syndication: false,
        syndication_summary: "Timeline service unavailable in offline fallback mode.",
        timeline: []
      };
    }
  },
  // VeriNews AI 3.0: AI Research Agent & Graph Endpoints
  conductResearch: async (payload) => {
    try {
      const res = await client.post('/claims/research', payload);
      return res.data;
    } catch (e) {
      throw new Error(e.response?.data?.detail || "Research agent investigation failed.");
    }
  },
  generateClaimGraph: async (investigation) => {
    try {
      const res = await client.post('/claims/graph', { investigation });
      return res.data;
    } catch (e) {
      return {
        investigation_id: null,
        nodes: [],
        edges: [],
        is_empty: true,
        message: "Graph generation unavailable."
      };
    }
  },
  searchFactChecks: async (claim, maxResults = 5) => {
    try {
      const res = await client.post('/claims/factcheck', { claim, max_results: maxResults });
      return res.data;
    } catch (e) {
      return {
        query: claim,
        matches_found: 0,
        status: "NO_MATCHES_FOUND",
        message: "Fact-check query offline fallback.",
        results: []
      };
    }
  },
  getModelDrift: async () => {
    try {
      const res = await client.get('/model/drift');
      return res.data;
    } catch (e) {
      return {
        drift_status: "UNAVAILABLE",
        drift_level: "Telemetry Offline",
        psi_score: 0.0,
        live_telemetry: {
          total_inferences: 0,
          fake_rate_percentage: 50.0,
          real_rate_percentage: 50.0,
          disagreement_rate_percentage: 0.0,
          average_latency_ms: 0.0
        }
      };
    }
  },
  resetModelDrift: async () => {
    try {
      const res = await client.post('/model/drift/reset');
      return res.data;
    } catch (e) {
      return { status: "ERROR", message: "Failed to reset telemetry." };
    }
  },
  getExportReportUrl: (scanId) => {
    return `/api/export/${scanId}/export`;
  }
};
