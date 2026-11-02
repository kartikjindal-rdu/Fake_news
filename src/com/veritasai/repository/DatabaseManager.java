package com.veritasai.repository;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

/**
 * Manages database connections for Veritas AI scan history auditing.
 * Automatically initializes SQLite schema or falls back gracefully to in-memory store.
 */
public class DatabaseManager {

    private static final String DB_URL = "jdbc:sqlite:veritas_scans.db";
    private static boolean sqliteDriverAvailable = false;

    static {
        try {
            Class.forName("org.sqlite.JDBC");
            sqliteDriverAvailable = true;
            initSchema();
        } catch (ClassNotFoundException e) {
            sqliteDriverAvailable = false;
        }
    }

    private static void initSchema() {
        if (!sqliteDriverAvailable) return;
        String sql = "CREATE TABLE IF NOT EXISTS scan_history (" +
                     "scan_id TEXT PRIMARY KEY, " +
                     "timestamp TEXT, " +
                     "headline TEXT, " +
                     "source_domain TEXT, " +
                     "prediction TEXT, " +
                     "fake_probability REAL, " +
                     "risk_score REAL, " +
                     "user_notes TEXT)";
        try (Connection conn = getConnection(); Statement stmt = conn.createStatement()) {
            stmt.execute(sql);
        } catch (Exception ignored) {
        }
    }

    public static Connection getConnection() throws Exception {
        if (!sqliteDriverAvailable) {
            throw new IllegalStateException("SQLite JDBC Driver is not present on classpath; using in-memory repository.");
        }
        return DriverManager.getConnection(DB_URL);
    }

    public static boolean isSqliteDriverAvailable() {
        return sqliteDriverAvailable;
    }
}
