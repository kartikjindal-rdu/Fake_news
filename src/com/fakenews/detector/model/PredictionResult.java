package com.fakenews.detector.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Encapsulates the rich multi-factor output of the Fake News AI detection engine.
 */
public class PredictionResult {

    public enum Verdict {
        REAL("Verified Credible News", "#10b981"),
        FAKE("High Probability Fake / Misinformation", "#ef4444"),
        SUSPICIOUS("Suspicious / Unverified Claims", "#f59e0b"),
        SATIRE("Satire / Parody Detected", "#8b5cf6");

        private final String label;
        private final String colorHex;

        Verdict(String label, String colorHex) {
            this.label = label;
            this.colorHex = colorHex;
        }

        public String getLabel() {
            return label;
        }

        public String getColorHex() {
            return colorHex;
        }
    }

    private Verdict verdict;
    private double fakeProbability;        // 0.0 to 100.0%
    private double realProbability;        // 0.0 to 100.0%
    private double confidenceScore;        // 0.0 to 100.0%
    private double sensationalismScore;    // 0.0 to 100.0%
    private double clickbaitScore;         // 0.0 to 100.0%
    private double emotionalBiasScore;     // 0.0 to 100.0%
    private String emotionalTone;          // "High Urgency / Fear", "Aggressive / Outrage", "Neutral / Objective"
    private double readabilityScore;       // 0 to 100 (Flesch score)
    private String readabilityLevel;       // "Standard Journalistic", "Low Complexity / Simple", etc.
    private int wordCount;
    private int sentenceCount;
    private DomainReputation domainReputation;
    private List<String> flaggedKeywords;
    private List<String> insights;
    private String factCheckQueryUrl;

    public PredictionResult() {
        this.flaggedKeywords = new ArrayList<>();
        this.insights = new ArrayList<>();
        this.emotionalTone = "Neutral";
        this.readabilityLevel = "Standard";
    }

    public Verdict getVerdict() {
        return verdict;
    }

    public void setVerdict(Verdict verdict) {
        this.verdict = verdict;
    }

    public double getFakeProbability() {
        return fakeProbability;
    }

    public void setFakeProbability(double fakeProbability) {
        this.fakeProbability = fakeProbability;
    }

    public double getRealProbability() {
        return realProbability;
    }

    public void setRealProbability(double realProbability) {
        this.realProbability = realProbability;
    }

    public double getConfidenceScore() {
        return confidenceScore;
    }

    public void setConfidenceScore(double confidenceScore) {
        this.confidenceScore = confidenceScore;
    }

    public double getSensationalismScore() {
        return sensationalismScore;
    }

    public void setSensationalismScore(double sensationalismScore) {
        this.sensationalismScore = sensationalismScore;
    }

    public double getClickbaitScore() {
        return clickbaitScore;
    }

    public void setClickbaitScore(double clickbaitScore) {
        this.clickbaitScore = clickbaitScore;
    }

    public double getEmotionalBiasScore() {
        return emotionalBiasScore;
    }

    public void setEmotionalBiasScore(double emotionalBiasScore) {
        this.emotionalBiasScore = emotionalBiasScore;
    }

    public String getEmotionalTone() {
        return emotionalTone;
    }

    public void setEmotionalTone(String emotionalTone) {
        this.emotionalTone = emotionalTone;
    }

    public double getReadabilityScore() {
        return readabilityScore;
    }

    public void setReadabilityScore(double readabilityScore) {
        this.readabilityScore = readabilityScore;
    }

    public String getReadabilityLevel() {
        return readabilityLevel;
    }

    public void setReadabilityLevel(String readabilityLevel) {
        this.readabilityLevel = readabilityLevel;
    }

    public int getWordCount() {
        return wordCount;
    }

    public void setWordCount(int wordCount) {
        this.wordCount = wordCount;
    }

    public int getSentenceCount() {
        return sentenceCount;
    }

    public void setSentenceCount(int sentenceCount) {
        this.sentenceCount = sentenceCount;
    }

    public DomainReputation getDomainReputation() {
        return domainReputation;
    }

    public void setDomainReputation(DomainReputation domainReputation) {
        this.domainReputation = domainReputation;
    }

    public List<String> getFlaggedKeywords() {
        return flaggedKeywords;
    }

    public void setFlaggedKeywords(List<String> flaggedKeywords) {
        this.flaggedKeywords = flaggedKeywords;
    }

    public void addFlaggedKeyword(String keyword) {
        if (!flaggedKeywords.contains(keyword)) {
            flaggedKeywords.add(keyword);
        }
    }

    public List<String> getInsights() {
        return insights;
    }

    public void setInsights(List<String> insights) {
        this.insights = insights;
    }

    public void addInsight(String insight) {
        this.insights.add(insight);
    }

    public String getFactCheckQueryUrl() {
        return factCheckQueryUrl;
    }

    public void setFactCheckQueryUrl(String factCheckQueryUrl) {
        this.factCheckQueryUrl = factCheckQueryUrl;
    }

    /**
     * Serializes result to a clean JSON string for REST APIs and Mobile Apps.
     */
    public String toJson() {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        sb.append("  \"verdict\": \"").append(verdict != null ? verdict.name() : "UNKNOWN").append("\",\n");
        sb.append("  \"confidence\": ").append(confidenceScore).append(",\n");
        sb.append("  \"realProbability\": ").append(realProbability).append(",\n");
        sb.append("  \"fakeProbability\": ").append(fakeProbability).append(",\n");
        sb.append("  \"sensationalismScore\": ").append(sensationalismScore).append(",\n");
        sb.append("  \"clickbaitScore\": ").append(clickbaitScore).append(",\n");
        sb.append("  \"emotionalBiasScore\": ").append(emotionalBiasScore).append(",\n");
        sb.append("  \"emotionalTone\": \"").append(emotionalTone).append("\",\n");
        sb.append("  \"readability\": {\n");
        sb.append("    \"score\": ").append(readabilityScore).append(",\n");
        sb.append("    \"level\": \"").append(readabilityLevel).append("\",\n");
        sb.append("    \"wordCount\": ").append(wordCount).append(",\n");
        sb.append("    \"sentenceCount\": ").append(sentenceCount).append("\n");
        sb.append("  },\n");
        sb.append("  \"domainTrust\": \"").append(domainReputation != null ? domainReputation.getTrustLevel().name() : "NONE").append("\",\n");
        sb.append("  \"flaggedKeywords\": [");
        for (int i = 0; i < flaggedKeywords.size(); i++) {
            sb.append("\"").append(flaggedKeywords.get(i).replace("\"", "\\\"")).append("\"");
            if (i < flaggedKeywords.size() - 1) sb.append(", ");
        }
        sb.append("],\n");
        sb.append("  \"insights\": [");
        for (int i = 0; i < insights.size(); i++) {
            sb.append("\"").append(insights.get(i).replace("\"", "\\\"")).append("\"");
            if (i < insights.size() - 1) sb.append(", ");
        }
        sb.append("]\n");
        sb.append("}");
        return sb.toString();
    }
}
