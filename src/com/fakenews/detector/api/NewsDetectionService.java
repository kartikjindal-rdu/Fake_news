package com.fakenews.detector.api;

import com.fakenews.detector.classifier.FakeNewsDetector;
import com.fakenews.detector.data.HistoryManager;
import com.fakenews.detector.model.PredictionResult;

/**
 * Headless Application Service for Fake News Detection.
 * Designed for plug-and-play integration into Android apps (Android Studio)
 * or Spring Boot / Micronaut REST APIs.
 *
 * Example Android Usage:
 *   NewsDetectionService service = NewsDetectionService.getInstance();
 *   PredictionResult result = service.detectNews(title, body, url);
 *   String json = result.toJson();
 */
public class NewsDetectionService {

    private static NewsDetectionService instance;
    private final FakeNewsDetector detector;

    private NewsDetectionService() {
        this.detector = new FakeNewsDetector();
        this.detector.trainWithDefaults();
    }

    public static synchronized NewsDetectionService getInstance() {
        if (instance == null) {
            instance = new NewsDetectionService();
        }
        return instance;
    }

    /**
     * Primary entry point to analyze news text.
     */
    public PredictionResult detectNews(String title, String content, String sourceUrl) {
        PredictionResult result = detector.analyze(title, content, sourceUrl);
        // Log to session history
        HistoryManager.recordScan(title, sourceUrl, result);
        return result;
    }

    /**
     * Overload without URL.
     */
    public PredictionResult detectNews(String title, String content) {
        return detectNews(title, content, "");
    }

    public FakeNewsDetector getDetector() {
        return detector;
    }
}
