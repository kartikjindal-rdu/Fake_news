package com.veritasai.ml;

import com.fakenews.detector.classifier.NaiveBayesClassifier;
import com.fakenews.detector.data.DefaultDataset;
import com.fakenews.detector.model.NewsArticle;
import com.veritasai.model.ModelMetrics;
import com.veritasai.model.NewsInput;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Map;

/**
 * Embedded pure-Java Naive Bayes ML model implementation with full evaluation metrics.
 */
public class NaiveBayesModelService implements MLModelService {

    private final NaiveBayesClassifier classifier;
    private ModelMetrics metrics;

    public NaiveBayesModelService() {
        this.classifier = new NaiveBayesClassifier();
        this.metrics = new ModelMetrics();
        trainModel();
    }

    @Override
    public void trainModel() {
        List<NewsArticle> trainingData = DefaultDataset.getTrainingData();
        classifier.train(trainingData);
        evaluateModel();
    }

    @Override
    public Map<String, Double> predict(NewsInput input) {
        String combined = input.getFullCombinedText();
        return classifier.predictProbabilities(combined);
    }

    @Override
    public ModelMetrics evaluateModel() {
        List<NewsArticle> dataset = DefaultDataset.getTrainingData();
        int tp = 0, tn = 0, fp = 0, fn = 0;

        for (NewsArticle a : dataset) {
            Map<String, Double> probs = classifier.predictProbabilities(a.getFullCombinedText());
            double fakeP = probs.getOrDefault("FAKE", 0.5);
            String predicted = (fakeP >= 0.5) ? "FAKE" : "REAL";
            String actual = a.getLabel().toUpperCase();

            if (actual.equals("FAKE") && predicted.equals("FAKE")) {
                tp++;
            } else if (actual.equals("REAL") && predicted.equals("REAL")) {
                tn++;
            } else if (actual.equals("REAL") && predicted.equals("FAKE")) {
                fp++;
            } else if (actual.equals("FAKE") && predicted.equals("REAL")) {
                fn++;
            }
        }

        int total = tp + tn + fp + fn;
        double accuracy = (total > 0) ? (double) (tp + tn) / total : 0.0;
        double precision = (tp + fp > 0) ? (double) tp / (tp + fp) : 0.0;
        double recall = (tp + fn > 0) ? (double) tp / (tp + fn) : 0.0;
        double f1 = (precision + recall > 0) ? 2 * (precision * recall) / (precision + recall) : 0.0;

        metrics.setTruePositives(tp);
        metrics.setTrueNegatives(tn);
        metrics.setFalsePositives(fp);
        metrics.setFalseNegatives(fn);
        metrics.setAccuracy(Math.round(accuracy * 1000.0) / 10.0);
        metrics.setPrecision(Math.round(precision * 1000.0) / 10.0);
        metrics.setRecall(Math.round(recall * 1000.0) / 10.0);
        metrics.setF1Score(Math.round(f1 * 1000.0) / 10.0);
        metrics.setTrainingDate(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        metrics.setTrained(true);

        return metrics;
    }

    @Override
    public ModelMetrics getModelMetrics() {
        return metrics;
    }

    @Override
    public boolean isServiceAvailable() {
        return true;
    }
}
