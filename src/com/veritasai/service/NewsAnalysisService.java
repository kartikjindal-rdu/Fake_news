package com.veritasai.service;

import com.veritasai.ml.MLModelService;
import com.veritasai.ml.NaiveBayesModelService;
import com.veritasai.model.*;
import com.veritasai.model.NewsAnalysisResult.PredictionVerdict;
import com.veritasai.repository.ScanRepository;
import com.veritasai.repository.SQLiteScanRepository;
import com.veritasai.util.Constants.RiskLevel;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Map;
import java.util.UUID;

/**
 * Enterprise implementation of the 10-step News Analysis Pipeline.
 */
public class NewsAnalysisService implements NewsAnalyzer {

    private static NewsAnalysisService instance;
    private final MLModelService mlService;
    private final ScanRepository repository;

    private NewsAnalysisService() {
        this.mlService = new NaiveBayesModelService();
        this.repository = new SQLiteScanRepository();
    }

    public static synchronized NewsAnalysisService getInstance() {
        if (instance == null) {
            instance = new NewsAnalysisService();
        }
        return instance;
    }

    @Override
    public NewsAnalysisResult analyze(NewsInput input, AnalysisProgressListener listener) {
        NewsAnalysisResult result = new NewsAnalysisResult();
        String scanId = "VRT-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
        result.setScanId(scanId);
        result.setTimestamp(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));

        // STEP 1: Validating Input
        if (listener != null) listener.onProgressStep(1, "Validating News Input & Metadata...");
        String headline = (input != null && input.getHeadline() != null) ? input.getHeadline().trim() : "";
        String content = (input != null && input.getContent() != null) ? input.getContent().trim() : "";
        String url = (input != null && input.getSourceUrl() != null) ? input.getSourceUrl().trim() : "";

        // STEP 2: Extracting Content
        if (listener != null) listener.onProgressStep(2, "Extracting Text & Assertions...");
        String combined = headline + " " + content;

        // STEP 3: Cleaning Text
        if (listener != null) listener.onProgressStep(3, "Sanitizing & Normalizing Text Tokens...");
        String cleanedText = TextPreprocessor.cleanText(combined);

        // STEP 4: NLP Analysis & Readability
        if (listener != null) listener.onProgressStep(4, "Performing Linguistic & Readability Scoring...");
        ReadabilityAnalyzer.ReadabilityData readData = ReadabilityAnalyzer.analyze(combined);
        result.setReadabilityScore(readData.score);
        result.setReadabilityLevel(readData.level);
        result.setWordCount(readData.wordCount);
        result.setSentenceCount(readData.sentenceCount);

        // STEP 5: Detecting Clickbait
        if (listener != null) listener.onProgressStep(5, "Evaluating Clickbait Patterns & Curiosity Gaps...");
        ClickbaitAnalyzer.ClickbaitResult clickbait = ClickbaitAnalyzer.analyze(headline, content);
        result.setClickbaitScore(clickbait.score);

        // STEP 6: Detecting Emotional Manipulation & Sensationalism
        if (listener != null) listener.onProgressStep(6, "Scanning Emotional Manipulation & Outrage Triggers...");
        SensationalismAnalyzer.SensationalismResult sensationalism = SensationalismAnalyzer.analyze(combined);
        result.setSensationalismScore(sensationalism.score);

        EmotionAnalyzer.EmotionResult emotion = EmotionAnalyzer.analyze(combined);
        result.setEmotionalManipulationScore(emotion.score);
        result.setEmotionalTone(emotion.dominantTone);

        // Language Manipulation Score (Blend of Clickbait + Sensationalism + Emotion)
        double langManip = (clickbait.score * 0.35) + (sensationalism.score * 0.35) + (emotion.score * 0.30);
        result.setLanguageManipulationScore(Math.round(langManip * 10.0) / 10.0);

        // Source Domain Analysis
        DomainAnalysis domainAnalysis = DomainAnalyzer.analyze(url);
        result.setDomainAnalysis(domainAnalysis);
        result.setSourceTrustScore(domainAnalysis.getSourceTrustScore());

