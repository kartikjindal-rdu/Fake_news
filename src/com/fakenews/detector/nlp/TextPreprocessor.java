package com.fakenews.detector.nlp;

import java.util.ArrayList;
import java.util.List;

/**
 * Handles text cleaning, tokenization, stop-word removal, and n-gram extraction.
 */
public class TextPreprocessor {

    /**
     * Cleans raw text: converts to lower case and replaces non-alphanumeric characters.
     */
    public static String cleanText(String text) {
        if (text == null) return "";
        return text.toLowerCase().replaceAll("[^a-zA-Z0-9\\s]", " ").replaceAll("\\s+", " ").trim();
    }

    /**
     * Tokenizes cleaned text into normalized, stemmed words excluding stopwords.
     */
    public static List<String> tokenize(String text) {
        List<String> tokens = new ArrayList<>();
        if (text == null || text.trim().isEmpty()) {
            return tokens;
        }

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

    /**
     * Extracts unigrams and bigrams to capture contextual phrases.
     */
    public static List<String> extractFeatures(String text) {
        List<String> tokens = tokenize(text);
        List<String> features = new ArrayList<>(tokens);

        // Add Bigrams
        for (int i = 0; i < tokens.size() - 1; i++) {
            features.add(tokens.get(i) + "_" + tokens.get(i + 1));
        }

        return features;
    }
}
