package com.veritasai.model;

import com.veritasai.util.Constants.RiskLevel;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Encapsulates the complete 10-factor scoring breakdown, claims matrix,
 * structured explainability rationale, and serialized output.
 */
public class NewsAnalysisResult {

    public enum PredictionVerdict {
        VERIFIED_REAL("VERIFIED REAL", "#10b981"),
        LIKELY_FAKE("LIKELY FAKE / MISINFORMATION", "#ef4444"),
        SUSPICIOUS("SUSPICIOUS / UNVERIFIED", "#f59e0b"),
        SATIRE("SATIRE / PARODY", "#8b5cf6");

        private final String label;
        private final String colorHex;

        PredictionVerdict(String label, String colorHex) {
            this.label = label;
            this.colorHex = colorHex;
        }

        public String getLabel() { return label; }
        public String getColorHex() { return colorHex; }
    }

    private String scanId;
    private String timestamp;
    private PredictionVerdict verdict;
    private RiskLevel riskLevel;

    // 10 Core Scoring Metrics (0.0 to 100.0)
    private double fakeProbability;
    private double realProbability;
    private double aiConfidence;
    private double credibilityScore;
    private double riskScore;
    private double clickbaitScore;
    private double sensationalismScore;
    private double emotionalManipulationScore;
    private double sourceTrustScore;
    private double languageManipulationScore;

    // Linguistic Metadata
    private String emotionalTone;
    private double readabilityScore;
    private String readabilityLevel;
    private int wordCount;
    private int sentenceCount;

    // Rich Structure
    private DomainAnalysis domainAnalysis;
    private List<Claim> extractedClaims;
    private Map<String, String> highlightedTriggers; // word -> reason
    private List<String> primaryFindings;
    private List<String> suspiciousLanguageNotes;
    private List<String> sourceAnalysisNotes;
    private String recommendedAction;
    private String factCheckQueryUrl;

    public NewsAnalysisResult() {
        this.extractedClaims = new ArrayList<>();
        this.highlightedTriggers = new HashMap<>();
        this.primaryFindings = new ArrayList<>();
        this.suspiciousLanguageNotes = new ArrayList<>();
        this.sourceAnalysisNotes = new ArrayList<>();
        this.emotionalTone = "Neutral / Objective";
        this.readabilityLevel = "Standard Journalistic Style";
        this.riskLevel = RiskLevel.LOW;
        this.verdict = PredictionVerdict.VERIFIED_REAL;
    }

    // Getters and Setters
    public String getScanId() { return scanId; }
    public void setScanId(String scanId) { this.scanId = scanId; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public PredictionVerdict getVerdict() { return verdict; }
    public void setVerdict(PredictionVerdict verdict) { this.verdict = verdict; }

    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }

    public double getFakeProbability() { return fakeProbability; }
    public void setFakeProbability(double fakeProbability) { this.fakeProbability = fakeProbability; }

    public double getRealProbability() { return realProbability; }
    public void setRealProbability(double realProbability) { this.realProbability = realProbability; }

    public double getAiConfidence() { return aiConfidence; }
    public void setAiConfidence(double aiConfidence) { this.aiConfidence = aiConfidence; }

    public double getCredibilityScore() { return credibilityScore; }
    public void setCredibilityScore(double credibilityScore) { this.credibilityScore = credibilityScore; }

    public double getRiskScore() { return riskScore; }
    public void setRiskScore(double riskScore) { this.riskScore = riskScore; }

    public double getClickbaitScore() { return clickbaitScore; }
    public void setClickbaitScore(double clickbaitScore) { this.clickbaitScore = clickbaitScore; }

    public double getSensationalismScore() { return sensationalismScore; }
    public void setSensationalismScore(double sensationalismScore) { this.sensationalismScore = sensationalismScore; }

    public double getEmotionalManipulationScore() { return emotionalManipulationScore; }
    public void setEmotionalManipulationScore(double emotionalManipulationScore) { this.emotionalManipulationScore = emotionalManipulationScore; }

    public double getSourceTrustScore() { return sourceTrustScore; }
    public void setSourceTrustScore(double sourceTrustScore) { this.sourceTrustScore = sourceTrustScore; }

    public double getLanguageManipulationScore() { return languageManipulationScore; }
    public void setLanguageManipulationScore(double languageManipulationScore) { this.languageManipulationScore = languageManipulationScore; }

