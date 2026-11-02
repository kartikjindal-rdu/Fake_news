package com.fakenews.detector.model;

/**
 * Represents the reputation classification of a news website domain.
 */
public class DomainReputation {

    public enum TrustLevel {
        HIGHLY_TRUSTED("Verified & Authoritative Source", "#10b981"),
        GENERALLY_RELIABLE("Established Media Outlet", "#3b82f6"),
        QUESTIONABLE("Mixed Reliability / Sensationalist", "#f59e0b"),
        UNRELIABLE_OR_HOAX("Flagged Fake / Satire / Propaganda", "#ef4444"),
        UNKNOWN_DOMAIN("Unverified Domain (Exercise Caution)", "#64748b");

        private final String description;
        private final String colorHex;

        TrustLevel(String description, String colorHex) {
            this.description = description;
            this.colorHex = colorHex;
        }

        public String getDescription() {
            return description;
        }

        public String getColorHex() {
            return colorHex;
        }
    }

    private String domain;
    private TrustLevel trustLevel;
    private String category;
    private String notes;

    public DomainReputation(String domain, TrustLevel trustLevel, String category, String notes) {
        this.domain = (domain != null) ? domain.toLowerCase().trim() : "";
        this.trustLevel = trustLevel;
        this.category = category;
        this.notes = notes;
    }

    public String getDomain() {
        return domain;
    }

    public TrustLevel getTrustLevel() {
        return trustLevel;
    }

    public String getCategory() {
        return category;
    }

    public String getNotes() {
        return notes;
    }

    @Override
    public String toString() {
        return domain + " [" + trustLevel + " - " + category + "]";
    }
}