        // STEP 7: Running Fake News Classifier
        if (listener != null) listener.onProgressStep(7, "Executing Machine Learning Classification Model...");
        Map<String, Double> mlProbs = mlService.predict(input);
        double rawFakeProb = mlProbs.getOrDefault("FAKE", 0.5) * 100.0;

        // Ensemble calculation
        double sourceModifier = (100.0 - domainAnalysis.getSourceTrustScore()) * 0.15;
        double adjustedFakeProb = (rawFakeProb * 0.55) + (langManip * 0.30) + sourceModifier;
        adjustedFakeProb = Math.max(0.0, Math.min(100.0, adjustedFakeProb));

        double fakeProb = Math.round(adjustedFakeProb * 10.0) / 10.0;
        double realProb = Math.round((100.0 - fakeProb) * 10.0) / 10.0;
        result.setFakeProbability(fakeProb);
        result.setRealProbability(realProb);

        // Credibility score is inverted fake probability with domain trust factor
        double cred = (realProb * 0.70) + (domainAnalysis.getSourceTrustScore() * 0.30);
        result.setCredibilityScore(Math.round(cred * 10.0) / 10.0);

        // Confidence calculation
        double mlConfidence = Math.max(fakeProb, realProb);
        double heuristicConvergence = 100.0 - Math.abs(fakeProb - langManip);
        double confidence = ConfidenceCalculator.calculate(mlConfidence, heuristicConvergence, readData.wordCount);
        result.setAiConfidence(confidence);

        // STEP 8: Calculating Risk Score & Verdict
        if (listener != null) listener.onProgressStep(8, "Computing Multi-Factor Risk Matrix...");
        RiskScoreCalculator.RiskEvaluation riskEval = RiskScoreCalculator.calculate(
                fakeProb, sensationalism.score, clickbait.score, emotion.score, domainAnalysis.getSourceTrustScore()
        );
        result.setRiskScore(riskEval.riskScore);
        result.setRiskLevel(riskEval.riskLevel);

        // Determine Verdict
        if (domainAnalysis.getEditorialCategory().contains("Satire")) {
            result.setVerdict(PredictionVerdict.SATIRE);
        } else if (fakeProb >= 65.0) {
            result.setVerdict(PredictionVerdict.LIKELY_FAKE);
        } else if (realProb >= 65.0) {
            result.setVerdict(PredictionVerdict.VERIFIED_REAL);
        } else {
            result.setVerdict(PredictionVerdict.SUSPICIOUS);
        }

        // STEP 9: Generating Explanation & Claim Extraction
        if (listener != null) listener.onProgressStep(9, "Extracting Assertions & Structuring Explanations...");
        ExplainabilityEngine.populateExplanations(result, clickbait, sensationalism, emotion, domainAnalysis);
        result.getExtractedClaims().addAll(ClaimExtractor.extractClaims(headline, content, result.getRiskLevel()));

        // Fact Check Search Link
        try {
            String q = !headline.isEmpty() ? headline : (content.length() > 60 ? content.substring(0, 60) : content);
            String encoded = URLEncoder.encode(q, StandardCharsets.UTF_8.toString());
            result.setFactCheckQueryUrl("https://toolbox.google.com/factcheck/explorer/search/list:false;query:" + encoded);
        } catch (Exception ignored) {
        }

        // STEP 10: Generating Final Report & Persisting to Repository
        if (listener != null) listener.onProgressStep(10, "Finalizing Audit Record & Synthesis...");
        ScanRecord record = new ScanRecord(
                result.getScanId(),
                result.getTimestamp(),
                !headline.isEmpty() ? headline : "Text Scan: " + (content.length() > 40 ? content.substring(0, 40) + "..." : content),
                domainAnalysis.getDomainName().isEmpty() ? "Direct Input" : domainAnalysis.getDomainName(),
                result.getVerdict().getLabel(),
                result.getFakeProbability(),
                result.getRiskScore(),
                "Analyzed by Veritas AI Enterprise Engine"
        );
        repository.save(record);

        return result;
    }

    public ScanRepository getRepository() { return repository; }
    public MLModelService getMlService() { return mlService; }
}
