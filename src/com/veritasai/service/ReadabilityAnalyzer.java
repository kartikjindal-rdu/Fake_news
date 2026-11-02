package com.veritasai.service;

import com.veritasai.nlp.ReadabilityCalculator;

/**
 * Evaluates text syntactic complexity and Flesch Reading Ease.
 */
public class ReadabilityAnalyzer {

    public static class ReadabilityData {
        public double score;
        public String level;
        public int wordCount;
        public int sentenceCount;
    }

    public static ReadabilityData analyze(String text) {
        ReadabilityCalculator.ReadabilityResult raw = ReadabilityCalculator.calculate(text);
        ReadabilityData data = new ReadabilityData();
        data.score = raw.score;
        data.level = raw.level;
        data.wordCount = raw.wordCount;
        data.sentenceCount = raw.sentenceCount;
        return data;
    }
}
