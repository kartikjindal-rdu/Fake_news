package com.veritasai.service;

import com.veritasai.model.DomainAnalysis;
import com.veritasai.model.NewsAnalysisResult;
import com.veritasai.util.Constants.RiskLevel;

import java.util.Map;

/**
 * Generates transparent, structured explainable AI rationale.
 */
public class ExplainabilityEngine {

    public static void populateExplanations(NewsAnalysisResult result,
                                           ClickbaitAnalyzer.ClickbaitResult clickbait,
                                           SensationalismAnalyzer.SensationalismResult sensationalism,
                                           EmotionAnalyzer.EmotionResult emotion,
                                           DomainAnalysis domainAnalysis) {

        // 1. PRIMARY FINDINGS
        if (result.getRiskLevel() == RiskLevel.CRITICAL || result.getRiskLevel() == RiskLevel.HIGH) {
            result.addPrimaryFinding("High risk of misleading or fabricated content detected across multiple analytical dimensions.");
        } else if (result.getRiskLevel() == RiskLevel.MODERATE) {
            result.addPrimaryFinding("Moderate risk: Some sensationalist or emotive patterns present that require factual verification.");
        } else {
            result.addPrimaryFinding("Text exhibits journalistic balance, objective vocabulary, and low manipulation indices.");
        }

        if (sensationalism.score > 40) {
            result.addPrimaryFinding("Headline/body contains unusually high concentration of hyperbolic and miraculous claims.");
        }
        if (clickbait.score > 40) {
            result.addPrimaryFinding("Structural clickbait syntax detected (curiosity gap prompts or excessive capitalization).");
        }
        if (emotion.score > 40) {
            result.addPrimaryFinding("Strong emotional manipulation markers (" + emotion.dominantTone + ") identified in sentence structure.");
        }

        // 2. SUSPICIOUS LANGUAGE
        for (Map.Entry<String, String> entry : sensationalism.detectedWords.entrySet()) {
            result.addSuspiciousLanguageNote(entry.getKey() + ": " + entry.getValue());
            result.addHighlightedTrigger(entry.getKey(), entry.getValue());
        }
        for (Map.Entry<String, String> entry : clickbait.detectedPatterns.entrySet()) {
            result.addSuspiciousLanguageNote(entry.getKey() + ": " + entry.getValue());
            result.addHighlightedTrigger(entry.getKey(), entry.getValue());
        }
        for (Map.Entry<String, String> entry : emotion.detectedTriggers.entrySet()) {
            result.addSuspiciousLanguageNote(entry.getKey() + ": " + entry.getValue());
            result.addHighlightedTrigger(entry.getKey(), entry.getValue());
        }

        if (result.getSuspiciousLanguageNotes().isEmpty()) {
            result.addSuspiciousLanguageNote("No prominent manipulation keywords or sensational triggers flagged.");
        }

        // 3. SOURCE ANALYSIS
        if (domainAnalysis != null && !domainAnalysis.getDomainName().isEmpty()) {
            result.addSourceAnalysisNote("Domain: " + domainAnalysis.getDomainName() + " (" + domainAnalysis.getEditorialCategory() + ")");
            result.addSourceAnalysisNote("Trust Assessment: " + domainAnalysis.getAssessmentSummary());
            for (String ind : domainAnalysis.getSuspiciousIndicators()) {
                result.addSourceAnalysisNote("Warning: " + ind);
            }
        } else {
            result.addSourceAnalysisNote("Source URL not provided. Linguistic evaluation performed solely on provided text.");
        }

        // 4. RECOMMENDED ACTION
        result.setRecommendedAction(result.getRiskLevel().getRecommendation());
    }
}
