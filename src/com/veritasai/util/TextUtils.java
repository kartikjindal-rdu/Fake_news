package com.veritasai.util;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * String and regex analysis utilities.
 */
public class TextUtils {

    public static int countWords(String text) {
        if (text == null || text.trim().isEmpty()) return 0;
        return text.trim().split("\\s+").length;
    }

    public static int countSentences(String text) {
        if (text == null || text.trim().isEmpty()) return 0;
        String[] s = text.trim().split("[.!?]+");
        return Math.max(1, s.length);
    }

    public static double calculateCapsRatio(String text) {
        if (text == null || text.isEmpty()) return 0.0;
        int upper = 0, letters = 0;
        for (char c : text.toCharArray()) {
            if (Character.isLetter(c)) {
                letters++;
                if (Character.isUpperCase(c)) upper++;
            }
        }
        return (letters > 0) ? (double) upper / letters : 0.0;
    }

    public static int countPunctuationClusters(String text) {
        if (text == null || text.isEmpty()) return 0;
        Pattern p = Pattern.compile("([!?]{2,})");
        Matcher m = p.matcher(text);
        int count = 0;
        while (m.find()) count++;
        return count;
    }

    public static List<String> extractSentences(String text) {
        List<String> list = new ArrayList<>();
        if (text == null || text.trim().isEmpty()) return list;
        String[] parts = text.split("(?<=[.!?])\\s+");
        for (String p : parts) {
            String s = p.trim();
            if (!s.isEmpty()) list.add(s);
        }
        return list;
    }
}
