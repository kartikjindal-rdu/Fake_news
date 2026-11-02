package com.fakenews.detector.gui.components;

import javax.swing.*;
import java.awt.*;

/**
 * Custom modern panel with rounded corners and anti-aliased borders.
 */
public class RoundedPanel extends JPanel {

    private int cornerRadius = 14;
    private Color backgroundColor;
    private Color borderColor;

    public RoundedPanel(int radius, Color bg, Color border) {
        super();
        this.cornerRadius = radius;
        this.backgroundColor = bg;
        this.borderColor = border;
        setOpaque(false);
    }

    public RoundedPanel(Color bg, Color border) {
        this(14, bg, border);
    }

    public void setCustomColors(Color bg, Color border) {
        this.backgroundColor = bg;
        this.borderColor = border;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g.create();
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        int width = getWidth();
        int height = getHeight();

        // Fill background
        g2.setColor(backgroundColor != null ? backgroundColor : getBackground());
        g2.fillRoundRect(0, 0, width - 1, height - 1, cornerRadius, cornerRadius);

        // Draw border
        if (borderColor != null) {
            g2.setColor(borderColor);
            g2.drawRoundRect(0, 0, width - 1, height - 1, cornerRadius, cornerRadius);
        }

        g2.dispose();
    }
}
