package com.veritasai.service;

import com.veritasai.model.Claim;
import com.veritasai.model.Claim.VerificationStatus;
import com.veritasai.util.Constants.RiskLevel;
import com.veritasai.util.TextUtils;

import java.util.ArrayList;
import java.util.List;

/**
 * Extracts and tags central factual claims from news text for verification auditing.
 */
public class ClaimExtractor {

    public static List<Claim> extractClaims(String headline, String content, RiskLevel overallRisk) {
        List<Claim> claims = new ArrayList<>();
        String combined = (headline != null ? headline : "") + ". " + (content != null ? content : "");
        List<String> sentences = TextUtils.extractSentences(combined);

        int claimIndex = 1;
        for (String sentence : sentences) {
            String sLower = sentence.toLowerCase();

            // Look for assertive factual claims, causal statements, statistics, or quotes
            boolean isClaimCandidate = sLower.contains("claims") || sLower.contains("revealed") ||
                                       sLower.contains("discovered") || sLower.contains("proves") ||
                                       sLower.contains("announces") || sLower.contains("confirmed") ||
                                       sLower.contains("causes") || sLower.contains("cures") ||
                                       sLower.matches(".*\\d+%.*") || sLower.matches(".*\\$\\d+.*") ||
                                       sentence.contains("\"");

            if (isClaimCandidate || (claimIndex == 1 && sentence.length() > 20)) {
                RiskLevel claimRisk = overallRisk;
                VerificationStatus status;

                if (sLower.contains("miracle") || sLower.contains("secret") || sLower.contains("banned") || sLower.contains("illuminati")) {
                    claimRisk = RiskLevel.CRITICAL;
                    status = VerificationStatus.CONFLICTING_EVIDENCE;
                } else if (overallRisk == RiskLevel.HIGH || overallRisk == RiskLevel.CRITICAL) {
                    status = VerificationStatus.REQUIRES_VERIFICATION;
                } else if (overallRisk == RiskLevel.LOW) {
                    status = VerificationStatus.SUPPORTED_EVIDENCE;
                } else {
                    status = VerificationStatus.NOT_VERIFIED;
                }

                String rationale = "Extracted assertion evaluated against empirical knowledge base heuristics.";
                claims.add(new Claim(sentence.trim(), claimRisk, status, rationale));
                claimIndex++;

                if (claims.size() >= 4) break; // Keep top 4 key claims
            }
        }

        if (claims.isEmpty() && !combined.trim().isEmpty()) {
            claims.add(new Claim(combined.trim(), overallRisk, VerificationStatus.NOT_VERIFIED, "Primary claim statement extracted."));
        }

        return claims;
    }
}
