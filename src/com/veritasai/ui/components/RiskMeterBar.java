package com.veritasai.ui.components;

import com.veritasai.util.Constants.RiskLevel;

import javax.swing.*;
import java.awt.*;

/**
 * Custom 4-tier segmented risk meter bar (LOW, MODERATE, HIGH, CRITICAL).
 */
public class RiskMeterBar extends JPanel {

    private static final long serialVersionUID = 1L;

    private double riskScore = 0.0;
    private RiskLevel riskLevel = RiskLevel.LOW;

    public RiskMeterBar() {
        setPreferredSize(new Dimension(280, 48));
        setOpaque(false);
    }

    public void setRisk(double score, RiskLevel level) {
        this.riskScore = Math.max(0.0, Math.min(100.0, score));
        this.riskLevel = level;
        repaint();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g.create();
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        int width = getWidth() - 10;
        int barHeight = 16;
        int y = 20;

        // Draw 4 segments
        int segW = width / 4;
        Color[] colors = {
            new Color(16, 185, 129), // Low - Green
            new Color(245, 158, 11), // Moderate - Yellow/Amber
            new Color(249, 115, 22), // High - Orange
            new Color(239, 68, 68)   // Critical - Red
        };

        for (int i = 0; i < 4; i++) {
            g2.setColor(colors[i]);
            g2.fillRoundRect(5 + (i * segW), y, segW - 2, barHeight, 6, 6);
        }

        // Labels below segments
        g2.setFont(new Font("Segoe UI", Font.BOLD, 9));
        g2.setColor(new Color(100, 116, 139));
        g2.drawString("LOW", 10, y + barHeight + 10);
        g2.drawString("MODERATE", 10 + segW, y + barHeight + 10);
        g2.drawString("HIGH", 10 + (segW * 2), y + barHeight + 10);
        g2.drawString("CRITICAL", 10 + (segW * 3), y + barHeight + 10);

        // Draw pointer indicator
        int pointerX = 5 + (int) ((riskScore / 100.0) * width);
        pointerX = Math.max(5, Math.min(5 + width, pointerX));

        g2.setColor(riskLevel.getColor());
        int[] xPoints = {pointerX, pointerX - 6, pointerX + 6};
        int[] yPoints = {y + barHeight, y - 6, y - 6};
        g2.fillPolygon(xPoints, yPoints, 3);

        // Draw current score label at top
        g2.setFont(new Font("Segoe UI", Font.BOLD, 12));
        String text = String.format("%s (%.1f/100)", riskLevel.getLabel(), riskScore);
        FontMetrics fm = g2.getFontMetrics();
        g2.drawString(text, (getWidth() - fm.stringWidth(text)) / 2, 12);

        g2.dispose();
    }
}
