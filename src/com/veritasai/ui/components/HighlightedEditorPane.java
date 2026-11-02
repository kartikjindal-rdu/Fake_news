package com.veritasai.ui.components;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Custom text component capable of highlighting suspicious, sensational,
 * clickbait, and urgency terms with interactive hover explanations.
 */
public class HighlightedEditorPane extends JEditorPane {

    private static final long serialVersionUID = 1L;

    public HighlightedEditorPane() {
        setContentType("text/html");
        setEditable(false);
        setBorder(new EmptyBorder(8, 8, 8, 8));
    }

    public void renderTextWithHighlights(String rawText, Map<String, String> highlights, boolean isDarkMode) {
        if (rawText == null || rawText.isEmpty()) {
            setText("<html><body style='font-family: Segoe UI; color: #94a3b8; font-size: 11pt;'><i>No text analyzed yet.</i></body></html>");
            return;
        }

        String bgHex = isDarkMode ? "#0f172a" : "#f8fafc";
        String textHex = isDarkMode ? "#f8fafc" : "#1e293b";
        String highlightBg = isDarkMode ? "#7f1d1d" : "#fee2e2";
        String highlightFg = isDarkMode ? "#fecaca" : "#991b1b";

        String escapedText = rawText.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>");

        if (highlights != null) {
            for (Map.Entry<String, String> entry : highlights.entrySet()) {
                String keyword = entry.getKey();
                String reason = entry.getValue().replace("\"", "&quot;");

                Pattern p = Pattern.compile("(?i)\\b(" + Pattern.quote(keyword) + ")\\b");
                Matcher m = p.matcher(escapedText);

                StringBuffer sb = new StringBuffer();
                while (m.find()) {
                    String matched = m.group(1);
                    String replacement = String.format(
                        "<span title='%s' style='background-color: %s; color: %s; font-weight: bold; border-radius: 3px; padding: 1px 4px; border: 1px solid %s;'>%s</span>",
                        reason, highlightBg, highlightFg, highlightFg, matched
                    );
                    m.appendReplacement(sb, Matcher.quoteReplacement(replacement));
                }
                m.appendTail(sb);
                escapedText = sb.toString();
            }
        }

        String html = String.format(
            "<html><body style='font-family: Segoe UI, sans-serif; background-color: %s; color: %s; font-size: 11pt; line-height: 1.5;'>%s</body></html>",
            bgHex, textHex, escapedText
        );

        setText(html);
        setCaretPosition(0);
    }
}