    public String getEmotionalTone() { return emotionalTone; }
    public void setEmotionalTone(String emotionalTone) { this.emotionalTone = emotionalTone; }

    public double getReadabilityScore() { return readabilityScore; }
    public void setReadabilityScore(double readabilityScore) { this.readabilityScore = readabilityScore; }

    public String getReadabilityLevel() { return readabilityLevel; }
    public void setReadabilityLevel(String readabilityLevel) { this.readabilityLevel = readabilityLevel; }

    public int getWordCount() { return wordCount; }
    public void setWordCount(int wordCount) { this.wordCount = wordCount; }

    public int getSentenceCount() { return sentenceCount; }
    public void setSentenceCount(int sentenceCount) { this.sentenceCount = sentenceCount; }

    public DomainAnalysis getDomainAnalysis() { return domainAnalysis; }
    public void setDomainAnalysis(DomainAnalysis domainAnalysis) { this.domainAnalysis = domainAnalysis; }

    public List<Claim> getExtractedClaims() { return extractedClaims; }
    public void addClaim(Claim claim) { this.extractedClaims.add(claim); }

    public Map<String, String> getHighlightedTriggers() { return highlightedTriggers; }
    public void addHighlightedTrigger(String trigger, String reason) { this.highlightedTriggers.put(trigger, reason); }

    public List<String> getPrimaryFindings() { return primaryFindings; }
    public void addPrimaryFinding(String finding) { this.primaryFindings.add(finding); }

    public List<String> getSuspiciousLanguageNotes() { return suspiciousLanguageNotes; }
    public void addSuspiciousLanguageNote(String note) { this.suspiciousLanguageNotes.add(note); }

    public List<String> getSourceAnalysisNotes() { return sourceAnalysisNotes; }
    public void addSourceAnalysisNote(String note) { this.sourceAnalysisNotes.add(note); }

    public String getRecommendedAction() { return recommendedAction; }
    public void setRecommendedAction(String recommendedAction) { this.recommendedAction = recommendedAction; }

    public String getFactCheckQueryUrl() { return factCheckQueryUrl; }
    public void setFactCheckQueryUrl(String factCheckQueryUrl) { this.factCheckQueryUrl = factCheckQueryUrl; }

    public String toJson() {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        sb.append("  \"scanId\": \"").append(scanId).append("\",\n");
        sb.append("  \"timestamp\": \"").append(timestamp).append("\",\n");
        sb.append("  \"verdict\": \"").append(verdict.name()).append("\",\n");
        sb.append("  \"riskLevel\": \"").append(riskLevel.name()).append("\",\n");
        sb.append("  \"scores\": {\n");
        sb.append("    \"fakeProbability\": ").append(fakeProbability).append(",\n");
        sb.append("    \"realProbability\": ").append(realProbability).append(",\n");
        sb.append("    \"aiConfidence\": ").append(aiConfidence).append(",\n");
        sb.append("    \"credibilityScore\": ").append(credibilityScore).append(",\n");
        sb.append("    \"riskScore\": ").append(riskScore).append(",\n");
        sb.append("    \"clickbaitScore\": ").append(clickbaitScore).append(",\n");
        sb.append("    \"sensationalismScore\": ").append(sensationalismScore).append(",\n");
        sb.append("    \"emotionalManipulationScore\": ").append(emotionalManipulationScore).append(",\n");
        sb.append("    \"sourceTrustScore\": ").append(sourceTrustScore).append(",\n");
        sb.append("    \"languageManipulationScore\": ").append(languageManipulationScore).append("\n");
        sb.append("  },\n");
        sb.append("  \"linguistic\": {\n");
        sb.append("    \"tone\": \"").append(emotionalTone).append("\",\n");
        sb.append("    \"readabilityScore\": ").append(readabilityScore).append(",\n");
        sb.append("    \"readabilityLevel\": \"").append(readabilityLevel).append("\",\n");
        sb.append("    \"wordCount\": ").append(wordCount).append(",\n");
        sb.append("    \"sentenceCount\": ").append(sentenceCount).append("\n");
        sb.append("  },\n");
        sb.append("  \"recommendation\": \"").append(recommendedAction != null ? recommendedAction.replace("\"", "\\\"") : "").append("\"\n");
        sb.append("}");
        return sb.toString();
    }
}
