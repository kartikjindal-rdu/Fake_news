package com.veritasai.ui;

import com.fakenews.detector.gui.ThemeManager;
import com.fakenews.detector.gui.components.RoundedPanel;
import com.veritasai.model.ScanRecord;
import com.veritasai.repository.DatabaseManager;
import com.veritasai.service.NewsAnalysisService;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import java.awt.*;
import java.util.List;

/**
 * System Administration & Analytical Dashboard Panel.
 * Displays live microservice statuses, scan distributions, risk metrics, and integration notes.
 */
public class DashboardPanel extends JPanel {

    private static final long serialVersionUID = 1L;

    private JLabel totalScansVal;
    private JLabel fakeScansVal;
    private JLabel verifiedScansVal;
    private JLabel avgRiskVal;

    private JLabel mlApiStatusLbl;
    private JLabel dbStatusLbl;
    private JLabel ocrStatusLbl;
    private JLabel cloudStatusLbl;

    public DashboardPanel() {
        setLayout(new BorderLayout(12, 12));
        setOpaque(false);
        setBorder(new EmptyBorder(10, 10, 10, 10));

        JPanel content = new JPanel(new GridLayout(2, 1, 12, 12));
        content.setOpaque(false);

        content.add(createTopOverviewSection());
        content.add(createStatusAndIntegrationSection());

        add(content, BorderLayout.CENTER);

        refreshDashboard();
    }

    private JPanel createTopOverviewSection() {
        RoundedPanel card = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        card.setLayout(new BorderLayout(10, 10));
        card.setBorder(new EmptyBorder(14, 14, 14, 14));

        JLabel title = new JLabel("📊 Intelligence Overview & Scan Analytics");
        title.setFont(ThemeManager.FONT_SECTION);
        title.setForeground(ThemeManager.getTextPrimary());

        JPanel statGrid = new JPanel(new GridLayout(1, 4, 12, 0));
        statGrid.setOpaque(false);

        totalScansVal = new JLabel("0", SwingConstants.CENTER);
        fakeScansVal = new JLabel("0", SwingConstants.CENTER);
        verifiedScansVal = new JLabel("0", SwingConstants.CENTER);
        avgRiskVal = new JLabel("0.0", SwingConstants.CENTER);

        statGrid.add(createCard("TOTAL AUDITS", totalScansVal, ThemeManager.ACCENT_BLUE));
        statGrid.add(createCard("FAKE / HIGH RISK", fakeScansVal, ThemeManager.ACCENT_RED));
        statGrid.add(createCard("VERIFIED FACTS", verifiedScansVal, ThemeManager.ACCENT_GREEN));
        statGrid.add(createCard("AVG RISK SCORE", avgRiskVal, ThemeManager.ACCENT_ORANGE));

        card.add(title, BorderLayout.NORTH);
        card.add(statGrid, BorderLayout.CENTER);
        return card;
    }

