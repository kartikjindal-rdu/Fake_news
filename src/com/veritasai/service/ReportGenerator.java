package com.veritasai.service;

import com.veritasai.model.Claim;
import com.veritasai.model.NewsAnalysisResult;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

/**
 * Generates forensic analysis reports in text, JSON, and printable formats.
 */
public class ReportGenerator {

    public static String generateTextReport(NewsAnalysisResult result, String headline) {
        StringBuilder sb = new StringBuilder();
        sb.append("================================================================================\n");
        sb.append("                 VERITAS AI - FORENSIC NEWS ANALYSIS REPORT                     \n");
        sb.append("================================================================================\n");
        sb.append("Scan Reference ID : ").append(result.getScanId()).append("\n");
        sb.append("Timestamp         : ").append(result.getTimestamp()).append("\n");
        sb.append("Headline / Claim  : ").append(headline != null && !headline.isEmpty() ? headline : "Untitled Input").append("\n");
        sb.append("--------------------------------------------------------------------------------\n");
        sb.append("FINAL VERDICT     : ").append(result.getVerdict().getLabel()).append("\n");
        sb.append("RISK LEVEL        : ").append(result.getRiskLevel().getLabel()).append(" (Score: ").append(result.getRiskScore()).append("/100)\n");
        sb.append("AI CONFIDENCE     : ").append(result.getAiConfidence()).append("%\n");
        sb.append("CREDIBILITY SCORE : ").append(result.getCredibilityScore()).append("/100\n");
        sb.append("--------------------------------------------------------------------------------\n");
        sb.append("10-FACTOR METRIC BREAKDOWN:\n");
        sb.append(String.format("  • Fake Probability        : %.1f%%\n", result.getFakeProbability()));
        sb.append(String.format("  • Verified Fact Likelihood: %.1f%%\n", result.getRealProbability()));
        sb.append(String.format("  • Sensationalism Score    : %.1f%%\n", result.getSensationalismScore()));
        sb.append(String.format("  • Clickbait Index         : %.1f%%\n", result.getClickbaitScore()));
        sb.append(String.format("  • Emotional Bias Score    : %.1f%% (%s)\n", result.getEmotionalManipulationScore(), result.getEmotionalTone()));
        sb.append(String.format("  • Source Trust Score      : %.1f%%\n", result.getSourceTrustScore()));
        sb.append(String.format("  • Readability Index       : %.1f (%s)\n", result.getReadabilityScore(), result.getReadabilityLevel()));
        sb.append(String.format("  • Word / Sentence Count   : %d words | %d sentences\n", result.getWordCount(), result.getSentenceCount()));

        sb.append("\n--------------------------------------------------------------------------------\n");
        sb.append("AI FORENSIC EXPLANATION & FINDINGS:\n");
        sb.append("[Primary Findings]\n");
        for (String pf : result.getPrimaryFindings()) {
            sb.append("  * ").append(pf).append("\n");
        }

        sb.append("\n[Suspicious Language & Triggers]\n");
        for (String sl : result.getSuspiciousLanguageNotes()) {
            sb.append("  * ").append(sl).append("\n");
        }

        sb.append("\n[Source / Domain Analysis]\n");
        for (String sa : result.getSourceAnalysisNotes()) {
            sb.append("  * ").append(sa).append("\n");
        }

        sb.append("\n--------------------------------------------------------------------------------\n");
        sb.append("EXTRACTED CLAIMS & VERIFICATION STATUS:\n");
        if (result.getExtractedClaims().isEmpty()) {
            sb.append("  * No distinct factual claims parsed.\n");
        } else {
            int idx = 1;
            for (Claim c : result.getExtractedClaims()) {
                sb.append(String.format("  Claim %d: \"%s\"\n", idx++, c.getText()));
                sb.append(String.format("    Status: [%s] | Risk: [%s]\n", c.getVerificationStatus().getLabel(), c.getRiskLevel().getLabel()));
            }
        }

        sb.append("\n--------------------------------------------------------------------------------\n");
        sb.append("RECOMMENDED ACTION:\n");
        sb.append("  ").append(result.getRecommendedAction()).append("\n");

        if (result.getFactCheckQueryUrl() != null) {
            sb.append("\nFACT-CHECK SEARCH LINK:\n");
            sb.append("  ").append(result.getFactCheckQueryUrl()).append("\n");
        }
        sb.append("================================================================================\n");
        return sb.toString();
    }

    public static void exportToFile(NewsAnalysisResult result, String headline, File file) throws IOException {
        String name = file.getName().toLowerCase();
        try (FileWriter writer = new FileWriter(file)) {
            if (name.endsWith(".json")) {
                writer.write(result.toJson());
            } else {
                writer.write(generateTextReport(result, headline));
            }
        }
    }
}
