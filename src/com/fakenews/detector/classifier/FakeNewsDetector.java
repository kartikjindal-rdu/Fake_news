package com.fakenews.detector.classifier;

import com.fakenews.detector.data.DefaultDataset;
import com.fakenews.detector.model.DomainReputation;
import com.fakenews.detector.model.NewsArticle;
import com.fakenews.detector.model.PredictionResult;
import com.fakenews.detector.model.PredictionResult.Verdict;
import com.fakenews.detector.nlp.ReadabilityCalculator;
import com.fakenews.detector.nlp.SentimentAnalyzer;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

/**
 * Supercharged Multi-Factor AI Engine coordinating NLP feature extraction, Naive Bayes ML,
 * Emotional Bias detection, Linguistic Sensationalism, Domain Trust ratings, and Readability indexing.
 */
public class FakeNewsDetector {

    private NaiveBayesClassifier classifier;
    private boolean isTrained;

    public FakeNewsDetector() {
        this.classifier = new NaiveBayesClassifier();
        this.isTrained = false;
    }

    public void trainWithDefaults() {
        train(DefaultDataset.getTrainingData());
    }

    public void train(List<NewsArticle> dataset) {
        if (dataset == null || dataset.isEmpty()) {
            throw new IllegalArgumentException("Training dataset cannot be empty.");
        }
        this.classifier.train(dataset);
        this.isTrained = true;
    }

    public PredictionResult analyze(String title, String content) {
        return analyze(title, content, "");
    }

