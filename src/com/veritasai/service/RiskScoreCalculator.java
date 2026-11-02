package com.veritasai.service;

import com.veritasai.util.Constants;
import com.veritasai.util.Constants.RiskLevel;

/**
 * Calculates normalized multi-factor composite risk scores.
 */
public class RiskScoreCalculator {

    public static class RiskEvaluation {
        public double riskScore; // 0.0 to 100.0
        public RiskLevel riskLevel;
    }

    /**
     * Weights:
     * - ML Fake Probability: 40%
     * - Sensationalism: 20%
     * - Clickbait: 15%
     * - Emotional Manipulation: 15%
     * - Source Inverted Trust: 10%
     */
    public static RiskEvaluation calculate(double fakeProb, double sensationalism,
                                           double clickbait, double emotion, double sourceTrust) {
        double invertedSourceRisk = 100.0 - sourceTrust;

        double composite = (fakeProb * 0.40) +
                           (sensationalism * 0.20) +
                           (clickbait * 0.15) +
                           (emotion * 0.15) +
                           (invertedSourceRisk * 0.10);

        composite = Math.max(0.0, Math.min(100.0, composite));
        double roundedScore = Math.round(composite * 10.0) / 10.0;

        RiskEvaluation eval = new RiskEvaluation();
        eval.riskScore = roundedScore;

        if (roundedScore <= Constants.RISK_LOW_MAX) {
            eval.riskLevel = RiskLevel.LOW;
        } else if (roundedScore <= Constants.RISK_MODERATE_MAX) {
            eval.riskLevel = RiskLevel.MODERATE;
        } else if (roundedScore <= Constants.RISK_HIGH_MAX) {
            eval.riskLevel = RiskLevel.HIGH;
        } else {
            eval.riskLevel = RiskLevel.CRITICAL;
        }

        return eval;
    }
}
