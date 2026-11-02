package com.veritasai.util;

import java.awt.Color;

/**
 * Global constants, thresholds, colors, and configuration settings for Veritas AI.
 */
public class Constants {

    public static final String APP_NAME = "VERITAS AI";
    public static final String APP_TITLE = "Advanced Fake News & Misinformation Intelligence Platform";
    public static final String APP_VERSION = "2.5.0-ENTERPRISE";

    // Risk Score Levels
    public static final double RISK_LOW_MAX = 25.0;
    public static final double RISK_MODERATE_MAX = 50.0;
    public static final double RISK_HIGH_MAX = 75.0;

    public enum RiskLevel {
        LOW("LOW RISK", "#10b981", "Content appears relatively low-risk, but independent verification is still recommended."),
        MODERATE("MODERATE RISK", "#f59e0b", "Exercise caution and verify important claims before sharing."),
        HIGH("HIGH RISK", "#f97316", "Multiple suspicious indicators detected. Verify claims against primary sources."),
        CRITICAL("CRITICAL RISK", "#ef4444", "Strong misinformation indicators detected. Do not rely on or distribute without verification.");

        private final String label;
        private final String colorHex;
        private final String recommendation;

        RiskLevel(String label, String colorHex, String recommendation) {
            this.label = label;
            this.colorHex = colorHex;
            this.recommendation = recommendation;
        }

        public String getLabel() { return label; }
        public String getColorHex() { return colorHex; }
        public String getRecommendation() { return recommendation; }
        public Color getColor() { return Color.decode(colorHex); }
    }

    // Default FastAPI Backend URL
    public static final String DEFAULT_PYTHON_ML_URL = "http://127.0.0.1:8000";
}
