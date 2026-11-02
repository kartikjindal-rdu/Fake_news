package com.fakenews.detector.data;

import com.fakenews.detector.model.NewsArticle;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Utility for loading and parsing news datasets from CSV or text files.
 */
public class DatasetLoader {

    /**
     * Loads news articles from a standard CSV format (title,content,label or text,label).
     */
    public static List<NewsArticle> loadFromCSV(File file) throws IOException {
        List<NewsArticle> articles = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String headerLine = reader.readLine();
            if (headerLine == null) {
                return articles;
            }

            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty()) continue;

                // Simple CSV parsing handling comma separators
                String[] parts = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", -1);
                if (parts.length >= 3) {
                    String title = stripQuotes(parts[0]);
                    String text = stripQuotes(parts[1]);
                    String label = stripQuotes(parts[2]).toUpperCase();
                    articles.add(new NewsArticle(title, text, label));
                } else if (parts.length == 2) {
                    String text = stripQuotes(parts[0]);
                    String label = stripQuotes(parts[1]).toUpperCase();
                    articles.add(new NewsArticle("", text, label));
                }
            }
        }
        return articles;
    }

    private static String stripQuotes(String s) {
        if (s == null) return "";
        s = s.trim();
        if (s.startsWith("\"") && s.endsWith("\"") && s.length() >= 2) {
            s = s.substring(1, s.length() - 1);
        }
        return s.replace("\"\"", "\"");
    }
}
