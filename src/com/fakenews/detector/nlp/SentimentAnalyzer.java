package com.fakenews.detector.nlp;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Evaluates emotional bias, urgency markers, fear/outrage triggers, and hyperbolic tone in text.
 */
public class SentimentAnalyzer {

    // Emotionally charged & hyper-partisan words
    private static final Set<String> FEAR_AND_PANIC_WORDS = new HashSet<>(Arrays.asList(
        "catastrophe", "apocalypse", "deadly", "fatal", "toxic", "destroy", "annihilation",
        "collapse", "terrifying", "horrifying", "nightmare", "panic", "disaster", "danger",
        "peril", "bloodbath", "poisonous", "threat", "lethal", "ruin", "crisis", "fatal"
    ));

    private static final Set<String> OUTRAGE_AND_ANGER_WORDS = new HashSet<>(Arrays.asList(
        "corrupt", "evil", "traitor", "scandal", "disgrace", "shameful", "treason",
        "liar", "criminals", "theft", "tyranny", "crooked", "disgusting", "villain",
        "fraud", "stealing", "conspiracy", "betrayal", "rage", "furious", "unforgivable"
    ));

    private static final Set<String> URGENCY_AND_CLICK_WORDS = new HashSet<>(Arrays.asList(
        "urgent", "immediately", "hurry", "warning", "alert", "breaking", "spread",
        "share", "forward", "viral", "secret", "censored", "banned", "now", "critical"
    ));

    public static class SentimentReport {
        public double emotionalBiasScore; // 0 to 100
        public String dominantTone;        // e.g. "High Urgency & Fear", "Aggressive / Outrage", "Neutral / Objective"
        public List<String> detectedEmotionWords = new ArrayList<>();
    }

    public static SentimentReport analyze(String text) {
        SentimentReport report = new SentimentReport();
        if (text == null || text.trim().isEmpty()) {
            report.emotionalBiasScore = 0.0;
            report.dominantTone = "Neutral / Factual";
            return report;
        }

        String lower = text.toLowerCase();
        int fearCount = 0;
        int outrageCount = 0;
        int urgencyCount = 0;

        for (String w : FEAR_AND_PANIC_WORDS) {
            if (containsWord(lower, w)) {
                fearCount++;
                report.detectedEmotionWords.add(w + " (Fear/Panic)");
            }
        }

        for (String w : OUTRAGE_AND_ANGER_WORDS) {
            if (containsWord(lower, w)) {
                outrageCount++;
                report.detectedEmotionWords.add(w + " (Outrage)");
            }
        }

        for (String w : URGENCY_AND_CLICK_WORDS) {
            if (containsWord(lower, w)) {
                urgencyCount++;
                report.detectedEmotionWords.add(w + " (Urgency)");
            }
        }

        int totalTriggers = fearCount + outrageCount + urgencyCount;
        report.emotionalBiasScore = Math.min(100.0, totalTriggers * 14.0);

        if (totalTriggers == 0) {
            report.dominantTone = "Objective / Neutral Journalism";
        } else if (fearCount >= outrageCount && fearCount >= urgencyCount && fearCount > 1) {
            report.dominantTone = "Fear & Panic Induction";
        } else if (outrageCount >= fearCount && outrageCount >= urgencyCount && outrageCount > 1) {
            report.dominantTone = "High Outrage & Aggression";
        } else if (urgencyCount > 1) {
            report.dominantTone = "High Urgency / Clickbait Prompt";
        } else {
            report.dominantTone = "Mild Emotional Bias";
        }

        return report;
    }

    private static boolean containsWord(String text, String word) {
        Pattern p = Pattern.compile("\\b" + Pattern.quote(word) + "\\b", Pattern.CASE_INSENSITIVE);
        return p.matcher(text).find();
    }
}
