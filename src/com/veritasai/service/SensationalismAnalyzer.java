package com.veritasai.service;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Detects sensationalism, hyperbole, miraculous assertions, and exaggerated language.
 */
public class SensationalismAnalyzer {

    private static final String[] SENSATIONAL_WORDS = {
        "shocking", "miracle", "unbelievable", "mind-blowing", "revolutionary",
        "cure-all", "catastrophic", "forbidden", "exposed", "terrifying",
        "stunning", "explosive", "massive secret", "doomsday", "apocalyptic",
        "magic", "guaranteed 100%", "insane", "bizarre", "horrifying"
    };

    public static class SensationalismResult {
        public double score; // 0 - 100
        public Map<String, String> detectedWords = new HashMap<>();
    }

    public static SensationalismResult analyze(String text) {
        SensationalismResult result = new SensationalismResult();
        if (text == null || text.trim().isEmpty()) return result;

        double total = 0.0;
        for (String word : SENSATIONAL_WORDS) {
            Pattern p = Pattern.compile("\\b" + Pattern.quote(word) + "\\b", Pattern.CASE_INSENSITIVE);
            Matcher m = p.matcher(text);
            int count = 0;
            while (m.find()) count++;

            if (count > 0) {
                total += Math.min(count * 12.0, 30.0);
                result.detectedWords.put(word.toUpperCase(), "Sensationalist Hyperbole: Word often used to exaggerate claims without empirical nuance.");
            }
        }

        result.score = Math.min(100.0, total);
        return result;
    }
}