    private JPanel createStatusAndIntegrationSection() {
        JPanel split = new JPanel(new GridLayout(1, 2, 12, 0));
        split.setOpaque(false);

        // System Status Card
        RoundedPanel statusCard = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        statusCard.setLayout(new BorderLayout(8, 8));
        statusCard.setBorder(new EmptyBorder(14, 14, 14, 14));

        JLabel sTitle = new JLabel("⚙️ System & Microservice Status");
        sTitle.setFont(ThemeManager.FONT_SECTION);
        sTitle.setForeground(ThemeManager.getTextPrimary());

        JPanel statusGrid = new JPanel(new GridLayout(4, 1, 6, 6));
        statusGrid.setOpaque(false);

        mlApiStatusLbl = createStatusBadge("ML Engine: Embedded Pure-Java Naive Bayes (Active)", ThemeManager.ACCENT_GREEN);
        dbStatusLbl = createStatusBadge(
            DatabaseManager.isSqliteDriverAvailable() ? "Database: SQLite File Persistence (Active)" : "Database: Synchronized Memory Store (Active)",
            ThemeManager.ACCENT_GREEN
        );
        ocrStatusLbl = createStatusBadge("OCR Engine: Tesseract Interface Service (Active)", ThemeManager.ACCENT_BLUE);
        cloudStatusLbl = createStatusBadge("REST / Mobile API: Headless NewsAnalysisService (Ready)", ThemeManager.ACCENT_GREEN);

        statusGrid.add(mlApiStatusLbl);
        statusGrid.add(dbStatusLbl);
        statusGrid.add(ocrStatusLbl);
        statusGrid.add(cloudStatusLbl);

        statusCard.add(sTitle, BorderLayout.NORTH);
        statusCard.add(statusGrid, BorderLayout.CENTER);

        // API & Mobile Guide Card
        RoundedPanel guideCard = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        guideCard.setLayout(new BorderLayout(8, 8));
        guideCard.setBorder(new EmptyBorder(14, 14, 14, 14));

        JLabel gTitle = new JLabel("📱 Android & Spring Boot API Quick Access");
        gTitle.setFont(ThemeManager.FONT_SECTION);
        gTitle.setForeground(ThemeManager.getTextPrimary());

        JTextArea guide = new JTextArea();
        guide.setFont(ThemeManager.FONT_CODE);
        guide.setEditable(false);
        guide.setOpaque(false);
        guide.setForeground(ThemeManager.getTextPrimary());
        guide.setText(
            "// Android Studio (Java/Kotlin) or Spring Boot Call:\n" +
            "NewsAnalysisService service = NewsAnalysisService.getInstance();\n" +
            "NewsInput input = new NewsInput(title, body, url);\n" +
            "NewsAnalysisResult res = service.analyze(input, null);\n" +
            "String json = res.toJson(); // Instant JSON payload\n"
        );

        guideCard.add(gTitle, BorderLayout.NORTH);
        guideCard.add(guide, BorderLayout.CENTER);

        split.add(statusCard);
        split.add(guideCard);
        return split;
    }

    private JPanel createCard(String title, JLabel val, Color col) {
        JPanel p = new JPanel(new BorderLayout(4, 4));
        p.setOpaque(true);
        p.setBackground(ThemeManager.getInputBackground());
        p.setBorder(new LineBorder(ThemeManager.getCardBorder(), 1, true));

        JLabel t = new JLabel(title, SwingConstants.CENTER);
        t.setFont(ThemeManager.FONT_SMALL_11);
        t.setForeground(ThemeManager.getTextSecondary());

        val.setFont(new Font("Segoe UI", Font.BOLD, 26));
        val.setForeground(col);

        p.add(t, BorderLayout.NORTH);
        p.add(val, BorderLayout.CENTER);
        return p;
    }

    private JLabel createStatusBadge(String text, Color col) {
        JLabel l = new JLabel("• " + text);
        l.setFont(ThemeManager.FONT_REGULAR_12);
        l.setForeground(col);
        return l;
    }

    public void refreshDashboard() {
        List<ScanRecord> records = NewsAnalysisService.getInstance().getRepository().getAll();
        int total = records.size();
        int fake = 0;
        int verified = 0;
        double sumRisk = 0.0;

        for (ScanRecord r : records) {
            if (r.getPrediction().contains("FAKE") || r.getRiskScore() >= 50.0) {
                fake++;
            } else if (r.getPrediction().contains("REAL") || r.getRiskScore() <= 25.0) {
                verified++;
            }
            sumRisk += r.getRiskScore();
        }

        double avg = (total > 0) ? sumRisk / total : 0.0;

        totalScansVal.setText(String.valueOf(total));
        fakeScansVal.setText(String.valueOf(fake));
        verifiedScansVal.setText(String.valueOf(verified));
        avgRiskVal.setText(String.format("%.1f", avg));
    }
}
