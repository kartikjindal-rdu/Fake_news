package com.fakenews.detector.gui;

import java.awt.Color;
import java.awt.Font;

/**
 * Manages color schemes and fonts for Dark and Light themes.
 */
public class ThemeManager {

    private static boolean isDarkMode = false;

    // Fonts
    public static final Font FONT_TITLE = new Font("Segoe UI", Font.BOLD, 22);
    public static final Font FONT_SUBTITLE = new Font("Segoe UI", Font.PLAIN, 13);
    public static final Font FONT_SECTION = new Font("Segoe UI", Font.BOLD, 15);
    public static final Font FONT_BOLD_13 = new Font("Segoe UI", Font.BOLD, 13);
    public static final Font FONT_REGULAR_13 = new Font("Segoe UI", Font.PLAIN, 13);
    public static final Font FONT_REGULAR_12 = new Font("Segoe UI", Font.PLAIN, 12);
    public static final Font FONT_SMALL_11 = new Font("Segoe UI", Font.PLAIN, 11);
    public static final Font FONT_CODE = new Font("Consolas", Font.PLAIN, 12);

    public static boolean isDarkMode() {
        return isDarkMode;
    }

    public static void setDarkMode(boolean dark) {
        isDarkMode = dark;
    }

    // Dynamic Colors based on theme
    public static Color getBackground() {
        return isDarkMode ? new Color(15, 23, 42) : new Color(241, 245, 249);
    }

    public static Color getCardBackground() {
        return isDarkMode ? new Color(30, 41, 59) : Color.WHITE;
    }

    public static Color getCardBorder() {
        return isDarkMode ? new Color(51, 65, 85) : new Color(226, 232, 240);
    }

    public static Color getTextPrimary() {
        return isDarkMode ? new Color(248, 250, 252) : new Color(15, 23, 42);
    }

    public static Color getTextSecondary() {
        return isDarkMode ? new Color(148, 163, 184) : new Color(100, 116, 139);
    }

    public static Color getInputBackground() {
        return isDarkMode ? new Color(15, 23, 42) : new Color(248, 250, 252);
    }

    public static Color getInputBorder() {
        return isDarkMode ? new Color(71, 85, 105) : new Color(203, 213, 225);
    }

    // Static Accent Colors
    public static final Color ACCENT_BLUE = new Color(37, 99, 235);
    public static final Color ACCENT_GREEN = new Color(16, 185, 129);
    public static final Color ACCENT_RED = new Color(239, 68, 68);
    public static final Color ACCENT_ORANGE = new Color(245, 158, 11);
    public static final Color ACCENT_PURPLE = new Color(139, 92, 246);
}
