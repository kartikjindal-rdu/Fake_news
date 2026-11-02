package com.fakenews.detector.model;

import java.text.SimpleDateFormat;
import java.util.*;

/**
 * Encapsulates a complete persistent scan audit record for VERITAS AI.
 * Contains all 22 forensic metrics, cryptographic fingerprint, and detailed reports.
 */
public class HistoryRecord {

    private String scanId;
    private String timestamp;
    private String sourceUrl;
    private String domain;
    private String headline;
    private String articleText;
    private String finalRiskLevel; // LOW, MODERATE, HIGH, CRITICAL
    private double riskScore;
    private double analysisConfidence;
    private double clickbaitScore;
    private double sensationalismScore;
    private double emotionalScore;
    private double urgencyScore;
    private double languageManipulationScore;
    private double domainRiskScore;
    private double headlineConsistencyScore;
    private String writingStyle;
    private String readabilityLevel;
    private List<String> detectedSignals;
    private List<String> trustSignals;
    private String contentFingerprint;
    private String forensicExplanation;
    private String rawJsonPayload;

    public HistoryRecord() {
        this.timestamp = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ssXXX").format(new Date());
        this.detectedSignals = new ArrayList<>();
        this.trustSignals = new ArrayList<>();
    }

    public HistoryRecord(String scanId, String sourceUrl, String domain, String headline, String articleText,
                         String finalRiskLevel, double riskScore, double analysisConfidence,
                         double clickbaitScore, double sensationalismScore, double emotionalScore,
                         double urgencyScore, double languageManipulationScore, double domainRiskScore,
                         double headlineConsistencyScore, String writingStyle, String readabilityLevel,
                         List<String> detectedSignals, List<String> trustSignals, String contentFingerprint,
                         String forensicExplanation) {
        this();
        this.scanId = scanId;
        this.sourceUrl = (sourceUrl != null) ? sourceUrl : "";
        this.domain = (domain != null && !domain.isEmpty()) ? domain : (sourceUrl != null && sourceUrl.contains("://") ? sourceUrl.split("://")[1].split("/")[0] : "Direct Input");
        this.headline = (headline != null && !headline.trim().isEmpty()) ? headline : (articleText != null && articleText.length() > 60 ? articleText.substring(0, 60) + "..." : "Untitled Scan");
        this.articleText = (articleText != null) ? articleText : "";
        this.finalRiskLevel = (finalRiskLevel != null) ? finalRiskLevel : "LOW";
        this.riskScore = riskScore;
        this.analysisConfidence = analysisConfidence;
        this.clickbaitScore = clickbaitScore;
        this.sensationalismScore = sensationalismScore;
        this.emotionalScore = emotionalScore;
        this.urgencyScore = urgencyScore;
        this.languageManipulationScore = languageManipulationScore;
        this.domainRiskScore = domainRiskScore;
        this.headlineConsistencyScore = headlineConsistencyScore;
        this.writingStyle = (writingStyle != null) ? writingStyle : "Neutral";
        this.readabilityLevel = (readabilityLevel != null) ? readabilityLevel : "Standard";
        this.detectedSignals = (detectedSignals != null) ? detectedSignals : new ArrayList<>();
        this.trustSignals = (trustSignals != null) ? trustSignals : new ArrayList<>();
        this.contentFingerprint = (contentFingerprint != null) ? contentFingerprint : "";
        this.forensicExplanation = (forensicExplanation != null) ? forensicExplanation : "";
    }

    // Backward compatibility constructor
    public HistoryRecord(String id, String title, String sourceUrl, String verdict,
                         double confidenceScore, double fakeProbability, double realProbability) {
        this();
        this.scanId = id;
        this.headline = title;
        this.sourceUrl = sourceUrl;
        this.domain = sourceUrl != null && sourceUrl.contains("://") ? sourceUrl.split("://")[1].split("/")[0] : "Direct Input";
        this.finalRiskLevel = fakeProbability > 65 ? "HIGH" : (fakeProbability > 35 ? "MODERATE" : "LOW");
        this.riskScore = fakeProbability;
        this.analysisConfidence = confidenceScore;
    }

