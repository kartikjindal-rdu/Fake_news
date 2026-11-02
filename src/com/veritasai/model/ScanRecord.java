package com.veritasai.model;

/**
 * Entity representing a persisted scan record in database and audit history.
 */
public class ScanRecord {

    private String scanId;
    private String timestamp;
    private String headline;
    private String sourceDomain;
    private String prediction;
    private double fakeProbability;
    private double riskScore;
    private String userNotes;

    public ScanRecord(String scanId, String timestamp, String headline, String sourceDomain,
                      String prediction, double fakeProbability, double riskScore, String userNotes) {
        this.scanId = scanId;
        this.timestamp = timestamp;
        this.headline = headline;
        this.sourceDomain = sourceDomain;
        this.prediction = prediction;
        this.fakeProbability = fakeProbability;
        this.riskScore = riskScore;
        this.userNotes = (userNotes != null) ? userNotes : "";
    }

    public String getScanId() { return scanId; }
    public String getTimestamp() { return timestamp; }
    public String getHeadline() { return headline; }
    public String getSourceDomain() { return sourceDomain; }
    public String getPrediction() { return prediction; }
    public double getFakeProbability() { return fakeProbability; }
    public double getRiskScore() { return riskScore; }
    public String getUserNotes() { return userNotes; }
    public void setUserNotes(String userNotes) { this.userNotes = userNotes; }

    public String toCsvRow() {
        return String.format("\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%.1f,%.1f,\"%s\"",
                scanId, timestamp,
                headline.replace("\"", "\"\""),
                sourceDomain.replace("\"", "\"\""),
                prediction, fakeProbability, riskScore,
                userNotes.replace("\"", "\"\""));
    }
}
