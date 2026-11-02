package com.veritasai.model;

import com.veritasai.util.Constants.RiskLevel;

/**
 * Represents a key factual claim extracted from news text.
 */
public class Claim {

    public enum VerificationStatus {
        NOT_VERIFIED("Not Verified", "#64748b"),
        REQUIRES_VERIFICATION("Requires Verification", "#f59e0b"),
        SUPPORTED_EVIDENCE("Supported by Evidence", "#10b981"),
        CONFLICTING_EVIDENCE("Conflicting Evidence Found", "#ef4444");

        private final String label;
        private final String colorHex;

        VerificationStatus(String label, String colorHex) {
            this.label = label;
            this.colorHex = colorHex;
        }

        public String getLabel() { return label; }
        public String getColorHex() { return colorHex; }
    }

    private String text;
    private RiskLevel riskLevel;
    private VerificationStatus verificationStatus;
    private String rationale;

    public Claim(String text, RiskLevel riskLevel, VerificationStatus verificationStatus, String rationale) {
        this.text = text;
        this.riskLevel = riskLevel;
        this.verificationStatus = verificationStatus;
        this.rationale = rationale;
    }

    public String getText() { return text; }
    public RiskLevel getRiskLevel() { return riskLevel; }
    public VerificationStatus getVerificationStatus() { return verificationStatus; }
    public String getRationale() { return rationale; }
}
