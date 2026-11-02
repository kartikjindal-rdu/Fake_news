package com.fakenews.detector.classifier;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Analyzes linguistic cues, emotional bias, clickbait patterns, and sensationalism in news content.
 */
public class LinguisticAnalyzer {

    // Suspicious, clickbait, and conspiracy trigger phrases
    private static final String[] SENSATIONAL_PATTERNS = {
        "you won't believe", "you wont believe", "shocking truth", "secret cure",
        "miracle remedy", "doctors don't want you to know", "doctors hate this",
        "what they don't tell you", "they are hiding this", "illuminati",
        "secret government", "conspiracy exposed", "urgent share this",
        "forward before it gets deleted", "banned from tv", "mind control",
        "alien invasion", "guaranteed 100%", "magic pill", "overnight cure",
        "leaked audio exposes", "proof that mainstream media lies",
        "end of the world", "doomsday prediction", "scientists stunned",
        "unbelievable secret", "make millions fast", "toxic truth"
    };

    private static final String[] FAKE_NEWS_TRIGGER_WORDS = {
        "miracle", "shocking", "unbelievable", "secret", "exposed", "hoax",
        "illuminati", "conspiracy", "leak", "leaked", "cure-all", "toxic",
        "banned", "censored", "hidden", "stumble", "disaster", "apocalypse",
        "traitor", "scam", "rigged", "coverup", "cover-up", "doomsday"
    };

    public static class LinguisticReport {
        public double sensationalismScore; // 0 - 100
        public double clickbaitScore;      // 0 - 100
        public double capsRatio;           // 0 - 1
        public int excessivePunctuationCount;
        public List<String> detectedTriggers = new ArrayList<>();
        public List<String> observations = new ArrayList<>();
    }

    public static LinguisticReport analyze(String title, String content) {
        LinguisticReport report = new LinguisticReport();
        String fullText = (title + " " + content).trim();
        if (fullText.isEmpty()) {
            return report;
        }

        String lowerText = fullText.toLowerCase();

        // 1. Check Sensational Phrases
        for (String phrase : SENSATIONAL_PATTERNS) {
            if (lowerText.contains(phrase)) {
                report.detectedTriggers.add(phrase.toUpperCase());
                report.sensationalismScore += 25.0;
            }
        }

        // 2. Check Trigger Words
        for (String word : FAKE_NEWS_TRIGGER_WORDS) {
            Pattern p = Pattern.compile("\\b" + Pattern.quote(word) + "\\b", Pattern.CASE_INSENSITIVE);
            Matcher m = p.matcher(fullText);
            int count = 0;
            while (m.find()) {
                count++;
            }
            if (count > 0) {
                report.detectedTriggers.add(word);
                report.sensationalismScore += Math.min(count * 8.0, 20.0);
            }
        }

        // 3. ALL CAPS ratio in title / content
        int uppercaseChars = 0;
        int letterChars = 0;
        for (char c : fullText.toCharArray()) {
            if (Character.isLetter(c)) {
                letterChars++;
                if (Character.isUpperCase(c)) {
                    uppercaseChars++;
                }
            }
        }

        if (letterChars > 0) {
            report.capsRatio = (double) uppercaseChars / letterChars;
            if (report.capsRatio > 0.35 && letterChars > 15) {
                report.clickbaitScore += 30.0;
                report.observations.add("Excessive UPPERCASE letters detected (often used in emotional clickbait headlines).");
            }
        }

        // 4. Excessive Punctuation (e.g., !!!, ???, !?!?)
        Pattern punctPattern = Pattern.compile("([!?]{2,})");
        Matcher punctMatcher = punctPattern.matcher(fullText);
        int punctMatches = 0;
        while (punctMatcher.find()) {
            punctMatches++;
        }
        report.excessivePunctuationCount = punctMatches;
        if (punctMatches > 0) {
            report.clickbaitScore += Math.min(punctMatches * 15.0, 35.0);
            report.observations.add("Dramatic punctuation clusters ('!!' or '??') detected.");
        }

        // 5. Title specific clickbait patterns (e.g., starting with Numbers or 'Why you...')
        if (title != null && !title.trim().isEmpty()) {
            String titleLower = title.toLowerCase().trim();
            if (titleLower.matches("^\\d+\\s+.*") || titleLower.contains("this one trick") || titleLower.contains("will blow your mind")) {
                report.clickbaitScore += 25.0;
                report.observations.add("Classic listicle/clickbait headline syntax identified.");
            }
        }

        // Normalize Scores to 0-100 range
        report.sensationalismScore = Math.min(100.0, report.sensationalismScore);
        report.clickbaitScore = Math.min(100.0, report.clickbaitScore);

        return report;
    }
}
