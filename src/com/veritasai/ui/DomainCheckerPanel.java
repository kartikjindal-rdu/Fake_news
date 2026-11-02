package com.veritasai.ui;

import com.fakenews.detector.gui.ThemeManager;
import com.fakenews.detector.gui.components.RoundedPanel;
import com.veritasai.model.DomainAnalysis;
import com.veritasai.service.DomainAnalyzer;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import java.awt.*;

/**
 * Domain Credibility & Heuristic Security Checker Panel.
 */
public class DomainCheckerPanel extends JPanel {

    private static final long serialVersionUID = 1L;

    private JTextField domainInputField;
    private JLabel riskBadge;
    private JLabel domainNameLbl;
    private JLabel httpsLbl;
    private JLabel urlStructureLbl;
    private JLabel domainLengthLbl;
    private JLabel subdomainCountLbl;
    private JLabel trustScoreLbl;
    private JTextArea indicatorsArea;

    public DomainCheckerPanel() {
        setLayout(new BorderLayout(12, 12));
        setOpaque(false);
        setBorder(new EmptyBorder(10, 10, 10, 10));

        RoundedPanel card = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        card.setLayout(new BorderLayout(12, 12));
        card.setBorder(new EmptyBorder(16, 16, 16, 16));

        // Top Search Bar
        JPanel topBar = new JPanel(new BorderLayout(8, 8));
        topBar.setOpaque(false);

        JLabel title = new JLabel("🌐 Domain Structure & Credibility Inspector");
        title.setFont(ThemeManager.FONT_SECTION);
        title.setForeground(ThemeManager.getTextPrimary());

        JPanel searchRow = new JPanel(new BorderLayout(8, 0));
        searchRow.setOpaque(false);

        domainInputField = new JTextField("https://www.reuters.com/news/world");
        domainInputField.setFont(ThemeManager.FONT_REGULAR_13);
        domainInputField.setBorder(BorderFactory.createCompoundBorder(
            new LineBorder(ThemeManager.getInputBorder(), 1, true),
            new EmptyBorder(6, 10, 6, 10)
        ));

        JButton inspectBtn = new JButton("🔍 Evaluate Domain");
        styleButton(inspectBtn, ThemeManager.ACCENT_BLUE, Color.WHITE);
        inspectBtn.addActionListener(e -> runDomainCheck());

        searchRow.add(domainInputField, BorderLayout.CENTER);
        searchRow.add(inspectBtn, BorderLayout.EAST);

        topBar.add(title, BorderLayout.NORTH);
        topBar.add(searchRow, BorderLayout.SOUTH);

        // Center Split (Details on Left, Indicators on Right)
        JPanel detailsGrid = new JPanel(new GridLayout(1, 2, 12, 0));
        detailsGrid.setOpaque(false);

        // Left Info Card
        RoundedPanel leftInfo = new RoundedPanel(10, ThemeManager.getInputBackground(), ThemeManager.getCardBorder());
        leftInfo.setLayout(new BorderLayout(8, 8));
        leftInfo.setBorder(new EmptyBorder(12, 12, 12, 12));

        riskBadge = new JLabel("DOMAIN RISK: LOW", SwingConstants.CENTER);
        riskBadge.setFont(ThemeManager.FONT_BOLD_13);
        riskBadge.setOpaque(true);
        riskBadge.setBackground(new Color(220, 252, 231));
        riskBadge.setForeground(new Color(22, 101, 52));
        riskBadge.setPreferredSize(new Dimension(100, 36));
        riskBadge.setBorder(new LineBorder(new Color(134, 239, 172), 1, true));

        JPanel infoFields = new JPanel(new GridLayout(6, 1, 4, 4));
        infoFields.setOpaque(false);

        domainNameLbl = new JLabel("• Domain: reuters.com");
        httpsLbl = new JLabel("• HTTPS Protocol: Active & Secured");
        urlStructureLbl = new JLabel("• Structure: Standard Domain");
        domainLengthLbl = new JLabel("• Domain Length: 11 chars");
        subdomainCountLbl = new JLabel("• Subdomain Depth: 0");
        trustScoreLbl = new JLabel("• Source Trust Index: 95/100");

        infoFields.add(domainNameLbl);
        infoFields.add(httpsLbl);
        infoFields.add(urlStructureLbl);
        infoFields.add(domainLengthLbl);
        infoFields.add(subdomainCountLbl);
        infoFields.add(trustScoreLbl);

        leftInfo.add(riskBadge, BorderLayout.NORTH);
        leftInfo.add(infoFields, BorderLayout.CENTER);

        // Right Indicators Card
        RoundedPanel rightInfo = new RoundedPanel(10, ThemeManager.getInputBackground(), ThemeManager.getCardBorder());
        rightInfo.setLayout(new BorderLayout(8, 8));
        rightInfo.setBorder(new EmptyBorder(12, 12, 12, 12));

        JLabel rightTitle = new JLabel("⚠️ Heuristic Risk Indicators & Editorial Notes");
        rightTitle.setFont(ThemeManager.FONT_BOLD_13);
        rightTitle.setForeground(ThemeManager.getTextPrimary());

        indicatorsArea = new JTextArea();
        indicatorsArea.setFont(ThemeManager.FONT_REGULAR_12);
        indicatorsArea.setEditable(false);
        indicatorsArea.setOpaque(false);
        indicatorsArea.setForeground(ThemeManager.getTextPrimary());
        indicatorsArea.setText("• Domain is an internationally verified authoritative news organization.\n• Editorial oversight matches global journalism standards.\n");

        JScrollPane scroll = new JScrollPane(indicatorsArea);
        scroll.setBorder(null);
        scroll.setOpaque(false);
        scroll.getViewport().setOpaque(false);

        rightInfo.add(rightTitle, BorderLayout.NORTH);
        rightInfo.add(scroll, BorderLayout.CENTER);

        detailsGrid.add(leftInfo);
        detailsGrid.add(rightInfo);

        // Bottom Disclaimer
        JLabel disclaimer = new JLabel("* Note: Domain indicators are heuristic risk assessments and do not constitute absolute proof.", SwingConstants.CENTER);
        disclaimer.setFont(ThemeManager.FONT_SMALL_11);
        disclaimer.setForeground(ThemeManager.getTextSecondary());

        card.add(topBar, BorderLayout.NORTH);
        card.add(detailsGrid, BorderLayout.CENTER);
        card.add(disclaimer, BorderLayout.SOUTH);

        add(card, BorderLayout.CENTER);
    }

