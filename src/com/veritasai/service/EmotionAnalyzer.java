package com.veritasai.service;

import java.util.*;
import java.util.regex.Pattern;

/**
 * Detects emotional manipulation, fear-mongering, outrage triggers, and artificial urgency.
 */
public class EmotionAnalyzer {

    private static final Set<String> FEAR_WORDS = new HashSet<>(Arrays.asList(
        "deadly", "fatal", "toxic", "destroy", "annihilation", "collapse", "terrifying",
        "nightmare", "panic", "disaster", "danger", "peril", "bloodbath", "poisonous",
        "lethal", "threat", "crisis", "apocalypse"
    ));

    private static final Set<String> OUTRAGE_WORDS = new HashSet<>(Arrays.asList(
        "corrupt", "evil", "traitor", "scandal", "disgrace", "shameful", "treason",
        "liar", "criminals", "tyranny", "crooked", "disgusting", "villain", "fraud",
        "stealing", "conspiracy", "betrayal", "furious"
    ));

    private static final Set<String> URGENCY_WORDS = new HashSet<>(Arrays.asList(
        "urgent", "immediately", "hurry", "warning", "alert", "breaking", "forward this",
        "share before deleted", "act now", "last chance", "spread rapidly"
    ));

    public static class EmotionResult {
        public double score; // 0 - 100
        public String dominantTone;
        public Map<String, String> detectedTriggers = new HashMap<>();
    }

    public static EmotionResult analyze(String text) {
        EmotionResult res = new EmotionResult();
        if (text == null || text.trim().isEmpty()) {
            res.score = 0.0;
            res.dominantTone = "Objective / Neutral Journalism";
            return res;
        }

        String lower = text.toLowerCase();
        int fearCount = 0, outrageCount = 0, urgencyCount = 0;

        for (String w : FEAR_WORDS) {
            if (containsWord(lower, w)) {
                fearCount++;
                res.detectedTriggers.put(w.toUpperCase(), "Emotional Fear/Panic Marker: Word engineered to induce immediate alarm.");
            }
        }
        for (String w : OUTRAGE_WORDS) {
            if (containsWord(lower, w)) {
                outrageCount++;
                res.detectedTriggers.put(w.toUpperCase(), "Outrage/Anger Marker: Highly polarizing language designed to provoke hostility.");
            }
        }
        for (String w : URGENCY_WORDS) {
            if (containsWord(lower, w)) {
                urgencyCount++;
                res.detectedTriggers.put(w.toUpperCase(), "Artificial Urgency Trigger: Pressures readers to act or share without verifying.");
            }
        }

        int total = fearCount + outrageCount + urgencyCount;
        res.score = Math.min(100.0, total * 15.0);

        if (total == 0) {
            res.dominantTone = "Objective / Neutral Journalism";
        } else if (fearCount >= outrageCount && fearCount >= urgencyCount && fearCount > 1) {
            res.dominantTone = "Fear & Panic Induction";
        } else if (outrageCount >= fearCount && outrageCount >= urgencyCount && outrageCount > 1) {
            res.dominantTone = "High Outrage & Aggression";
        } else if (urgencyCount > 1) {
            res.dominantTone = "High Urgency / Viral Prompt";
        } else {
            res.dominantTone = "Mild Emotional Bias";
        }

        return res;
    }

    private static boolean containsWord(String text, String word) {
        Pattern p = Pattern.compile("\\b" + Pattern.quote(word) + "\\b", Pattern.CASE_INSENSITIVE);
        return p.matcher(text).find();
    }
}
