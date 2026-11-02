package com.fakenews.detector.nlp;

import java.util.*;

/**
 * Computes TF-IDF (Term Frequency - Inverse Document Frequency) representations for documents.
 */
public class TFIDFVectorizer {

    private Map<String, Integer> documentFrequency;
    private int totalDocuments;
    private Set<String> vocabulary;

    public TFIDFVectorizer() {
        this.documentFrequency = new HashMap<>();
        this.totalDocuments = 0;
        this.vocabulary = new HashSet<>();
    }

    /**
     * Fits the vectorizer on a corpus of tokenized documents.
     */
    public void fit(List<List<String>> corpus) {
        documentFrequency.clear();
        vocabulary.clear();
        totalDocuments = corpus.size();

        for (List<String> doc : corpus) {
            Set<String> uniqueTerms = new HashSet<>(doc);
            for (String term : uniqueTerms) {
                documentFrequency.put(term, documentFrequency.getOrDefault(term, 0) + 1);
                vocabulary.add(term);
            }
        }
    }

    /**
     * Transforms a tokenized document into a TF-IDF map of (term -> tfidf_weight).
     */
    public Map<String, Double> transform(List<String> docTokens) {
        Map<String, Double> tfMap = new HashMap<>();
        if (docTokens == null || docTokens.isEmpty() || totalDocuments == 0) {
            return tfMap;
        }

        // Calculate Term Frequency
        for (String token : docTokens) {
            tfMap.put(token, tfMap.getOrDefault(token, 0.0) + 1.0);
        }

        int docLength = docTokens.size();
        Map<String, Double> tfidfMap = new HashMap<>();

        for (Map.Entry<String, Double> entry : tfMap.entrySet()) {
            String term = entry.getKey();
            double tf = entry.getValue() / docLength;
            int df = documentFrequency.getOrDefault(term, 0);

            // Smooth IDF calculation: ln((N + 1) / (DF + 1)) + 1
            double idf = Math.log((double) (totalDocuments + 1) / (df + 1)) + 1.0;
            tfidfMap.put(term, tf * idf);
        }

        return tfidfMap;
    }

    public Set<String> getVocabulary() {
        return vocabulary;
    }

    public int getTotalDocuments() {
        return totalDocuments;
    }
}
