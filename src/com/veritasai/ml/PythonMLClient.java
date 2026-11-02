package com.veritasai.ml;

import com.veritasai.model.ModelMetrics;
import com.veritasai.model.NewsInput;
import com.veritasai.util.Constants;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

/**
 * REST API client for connecting to a Python FastAPI Machine Learning microservice.
 * Handles timeouts, network errors, health checks, and fallback to embedded ML.
 */
public class PythonMLClient implements MLModelService {

    private String baseUrl;
    private final MLModelService fallbackService;

    public PythonMLClient(String baseUrl) {
        this.baseUrl = (baseUrl != null && !baseUrl.isEmpty()) ? baseUrl : Constants.DEFAULT_PYTHON_ML_URL;
        this.fallbackService = new NaiveBayesModelService();
    }

    public PythonMLClient() {
        this(Constants.DEFAULT_PYTHON_ML_URL);
    }

    @Override
    public boolean isServiceAvailable() {
        try {
            URL url = new URL(baseUrl + "/health");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(1500);
            conn.setReadTimeout(1500);
            int code = conn.getResponseCode();
            return code == 200;
        } catch (Exception e) {
            return false;
        }
    }

    @Override
    public Map<String, Double> predict(NewsInput input) {
        if (!isServiceAvailable()) {
            // Graceful fallback to embedded Java Naive Bayes
            return fallbackService.predict(input);
        }

        try {
            URL url = new URL(baseUrl + "/predict");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setConnectTimeout(3000);
            conn.setReadTimeout(3000);
            conn.setDoOutput(true);

            String jsonPayload = String.format("{\"headline\":\"%s\",\"content\":\"%s\",\"url\":\"%s\"}",
                    escapeJson(input.getHeadline()),
                    escapeJson(input.getContent()),
                    escapeJson(input.getSourceUrl()));

            try (OutputStream os = conn.getOutputStream()) {
                os.write(jsonPayload.getBytes(StandardCharsets.UTF_8));
            }

            int code = conn.getResponseCode();
            if (code == 200) {
                try (BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8))) {
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = br.readLine()) != null) response.append(line);

                    // Parse simple json response {fake_prob: 0.85, real_prob: 0.15}
                    return parseProbabilities(response.toString());
                }
            }
        } catch (Exception ignored) {
        }

        return fallbackService.predict(input);
    }

    private Map<String, Double> parseProbabilities(String json) {
        Map<String, Double> map = new HashMap<>();
        try {
            if (json.contains("\"fake_prob\"")) {
                String[] parts = json.split("\"fake_prob\"\\s*:\\s*");
                double fake = Double.parseDouble(parts[1].split("[,}]")[0].trim());
                map.put("FAKE", fake);
                map.put("REAL", 1.0 - fake);
                return map;
            }
        } catch (Exception ignored) {
        }
        return fallbackService.predict(new NewsInput("", ""));
    }

    private String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "");
    }

    @Override
    public void trainModel() {
        fallbackService.trainModel();
    }

    @Override
    public ModelMetrics evaluateModel() {
        return fallbackService.evaluateModel();
    }

    @Override
    public ModelMetrics getModelMetrics() {
        return fallbackService.getModelMetrics();
    }

    public String getBaseUrl() { return baseUrl; }
    public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }
}
