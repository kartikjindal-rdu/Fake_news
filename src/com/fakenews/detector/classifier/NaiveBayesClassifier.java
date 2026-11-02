package com.fakenews.detector.classifier;

import com.fakenews.detector.model.NewsArticle;
import com.fakenews.detector.nlp.TextPreprocessor;
import com.fakenews.detector.nlp.TFIDFVectorizer;

import java.util.*;

/**
 * Multinomial Naive Bayes Classifier using TF-IDF weighted features with Laplace smoothing.
 */
public class NaiveBayesClassifier {

    private TFIDFVectorizer vectorizer;
    private Map<String, Map<String, Double>> classTermWeights; // class -> (term -> sum_of_tfidf)
    private Map<String, Double> classTotalWeights;             // class -> total_weight
    private Map<String, Integer> classDocCounts;               // class -> document count
    private int totalTrainDocs;
    private Set<String> classes;

    public NaiveBayesClassifier() {
        this.vectorizer = new TFIDFVectorizer();
        this.classTermWeights = new HashMap<>();
        this.classTotalWeights = new HashMap<>();
        this.classDocCounts = new HashMap<>();
        this.classes = new HashSet<>();
        this.totalTrainDocs = 0;
    }

    /**
     * Trains the classifier on a list of labeled news articles.
     */
    public void train(List<NewsArticle> dataset) {
        classTermWeights.clear();
        classTotalWeights.clear();
        classDocCounts.clear();
        classes.clear();
        totalTrainDocs = dataset.size();

        // 1. Preprocess & extract features for corpus
        List<List<String>> tokenizedDocs = new ArrayList<>();
        for (NewsArticle article : dataset) {
            String combined = article.getFullCombinedText();
            List<String> features = TextPreprocessor.extractFeatures(combined);
            tokenizedDocs.add(features);
        }

        // 2. Fit TF-IDF Vectorizer
        vectorizer.fit(tokenizedDocs);

        // 3. Accumulate Class Statistics
        for (int i = 0; i < dataset.size(); i++) {
            NewsArticle article = dataset.get(i);
            String label = article.getLabel().toUpperCase();
            classes.add(label);

            classDocCounts.put(label, classDocCounts.getOrDefault(label, 0) + 1);

            Map<String, Double> tfidf = vectorizer.transform(tokenizedDocs.get(i));
            Map<String, Double> termWeightsForClass = classTermWeights.computeIfAbsent(label, k -> new HashMap<>());

            double currentClassTotal = classTotalWeights.getOrDefault(label, 0.0);

            for (Map.Entry<String, Double> entry : tfidf.entrySet()) {
                String term = entry.getKey();
                double weight = entry.getValue();
                termWeightsForClass.put(term, termWeightsForClass.getOrDefault(term, 0.0) + weight);
                currentClassTotal += weight;
            }

            classTotalWeights.put(label, currentClassTotal);
        }
    }

    /**
     * Calculates posterior probabilities for given text features.
     * Returns a map of Class -> Probability (0.0 to 1.0)
     */
    public Map<String, Double> predictProbabilities(String text) {
        Map<String, Double> probabilities = new HashMap<>();
        if (classes.isEmpty() || totalTrainDocs == 0) {
            probabilities.put("REAL", 0.5);
            probabilities.put("FAKE", 0.5);
            return probabilities;
        }

        List<String> features = TextPreprocessor.extractFeatures(text);
        Map<String, Double> docTfidf = vectorizer.transform(features);
        int vocabSize = Math.max(1, vectorizer.getVocabulary().size());

        Map<String, Double> logPosteriors = new HashMap<>();
        double maxLog = Double.NEGATIVE_INFINITY;

        for (String c : classes) {
            // Prior probability: P(Class)
            int docCount = classDocCounts.getOrDefault(c, 0);
            double priorLog = Math.log((double) docCount / totalTrainDocs);

            double logLikelihood = 0.0;
            double totalWeightForClass = classTotalWeights.getOrDefault(c, 0.0);
            Map<String, Double> termWeights = classTermWeights.getOrDefault(c, Collections.emptyMap());

            for (Map.Entry<String, Double> entry : docTfidf.entrySet()) {
                String term = entry.getKey();
                double termCount = entry.getValue();

                double termWeightInClass = termWeights.getOrDefault(term, 0.0);
                // Laplace smoothing
                double smoothedProb = (termWeightInClass + 1.0) / (totalWeightForClass + vocabSize);
                logLikelihood += termCount * Math.log(smoothedProb);
            }

            double totalLog = priorLog + logLikelihood;
            logPosteriors.put(c, totalLog);

            if (totalLog > maxLog) {
                maxLog = totalLog;
            }
        }

        // Softmax / Normalization from log space to probability space
        double sumExp = 0.0;
        for (String c : classes) {
            double expVal = Math.exp(logPosteriors.get(c) - maxLog);
            probabilities.put(c, expVal);
            sumExp += expVal;
        }

        if (sumExp > 0) {
            for (String c : classes) {
                probabilities.put(c, probabilities.get(c) / sumExp);
            }
        }

        // Ensure default keys exist
        if (!probabilities.containsKey("REAL")) probabilities.put("REAL", 0.5);
        if (!probabilities.containsKey("FAKE")) probabilities.put("FAKE", 0.5);

        return probabilities;
    }

    public TFIDFVectorizer getVectorizer() {
        return vectorizer;
    }
}
