package com.fakenews.detector.nlp;

/**
 * Computes Flesch Reading Ease and text complexity metrics.
 */
public class ReadabilityCalculator {

    public static class ReadabilityResult {
        public double score;          // 0 - 100
        public String level;          // "Standard Journalistic", "Simple / Casual", "Academic / Complex"
        public int wordCount;
        public int sentenceCount;
        public int syllableCount;
    }

    public static ReadabilityResult calculate(String text) {
        ReadabilityResult res = new ReadabilityResult();
        if (text == null || text.trim().isEmpty()) {
            res.score = 65.0;
            res.level = "Standard";
            return res;
        }

        String cleaned = text.trim();
        // Sentences
        String[] sentences = cleaned.split("[.!?]+");
        res.sentenceCount = Math.max(1, sentences.length);

        // Words
        String[] words = cleaned.replaceAll("[^a-zA-Z0-9\\s]", " ").split("\\s+");
        int validWords = 0;
        int totalSyllables = 0;

        for (String w : words) {
            w = w.trim();
            if (!w.isEmpty()) {
                validWords++;
                totalSyllables += countSyllables(w);
            }
        }

        res.wordCount = Math.max(1, validWords);
        res.syllableCount = totalSyllables;

        // Flesch Reading Ease Formula: 206.835 - (1.015 * ASL) - (84.6 * ASW)
        double avgSentenceLength = (double) res.wordCount / res.sentenceCount;
        double avgSyllablesPerWord = (double) totalSyllables / res.wordCount;

        double flesch = 206.835 - (1.015 * avgSentenceLength) - (84.6 * avgSyllablesPerWord);
        flesch = Math.max(0.0, Math.min(100.0, flesch));
        res.score = Math.round(flesch * 10.0) / 10.0;

        if (res.score >= 70) {
            res.level = "Simple / Casual (High Readability)";
        } else if (res.score >= 50) {
            res.level = "Standard Journalistic Style";
        } else if (res.score >= 30) {
            res.level = "Complex / Formal Report";
        } else {
            res.level = "Academic / Highly Dense";
        }

        return res;
    }

    private static int countSyllables(String word) {
        word = word.toLowerCase().replaceAll("[^a-z]", "");
        if (word.length() <= 3) return 1;

        int count = 0;
        boolean prevVowel = false;
        String vowels = "aeiouy";

        for (char c : word.toCharArray()) {
            boolean isVowel = vowels.indexOf(c) != -1;
            if (isVowel && !prevVowel) {
                count++;
            }
            prevVowel = isVowel;
        }

        if (word.endsWith("e") && count > 1) {
            count--;
        }

        return Math.max(1, count);
    }
}
