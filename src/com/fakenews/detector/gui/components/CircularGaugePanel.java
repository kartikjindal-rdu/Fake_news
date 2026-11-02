package com.fakenews.detector.gui.components;

import javax.swing.*;
import java.awt.*;

/**
 * Custom modern circular progress gauge component displaying confidence or risk percentage.
 */
public class CircularGaugePanel extends JPanel {

    private double percentage = 0.0;
    private String subtitle = "AI Confidence";
    private Color arcColor = new Color(37, 99, 235);
    private Color trackColor = new Color(226, 232, 240);
    private Color textColor = new Color(15, 23, 42);

    public CircularGaugePanel() {
        setPreferredSize(new Dimension(140, 140));
        setOpaque(false);
    }

    public void setValue(double pct, String subtitle, Color color) {
        this.percentage = Math.max(0.0, Math.min(100.0, pct));
        this.subtitle = subtitle;
        this.arcColor = color;
        repaint();
    }

    public void setThemeColors(Color track, Color text) {
        this.trackColor = track;
        this.textColor = text;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g.create();
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        int size = Math.min(getWidth(), getHeight()) - 16;
        int x = (getWidth() - size) / 2;
        int y = (getHeight() - size) / 2;
        int strokeWidth = 10;

        // Draw track background arc
        g2.setStroke(new BasicStroke(strokeWidth, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
        g2.setColor(trackColor);
        g2.drawArc(x + strokeWidth / 2, y + strokeWidth / 2, size - strokeWidth, size - strokeWidth, 0, 360);

        // Draw active progress arc (starts from top 90 deg)
        int angle = (int) Math.round((percentage / 100.0) * 360);
        g2.setColor(arcColor);
        g2.drawArc(x + strokeWidth / 2, y + strokeWidth / 2, size - strokeWidth, size - strokeWidth, 90, -angle);

        // Draw percentage text
        g2.setColor(textColor);
        g2.setFont(new Font("Segoe UI", Font.BOLD, 18));
        String valStr = String.format("%.0f%%", percentage);
        FontMetrics fm = g2.getFontMetrics();
        int valX = (getWidth() - fm.stringWidth(valStr)) / 2;
        int valY = (getHeight() / 2) + 2;
        g2.drawString(valStr, valX, valY);

        // Draw subtitle text
        g2.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        g2.setColor(new Color(148, 163, 184));
        FontMetrics fmSub = g2.getFontMetrics();
        int subX = (getWidth() - fmSub.stringWidth(subtitle)) / 2;
        int subY = valY + 16;
        g2.drawString(subtitle, subX, subY);

        g2.dispose();
    }
}
