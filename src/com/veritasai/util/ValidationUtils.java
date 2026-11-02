package com.veritasai.util;

import java.net.URI;
import java.util.regex.Pattern;

/**
 * Validation utilities for news claims, URLs, and file inputs.
 */
public class ValidationUtils {

    private static final Pattern URL_PATTERN = Pattern.compile(
        "^(https?://)?([\\da-z.-]+)\\.([a-z.]{2,6})([/\\w .-]*)*/?$",
        Pattern.CASE_INSENSITIVE
    );

    public static boolean isValidUrl(String url) {
        if (url == null || url.trim().isEmpty()) return false;
        try {
            String s = url.trim();
            if (!s.startsWith("http://") && !s.startsWith("https://")) {
                s = "https://" + s;
            }
            URI uri = new URI(s);
            return uri.getHost() != null && uri.getHost().contains(".");
        } catch (Exception e) {
            return false;
        }
    }

    public static boolean isHttps(String url) {
        if (url == null) return false;
        return url.trim().toLowerCase().startsWith("https://");
    }

    public static String sanitize(String input) {
        if (input == null) return "";
        return input.trim().replaceAll("[\\r\\n]+", " ");
    }
}