    /**
     * Evaluates a news claim with optional source URL / domain.
     */
    public PredictionResult analyze(String title, String content, String sourceUrl) {
        if (!isTrained) {
            trainWithDefaults();
        }

        String safeTitle = (title != null) ? title.trim() : "";
        String safeContent = (content != null) ? content.trim() : "";
        String combinedText = (safeTitle + " " + safeContent).trim();

        PredictionResult result = new PredictionResult();

        if (combinedText.isEmpty()) {
            result.setVerdict(Verdict.SUSPICIOUS);
            result.setConfidenceScore(0.0);
            result.setFakeProbability(50.0);
            result.setRealProbability(50.0);
            result.addInsight("No text provided for analysis.");
            return result;
        }

        // 1. Readability & Metrics
        ReadabilityCalculator.ReadabilityResult readRes = ReadabilityCalculator.calculate(combinedText);
        result.setWordCount(readRes.wordCount);
        result.setSentenceCount(readRes.sentenceCount);
        result.setReadabilityScore(readRes.score);
        result.setReadabilityLevel(readRes.level);

        // 2. Emotional Bias & Sentiment
        SentimentAnalyzer.SentimentReport sentReport = SentimentAnalyzer.analyze(combinedText);
        result.setEmotionalBiasScore(sentReport.emotionalBiasScore);
        result.setEmotionalTone(sentReport.dominantTone);
        for (String emoWord : sentReport.detectedEmotionWords) {
            result.addFlaggedKeyword(emoWord);
        }

        // 3. Linguistic & Clickbait Analysis
        LinguisticAnalyzer.LinguisticReport lingReport = LinguisticAnalyzer.analyze(safeTitle, safeContent);
        result.setSensationalismScore(lingReport.sensationalismScore);
        result.setClickbaitScore(lingReport.clickbaitScore);

        for (String trigger : lingReport.detectedTriggers) {
            result.addFlaggedKeyword(trigger);
        }
        for (String obs : lingReport.observations) {
            result.addInsight(obs);
        }

        // 4. Source / Domain Credibility
        DomainReputation domainRep = DomainCredibilityChecker.checkDomain(sourceUrl);
        result.setDomainReputation(domainRep);

        // 5. Machine Learning Naive Bayes Probabilities
        Map<String, Double> mlProbs = classifier.predictProbabilities(combinedText);
        double mlFakeProb = mlProbs.getOrDefault("FAKE", 0.5) * 100.0;
        double mlRealProb = mlProbs.getOrDefault("REAL", 0.5) * 100.0;

        // 6. Multi-Factor Ensemble Fusion
        // Weights: ML (50%), Linguistic/Clickbait (25%), Emotional Bias (15%), Readability/Format (10%)
        double heuristicPenalty = (lingReport.sensationalismScore * 0.5) + (lingReport.clickbaitScore * 0.5);
        double combinedFakeProb = (mlFakeProb * 0.50) + (heuristicPenalty * 0.25) + (sentReport.emotionalBiasScore * 0.15);

        // Domain modifier
        if (domainRep != null) {
            switch (domainRep.getTrustLevel()) {
                case HIGHLY_TRUSTED:
                    combinedFakeProb = combinedFakeProb * 0.55; // strong credibility boost
                    result.addInsight("Domain '" + domainRep.getDomain() + "' is an internationally verified authoritative news source.");
                    break;
                case GENERALLY_RELIABLE:
                    combinedFakeProb = combinedFakeProb * 0.75;
                    result.addInsight("Domain '" + domainRep.getDomain() + "' belongs to an established journalism publisher.");
                    break;
                case UNRELIABLE_OR_HOAX:
                    combinedFakeProb = Math.max(88.0, combinedFakeProb * 1.35);
                    result.addInsight("CRITICAL: Domain '" + domainRep.getDomain() + "' is cataloged as a known hoax, conspiracy, or satire outlet!");
                    break;
                case QUESTIONABLE:
                    combinedFakeProb = Math.max(65.0, combinedFakeProb * 1.15);
                    result.addInsight("WARNING: Domain '" + domainRep.getDomain() + "' has questionable credibility or unusual TLD markers.");
                    break;
                default:
                    break;
            }
        }

        combinedFakeProb = Math.max(0.0, Math.min(100.0, combinedFakeProb));
        double combinedRealProb = 100.0 - combinedFakeProb;

        result.setFakeProbability(Math.round(combinedFakeProb * 10.0) / 10.0);
        result.setRealProbability(Math.round(combinedRealProb * 10.0) / 10.0);

        // 7. Final Verdict Classification
        if (domainRep != null && domainRep.getCategory().contains("Satire")) {
            result.setVerdict(Verdict.SATIRE);
            result.setConfidenceScore(95.0);
            result.addInsight("Identified as satirical humor content; not intended to be factual news.");
        } else if (combinedFakeProb >= 65.0) {
            result.setVerdict(Verdict.FAKE);
            result.setConfidenceScore(Math.round(combinedFakeProb * 10.0) / 10.0);
            result.addInsight("High probability of fabricated information, panic induction, or misinformation.");
        } else if (combinedRealProb >= 65.0) {
            result.setVerdict(Verdict.REAL);
            result.setConfidenceScore(Math.round(combinedRealProb * 10.0) / 10.0);
            result.addInsight("Factual linguistic structure, neutral tone, and reputable vocabulary observed.");
        } else {
            result.setVerdict(Verdict.SUSPICIOUS);
            result.setConfidenceScore(Math.round(Math.max(combinedFakeProb, combinedRealProb) * 10.0) / 10.0);
            result.addInsight("Mixed signals detected. Independent verification with certified fact-checkers is advised.");
        }

        // 8. Generate Fact-Check Search deep-link
        try {
            String query = !safeTitle.isEmpty() ? safeTitle : (safeContent.length() > 60 ? safeContent.substring(0, 60) : safeContent);
            String encoded = URLEncoder.encode(query, StandardCharsets.UTF_8.toString());
            result.setFactCheckQueryUrl("https://toolbox.google.com/factcheck/explorer/search/list:false;query:" + encoded);
        } catch (Exception ignored) {
        }

        return result;
    }

    public NaiveBayesClassifier getClassifier() {
        return classifier;
    }

    public boolean isTrained() {
        return isTrained;
    }
}