    public String getId() {
        return scanId;
    }

    public String getScanId() {
        return scanId;
    }

    public void setScanId(String scanId) {
        this.scanId = scanId;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public String getSourceUrl() {
        return sourceUrl;
    }

    public void setSourceUrl(String sourceUrl) {
        this.sourceUrl = sourceUrl;
    }

    public String getDomain() {
        return domain;
    }

    public void setDomain(String domain) {
        this.domain = domain;
    }

    public String getHeadline() {
        return headline;
    }

    public void setHeadline(String headline) {
        this.headline = headline;
    }

    public String getTitle() {
        return headline;
    }

    public String getArticleText() {
        return articleText;
    }

    public void setArticleText(String articleText) {
        this.articleText = articleText;
    }

    public String getFinalRiskLevel() {
        return finalRiskLevel;
    }

    public void setFinalRiskLevel(String finalRiskLevel) {
        this.finalRiskLevel = finalRiskLevel;
    }

    public String getVerdict() {
        return finalRiskLevel;
    }

    public double getRiskScore() {
        return riskScore;
    }

    public void setRiskScore(double riskScore) {
        this.riskScore = riskScore;
    }

    public double getAnalysisConfidence() {
        return analysisConfidence;
    }

    public double getConfidenceScore() {
        return analysisConfidence;
    }

    public void setAnalysisConfidence(double analysisConfidence) {
        this.analysisConfidence = analysisConfidence;
    }

    public double getClickbaitScore() {
        return clickbaitScore;
    }

    public void setClickbaitScore(double clickbaitScore) {
        this.clickbaitScore = clickbaitScore;
    }

    public double getSensationalismScore() {
        return sensationalismScore;
    }

    public void setSensationalismScore(double sensationalismScore) {
        this.sensationalismScore = sensationalismScore;
    }

    public double getEmotionalScore() {
        return emotionalScore;
    }

    public void setEmotionalScore(double emotionalScore) {
        this.emotionalScore = emotionalScore;
    }

    public double getUrgencyScore() {
        return urgencyScore;
    }

    public void setUrgencyScore(double urgencyScore) {
        this.urgencyScore = urgencyScore;
    }

    public double getLanguageManipulationScore() {
        return languageManipulationScore;
    }

    public void setLanguageManipulationScore(double languageManipulationScore) {
        this.languageManipulationScore = languageManipulationScore;
    }

    public double getDomainRiskScore() {
        return domainRiskScore;
    }

    public void setDomainRiskScore(double domainRiskScore) {
        this.domainRiskScore = domainRiskScore;
    }

    public double getHeadlineConsistencyScore() {
        return headlineConsistencyScore;
    }

    public void setHeadlineConsistencyScore(double headlineConsistencyScore) {
        this.headlineConsistencyScore = headlineConsistencyScore;
    }

    public String getWritingStyle() {
        return writingStyle;
    }

    public void setWritingStyle(String writingStyle) {
        this.writingStyle = writingStyle;
    }

    public String getReadabilityLevel() {
        return readabilityLevel;
    }

    public void setReadabilityLevel(String readabilityLevel) {
        this.readabilityLevel = readabilityLevel;
    }

    public List<String> getDetectedSignals() {
        return detectedSignals;
    }

    public void setDetectedSignals(List<String> detectedSignals) {
        this.detectedSignals = detectedSignals;
    }

    public List<String> getTrustSignals() {
        return trustSignals;
    }

    public void setTrustSignals(List<String> trustSignals) {
        this.trustSignals = trustSignals;
    }

    public String getContentFingerprint() {
        return contentFingerprint;
    }

    public void setContentFingerprint(String contentFingerprint) {
        this.contentFingerprint = contentFingerprint;
    }

    public String getForensicExplanation() {
        return forensicExplanation;
    }

    public void setForensicExplanation(String forensicExplanation) {
        this.forensicExplanation = forensicExplanation;
    }

    public String getRawJsonPayload() {
        return rawJsonPayload;
    }

    public void setRawJsonPayload(String rawJsonPayload) {
        this.rawJsonPayload = rawJsonPayload;
    }

    public double getFakeProbability() {
        return riskScore;
    }

    public double getRealProbability() {
        return Math.max(0.0, 100.0 - riskScore);
    }

    public String toCsvLine() {
        return String.format("\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%.1f,%.1f,\"%s\",\"%s\",\"%s\"",
                scanId,
                timestamp,
                (headline != null ? headline.replace("\"", "\"\"") : ""),
                (domain != null ? domain.replace("\"", "\"\"") : ""),
                (sourceUrl != null ? sourceUrl.replace("\"", "\"\"") : ""),
                finalRiskLevel,
                riskScore,
                analysisConfidence,
                writingStyle,
                readabilityLevel,
                contentFingerprint);
    }

    public String toJson() {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        sb.append("\"scanId\":\"").append(escape(scanId)).append("\",");
        sb.append("\"timestamp\":\"").append(escape(timestamp)).append("\",");
        sb.append("\"sourceUrl\":\"").append(escape(sourceUrl)).append("\",");
        sb.append("\"domain\":\"").append(escape(domain)).append("\",");
        sb.append("\"headline\":\"").append(escape(headline)).append("\",");
        sb.append("\"articleText\":\"").append(escape(articleText)).append("\",");
        sb.append("\"finalRiskLevel\":\"").append(escape(finalRiskLevel)).append("\",");
        sb.append("\"riskScore\":").append(String.format(Locale.US, "%.1f", riskScore)).append(",");
        sb.append("\"analysisConfidence\":").append(String.format(Locale.US, "%.1f", analysisConfidence)).append(",");
        sb.append("\"clickbaitScore\":").append(String.format(Locale.US, "%.1f", clickbaitScore)).append(",");
        sb.append("\"sensationalismScore\":").append(String.format(Locale.US, "%.1f", sensationalismScore)).append(",");
        sb.append("\"emotionalScore\":").append(String.format(Locale.US, "%.1f", emotionalScore)).append(",");
        sb.append("\"urgencyScore\":").append(String.format(Locale.US, "%.1f", urgencyScore)).append(",");
        sb.append("\"languageManipulationScore\":").append(String.format(Locale.US, "%.1f", languageManipulationScore)).append(",");
        sb.append("\"domainRiskScore\":").append(String.format(Locale.US, "%.1f", domainRiskScore)).append(",");
        sb.append("\"headlineConsistencyScore\":").append(String.format(Locale.US, "%.1f", headlineConsistencyScore)).append(",");
        sb.append("\"writingStyle\":\"").append(escape(writingStyle)).append("\",");
        sb.append("\"readabilityLevel\":\"").append(escape(readabilityLevel)).append("\",");
        sb.append("\"contentFingerprint\":\"").append(escape(contentFingerprint)).append("\",");
        sb.append("\"forensicExplanation\":\"").append(escape(forensicExplanation)).append("\",");
        
        sb.append("\"detectedSignals\":[");
        for (int i = 0; i < detectedSignals.size(); i++) {
            sb.append("\"").append(escape(detectedSignals.get(i))).append("\"");
            if (i < detectedSignals.size() - 1) sb.append(",");
        }
        sb.append("],");

        sb.append("\"trustSignals\":[");
        for (int i = 0; i < trustSignals.size(); i++) {
            sb.append("\"").append(escape(trustSignals.get(i))).append("\"");
            if (i < trustSignals.size() - 1) sb.append(",");
        }
        sb.append("]");

        if (rawJsonPayload != null && !rawJsonPayload.trim().isEmpty()) {
            sb.append(",\"rawDetails\":").append(rawJsonPayload);
        }

        sb.append("}");
        return sb.toString();
    }

    private static String escape(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t");
    }
}
