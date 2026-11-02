package com.veritasai.repository;

import com.veritasai.model.ScanRecord;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * SQLite DAO implementation with automatic synchronized memory backing.
 */
public class SQLiteScanRepository implements ScanRepository {

    private final List<ScanRecord> memoryStore = new ArrayList<>();

    @Override
    public synchronized void save(ScanRecord record) {
        memoryStore.removeIf(r -> r.getScanId().equals(record.getScanId()));
        memoryStore.add(0, record);

        if (DatabaseManager.isSqliteDriverAvailable()) {
            String sql = "INSERT OR REPLACE INTO scan_history (scan_id, timestamp, headline, source_domain, prediction, fake_probability, risk_score, user_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
            try (Connection conn = DatabaseManager.getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setString(1, record.getScanId());
                ps.setString(2, record.getTimestamp());
                ps.setString(3, record.getHeadline());
                ps.setString(4, record.getSourceDomain());
                ps.setString(5, record.getPrediction());
                ps.setDouble(6, record.getFakeProbability());
                ps.setDouble(7, record.getRiskScore());
                ps.setString(8, record.getUserNotes());
                ps.executeUpdate();
            } catch (Exception ignored) {
            }
        }
    }

    @Override
    public synchronized List<ScanRecord> getAll() {
        if (DatabaseManager.isSqliteDriverAvailable()) {
            List<ScanRecord> list = new ArrayList<>();
            String sql = "SELECT * FROM scan_history ORDER BY timestamp DESC";
            try (Connection conn = DatabaseManager.getConnection(); Statement stmt = conn.createStatement(); ResultSet rs = stmt.executeQuery(sql)) {
                while (rs.next()) {
                    list.add(new ScanRecord(
                        rs.getString("scan_id"),
                        rs.getString("timestamp"),
                        rs.getString("headline"),
                        rs.getString("source_domain"),
                        rs.getString("prediction"),
                        rs.getDouble("fake_probability"),
                        rs.getDouble("risk_score"),
                        rs.getString("user_notes")
                    ));
                }
                return list;
            } catch (Exception ignored) {
            }
        }
        return Collections.unmodifiableList(new ArrayList<>(memoryStore));
    }

    @Override
    public synchronized ScanRecord getById(String scanId) {
        for (ScanRecord r : memoryStore) {
            if (r.getScanId().equals(scanId)) return r;
        }
        return null;
    }

    @Override
    public synchronized boolean delete(String scanId) {
        boolean removed = memoryStore.removeIf(r -> r.getScanId().equals(scanId));
        if (DatabaseManager.isSqliteDriverAvailable()) {
            String sql = "DELETE FROM scan_history WHERE scan_id = ?";
            try (Connection conn = DatabaseManager.getConnection(); PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setString(1, scanId);
                ps.executeUpdate();
            } catch (Exception ignored) {
            }
        }
        return removed;
    }

    @Override
    public synchronized void clearAll() {
        memoryStore.clear();
        if (DatabaseManager.isSqliteDriverAvailable()) {
            try (Connection conn = DatabaseManager.getConnection(); Statement stmt = conn.createStatement()) {
                stmt.execute("DELETE FROM scan_history");
            } catch (Exception ignored) {
            }
        }
    }

    @Override
    public synchronized List<ScanRecord> search(String query, String predictionFilter) {
        List<ScanRecord> all = getAll();
        List<ScanRecord> filtered = new ArrayList<>();
        String q = (query != null) ? query.toLowerCase().trim() : "";
        boolean filterAll = (predictionFilter == null || predictionFilter.equalsIgnoreCase("ALL") || predictionFilter.isEmpty());

        for (ScanRecord r : all) {
            boolean matchQuery = q.isEmpty() || r.getHeadline().toLowerCase().contains(q) ||
                                 r.getSourceDomain().toLowerCase().contains(q) ||
                                 r.getScanId().toLowerCase().contains(q);
            boolean matchPred = filterAll || r.getPrediction().equalsIgnoreCase(predictionFilter);

            if (matchQuery && matchPred) {
                filtered.add(r);
            }
        }
        return filtered;
    }

    @Override
    public synchronized void exportToCsv(File targetFile) throws IOException {
        List<ScanRecord> all = getAll();
        try (FileWriter writer = new FileWriter(targetFile)) {
            writer.write("ScanID,Timestamp,Headline,SourceDomain,Prediction,FakeProbability,RiskScore,UserNotes\n");
            for (ScanRecord r : all) {
                writer.write(r.toCsvRow() + "\n");
            }
        }
    }
}
