package com.veritasai.model;

import com.veritasai.util.Constants.RiskLevel;
import java.util.ArrayList;
import java.util.List;

/**
 * Encapsulates the heuristic domain inspection details.
 */
public class DomainAnalysis {

    private String domainName;
    private boolean hasHttps;
    private String urlStructure;
    private int domainLength;
    private int subdomainCount;
    private double sourceTrustScore; // 0 - 100
    private RiskLevel riskLevel;
    private String editorialCategory;
    private List<String> suspiciousIndicators;
    private String assessmentSummary;

    public DomainAnalysis(String domainName) {
        this.domainName = (domainName != null) ? domainName.toLowerCase().trim() : "";
        this.suspiciousIndicators = new ArrayList<>();
        this.riskLevel = RiskLevel.LOW;
        this.sourceTrustScore = 50.0;
        this.editorialCategory = "Unverified Domain";
        this.assessmentSummary = "Domain evaluated with heuristic indicators.";
    }

    public String getDomainName() { return domainName; }
    public void setDomainName(String domainName) { this.domainName = domainName; }

    public boolean isHasHttps() { return hasHttps; }
    public void setHasHttps(boolean hasHttps) { this.hasHttps = hasHttps; }

    public String getUrlStructure() { return urlStructure; }
    public void setUrlStructure(String urlStructure) { this.urlStructure = urlStructure; }

    public int getDomainLength() { return domainLength; }
    public void setDomainLength(int domainLength) { this.domainLength = domainLength; }

    public int getSubdomainCount() { return subdomainCount; }
    public void setSubdomainCount(int subdomainCount) { this.subdomainCount = subdomainCount; }

    public double getSourceTrustScore() { return sourceTrustScore; }
    public void setSourceTrustScore(double sourceTrustScore) { this.sourceTrustScore = sourceTrustScore; }

    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }

    public String getEditorialCategory() { return editorialCategory; }
    public void setEditorialCategory(String editorialCategory) { this.editorialCategory = editorialCategory; }

    public List<String> getSuspiciousIndicators() { return suspiciousIndicators; }
    public void addSuspiciousIndicator(String indicator) { this.suspiciousIndicators.add(indicator); }

    public String getAssessmentSummary() { return assessmentSummary; }
    public void setAssessmentSummary(String assessmentSummary) { this.assessmentSummary = assessmentSummary; }
}
