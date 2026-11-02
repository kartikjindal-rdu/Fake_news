package com.fakenews.detector.api;

import com.fakenews.detector.model.PredictionResult;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Utility for exporting forensic verification reports to JSON or text formats.
 */
public class ReportExporter {

    public static void exportToFile(PredictionResult result, String title, File targetFile) throws IOException {
        String name = targetFile.getName().toLowerCase();
        try (FileWriter writer = new FileWriter(targetFile)) {
            if (name.endsWith(".json")) {
                writer.write(result.toJson());
            } else {
                writer.write(generateTextReport(result, title));
            }
        }
    }

    public static String generateTextReport(PredictionResult result, String title) {
        StringBuilder sb = new StringBuilder();
        sb.append("=================================================================\n");
        sb.append("            AI FAKE NEWS DETECTION & FORENSIC REPORT            \n");
        sb.append("=================================================================\n");
        sb.append("Date / Timestamp : ").append(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date())).append("\n");
        sb.append("Headline / Claim : ").append(title != null && !title.isEmpty() ? title : "Untitled Text").append("\n");
        sb.append("-----------------------------------------------------------------\n");
        sb.append("FINAL VERDICT    : ").append(result.getVerdict().getLabel()).append("\n");
        sb.append("CONFIDENCE SCORE : ").append(result.getConfidenceScore()).append("%\n");
        sb.append("REAL LIKELIHOOD  : ").append(result.getRealProbability()).append("%\n");
        sb.append("FAKE LIKELIHOOD  : ").append(result.getFakeProbability()).append("%\n");
        sb.append("SENSATIONALISM   : ").append(result.getSensationalismScore()).append("%\n");
        sb.append("CLICKBAIT INDEX  : ").append(result.getClickbaitScore()).append("%\n");
        sb.append("EMOTIONAL BIAS   : ").append(result.getEmotionalBiasScore()).append("% (").append(result.getEmotionalTone()).append(")\n");
        sb.append("READABILITY      : ").append(result.getReadabilityScore()).append(" (").append(result.getReadabilityLevel()).append(")\n");
        sb.append("WORD COUNT       : ").append(result.getWordCount()).append(" words | ").append(result.getSentenceCount()).append(" sentences\n");
        
        if (result.getDomainReputation() != null) {
            sb.append("SOURCE DOMAIN    : ").append(result.getDomainReputation().getDomain()).append(" (")
              .append(result.getDomainReputation().getTrustLevel().getDescription()).append(")\n");
        }

        sb.append("\nFLAGGED KEYWORDS & TRIGGERS:\n");
        if (result.getFlaggedKeywords().isEmpty()) {
            sb.append("  * None detected\n");
        } else {
            for (String kw : result.getFlaggedKeywords()) {
                sb.append("  * ").append(kw).append("\n");
            }
        }

        sb.append("\nAI INSIGHTS & RATIONALE:\n");
        for (String insight : result.getInsights()) {
            sb.append("  • ").append(insight).append("\n");
        }

        if (result.getFactCheckQueryUrl() != null) {
            sb.append("\nFACT CHECK EXPLORER:\n  ").append(result.getFactCheckQueryUrl()).append("\n");
        }
        sb.append("=================================================================\n");
        return sb.toString();
    }
}
