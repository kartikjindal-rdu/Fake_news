package com.fakenews.detector.data;

import com.fakenews.detector.model.HistoryRecord;
import com.fakenews.detector.model.PredictionResult;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;
import java.util.UUID;

/**
 * Manages scan session history and interfaces with the permanent DatabaseManager.
 */
public class HistoryManager {

    private static final DatabaseManager db = DatabaseManager.getInstance();

    public static synchronized void recordScan(String title, String sourceUrl, PredictionResult result) {
        String id = "VERITAS-2026-" + UUID.randomUUID().toString().substring(0, 6).toUpperCase();
        HistoryRecord record = new HistoryRecord(
                id,
                title,
                sourceUrl,
                result.getVerdict().name(),
                result.getConfidenceScore(),
                result.getFakeProbability(),
                result.getRealProbability()
        );
        db.saveScan(record);
    }

    public static synchronized void saveRecord(HistoryRecord record) {
        db.saveScan(record);
    }

    public static synchronized List<HistoryRecord> getHistory() {
        return db.queryScans("", "ALL", "ALL", "ALL", "timestamp", "DESC");
    }

    public static synchronized void clearHistory() {
        db.clearAllScans();
    }

    public static synchronized boolean deleteScan(String scanId) {
        return db.deleteScan(scanId);
    }

    public static synchronized HistoryRecord getScan(String scanId) {
        return db.getScanById(scanId);
    }

    public static synchronized void exportToCSV(File file) throws IOException {
        try (FileWriter writer = new FileWriter(file)) {
            writer.write(db.exportCSV());
        }
    }
}
