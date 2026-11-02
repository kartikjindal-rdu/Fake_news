package com.fakenews.detector.model;

/**
 * Represents a news article or headline with its metadata and label.
 */
public class NewsArticle {
    private String title;
    private String content;
    private String sourceUrl;
    private String category;
    private String label; // "REAL" or "FAKE"

    public NewsArticle(String title, String content, String sourceUrl, String category, String label) {
        this.title = (title != null) ? title.trim() : "";
        this.content = (content != null) ? content.trim() : "";
        this.sourceUrl = (sourceUrl != null) ? sourceUrl.trim() : "";
        this.category = (category != null) ? category.trim() : "General";
        this.label = (label != null) ? label.toUpperCase().trim() : "UNKNOWN";
    }

    public NewsArticle(String title, String content, String label) {
        this(title, content, "", "General", label);
    }

    public NewsArticle(String fullText, String label) {
        this("", fullText, "", "General", label);
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getSourceUrl() {
        return sourceUrl;
    }

    public void setSourceUrl(String sourceUrl) {
        this.sourceUrl = sourceUrl;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public String getFullCombinedText() {
        if (title.isEmpty()) {
            return content;
        }
        if (content.isEmpty()) {
            return title;
        }
        return title + " " + content;
    }

    @Override
    public String toString() {
        return "NewsArticle [label=" + label + ", category=" + category + ", title=" + title + "]";
    }
}
