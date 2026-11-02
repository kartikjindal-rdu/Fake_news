package com.veritasai.service;

import com.veritasai.util.TextUtils;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * Detects and scores clickbait patterns, deceptive headlines, and curiosity gaps.
 */
public class ClickbaitAnalyzer {

    private static final String[] CLICKBAIT_PATTERNS = {
        "you won't believe", "you wont believe", "will blow your mind",
        "this one trick", "what happens next", "the reason why will shock",
        "see what she looks like now", "doctors hate this", "simple trick to",
        "before it is deleted", "banned from tv", "fans are crying",
        "jaw-dropping", "unbelievable secret", "everybody is talking about"
    };

    public static class ClickbaitResult {
        public double score; // 0 - 100
        public Map<String, String> detectedPatterns = new HashMap<>();
    }

    public static ClickbaitResult analyze(String headline, String body) {
        ClickbaitResult res = new ClickbaitResult();
        String combined = ((headline != null ? headline : "") + " " + (body != null ? body : "")).toLowerCase();

        double baseScore = 0.0;

        // 1. Specific Clickbait Phrases
        for (String pattern : CLICKBAIT_PATTERNS) {
            if (combined.contains(pattern)) {
                baseScore += 30.0;
                res.detectedPatterns.put(pattern.toUpperCase(), "Clickbait / Curiosity Gap Trigger: Designed to induce viral clicks rather than convey factual info.");
            }
        }

        // 2. Headline Caps Ratio
        if (headline != null && headline.length() > 10) {
            double capsRatio = TextUtils.calculateCapsRatio(headline);
            if (capsRatio > 0.40) {
                baseScore += 25.0;
                res.detectedPatterns.put("EXCESSIVE UPPERCASE", "Clickbait Visual Indicator: Over 40% uppercase characters used to attract attention.");
            }
        }

        // 3. Punctuation Clusters in Headline (???, !!!)
        int punctClusters = TextUtils.countPunctuationClusters(headline != null ? headline : "");
        if (punctClusters > 0) {
            baseScore += Math.min(punctClusters * 15.0, 30.0);
            res.detectedPatterns.put("DRAMATIC PUNCTUATION", "Clickbait Punctuation: Clusters of '!' or '?' found in headline.");
        }

        // 4. Headline starting with numbers (Listicle pattern)
        if (headline != null && headline.trim().matches("^\\d+\\s+.*")) {
            baseScore += 15.0;
            res.detectedPatterns.put("LISTICLE HEADLINE", "Listicle Pattern: Headline structured as numbered list.");
        }

        res.score = Math.min(100.0, baseScore);
        return res;
    }
}