    private void runDomainCheck() {
        String input = domainInputField.getText().trim();
        if (input.isEmpty()) return;

        DomainAnalysis da = DomainAnalyzer.analyze(input);

        riskBadge.setText("DOMAIN RISK: " + da.getRiskLevel().getLabel());
        riskBadge.setBackground(da.getRiskLevel().getColor());
        riskBadge.setForeground(Color.WHITE);

        domainNameLbl.setText("• Domain: " + da.getDomainName());
        httpsLbl.setText("• HTTPS Protocol: " + (da.isHasHttps() ? "Active & Secured" : "Unsecured (HTTP)"));
        urlStructureLbl.setText("• Structure: " + da.getUrlStructure());
        domainLengthLbl.setText("• Domain Length: " + da.getDomainLength() + " chars");
        subdomainCountLbl.setText("• Subdomain Depth: " + da.getSubdomainCount());
        trustScoreLbl.setText("• Source Trust Index: " + da.getSourceTrustScore() + "/100");

        StringBuilder sb = new StringBuilder();
        sb.append("• Assessment: ").append(da.getAssessmentSummary()).append("\n");
        sb.append("• Editorial Category: ").append(da.getEditorialCategory()).append("\n");
        if (!da.getSuspiciousIndicators().isEmpty()) {
            sb.append("\nFlagged Indicators:\n");
            for (String ind : da.getSuspiciousIndicators()) {
                sb.append("  * ").append(ind).append("\n");
            }
        }
        indicatorsArea.setText(sb.toString());
    }

    private void styleButton(JButton btn, Color bg, Color fg) {
        btn.setBackground(bg);
        btn.setForeground(fg);
        btn.setFocusPainted(false);
        btn.setFont(ThemeManager.FONT_BOLD_13);
        btn.setBorder(BorderFactory.createCompoundBorder(
            new LineBorder(ThemeManager.getCardBorder(), 1, true),
            new EmptyBorder(6, 14, 6, 14)
        ));
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
    }
}
