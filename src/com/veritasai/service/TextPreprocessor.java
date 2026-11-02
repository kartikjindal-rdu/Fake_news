package com.veritasai.service;

import com.fakenews.detector.nlp.PorterStemmer;
import com.fakenews.detector.nlp.StopWords;

import java.util.ArrayList;
import java.util.List;

/**
 * Text normalization, tokenization, stop-word removal, and n-gram extraction.
 */
public class TextPreprocessor {

    public static String cleanText(String text) {
        if (text == null) return "";
        return text.toLowerCase().replaceAll("[^a-zA-Z0-9\\s]", " ").replaceAll("\\s+", " ").trim();
    }

    public static List<String> tokenize(String text) {
        List<String> tokens = new ArrayList<>();
        if (text == null || text.trim().isEmpty()) return tokens;

        String cleaned = cleanText(text);
        String[] words = cleaned.split("\\s+");

        for (String word : words) {
            word = word.trim();
            if (word.length() > 2 && !StopWords.isStopWord(word)) {
                String stemmed = PorterStemmer.stem(word);
                if (!stemmed.isEmpty()) {
                    tokens.add(stemmed);
                }
            }
        }
        return tokens;
    }

    public static List<String> extractFeatures(String text) {
        List<String> tokens = tokenize(text);
        List<String> features = new ArrayList<>(tokens);
        for (int i = 0; i < tokens.size() - 1; i++) {
            features.add(tokens.get(i) + "_" + tokens.get(i + 1));
        }
        return features;
    }
}
