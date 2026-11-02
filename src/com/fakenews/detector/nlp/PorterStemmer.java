package com.fakenews.detector.nlp;

/**
 * Standard lightweight Porter Stemmer implementation in pure Java for word normalization.
 */
public class PorterStemmer {
    
    public static String stem(String word) {
        if (word == null || word.length() < 3) {
            return word;
        }
        
        String s = word.toLowerCase();
        
        // Step 1: Plurals and basic suffixes
        if (s.endsWith("sses")) {
            s = s.substring(0, s.length() - 2);
        } else if (s.endsWith("ies")) {
            s = s.substring(0, s.length() - 2);
        } else if (s.endsWith("ss")) {
            // Keep ss
        } else if (s.endsWith("s")) {
            s = s.substring(0, s.length() - 1);
        }

        if (s.endsWith("eed")) {
            if (s.length() > 4) {
                s = s.substring(0, s.length() - 1);
            }
        } else if ((s.endsWith("ed") || s.endsWith("ing")) && hasVowel(s.substring(0, s.length() - (s.endsWith("ed") ? 2 : 3)))) {
            s = s.substring(0, s.length() - (s.endsWith("ed") ? 2 : 3));
            if (s.endsWith("at") || s.endsWith("bl") || s.endsWith("iz")) {
                s += "e";
            }
        }

        // Step 2: Suffix replacements
        if (s.endsWith("ational")) s = s.substring(0, s.length() - 5) + "e";
        else if (s.endsWith("tional")) s = s.substring(0, s.length() - 2);
        else if (s.endsWith("izer")) s = s.substring(0, s.length() - 1);
        else if (s.endsWith("ator")) s = s.substring(0, s.length() - 2) + "e";
        else if (s.endsWith("alism")) s = s.substring(0, s.length() - 3);
        else if (s.endsWith("iveness")) s = s.substring(0, s.length() - 4);

        // Step 3: Remove common endings
        if (s.endsWith("ful") || s.endsWith("ness") || s.endsWith("less") || s.endsWith("ment") || s.endsWith("able") || s.endsWith("ible")) {
            if (s.length() > 6) {
                if (s.endsWith("ful") || s.endsWith("able") || s.endsWith("ible") || s.endsWith("less") || s.endsWith("ment")) {
                    s = s.substring(0, s.length() - 4);
                } else if (s.endsWith("ness")) {
                    s = s.substring(0, s.length() - 4);
                }
            }
        }

        return s;
    }

    private static boolean hasVowel(String str) {
        for (char c : str.toCharArray()) {
            if ("aeiou".indexOf(c) != -1) {
                return true;
            }
        }
        return false;
    }
}
