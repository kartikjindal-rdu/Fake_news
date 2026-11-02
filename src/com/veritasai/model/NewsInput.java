package com.veritasai.model;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Encapsulates the user input for news analysis.
 */
public class NewsInput {

    private String headline;
    private String content;
    private String sourceUrl;
    private File screenshotFile;
    private String timestamp;

    public NewsInput(String headline, String content, String sourceUrl, File screenshotFile) {
        this.headline = (headline != null) ? headline.trim() : "";
        this.content = (content != null) ? content.trim() : "";
        this.sourceUrl = (sourceUrl != null) ? sourceUrl.trim() : "";
        this.screenshotFile = screenshotFile;
        this.timestamp = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
    }

    public NewsInput(String headline, String content, String sourceUrl) {
        this(headline, content, sourceUrl, null);
    }

    public NewsInput(String headline, String content) {
        this(headline, content, "", null);
    }

    public String getHeadline() { return headline; }
    public void setHeadline(String headline) { this.headline = headline; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getSourceUrl() { return sourceUrl; }
    public void setSourceUrl(String sourceUrl) { this.sourceUrl = sourceUrl; }

    public File getScreenshotFile() { return screenshotFile; }
    public void setScreenshotFile(File screenshotFile) { this.screenshotFile = screenshotFile; }

    public String getTimestamp() { return timestamp; }

    public String getFullCombinedText() {
        if (headline.isEmpty()) return content;
        if (content.isEmpty()) return headline;
        return headline + " " + content;
    }
}
