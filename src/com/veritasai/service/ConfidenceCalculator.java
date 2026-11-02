package com.veritasai.service;

/**
 * Calculates AI confidence based on convergence between ML model and linguistic heuristics.
 */
public class ConfidenceCalculator {

    public static double calculate(double mlConfidence, double heuristicAgreementScore, int wordCount) {
        double lengthFactor = 1.0;
        if (wordCount < 10) {
            lengthFactor = 0.65; // lower confidence on ultra-short snippets
        } else if (wordCount < 25) {
            lengthFactor = 0.85;
        }

        double confidence = ((mlConfidence * 0.65) + (heuristicAgreementScore * 0.35)) * lengthFactor;
        confidence = Math.max(25.0, Math.min(99.0, confidence));
        return Math.round(confidence * 10.0) / 10.0;
    }
}
