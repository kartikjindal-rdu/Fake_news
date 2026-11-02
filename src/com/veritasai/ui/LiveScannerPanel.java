package com.veritasai.ui;

import com.fakenews.detector.data.DefaultDataset;
import com.fakenews.detector.gui.ThemeManager;
import com.fakenews.detector.gui.components.CircularGaugePanel;
import com.fakenews.detector.gui.components.RoundedPanel;
import com.fakenews.detector.model.NewsArticle;
import com.veritasai.model.Claim;
import com.veritasai.model.NewsAnalysisResult;
import com.veritasai.model.NewsInput;
import com.veritasai.ocr.OCRService;
import com.veritasai.ocr.PlaceholderOCRService;
import com.veritasai.service.NewsAnalysisService;
import com.veritasai.service.ReportGenerator;
import com.veritasai.ui.components.HighlightedEditorPane;
import com.veritasai.ui.components.RiskMeterBar;
import com.veritasai.ui.components.StepProgressDialog;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import javax.swing.border.TitledBorder;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.datatransfer.StringSelection;
import java.io.File;
import java.net.URI;
import java.util.List;

/**
 * Enterprise Live AI Scanner Panel with non-blocking SwingWorker execution,
 * 10-step progress dialog, OCR upload preparation, interactive highlights,
 * claim verification matrix, and structured explainability.
 */
public class LiveScannerPanel extends JPanel {

    private static final long serialVersionUID = 1L;

    private final Frame parentFrame;
    private final NewsAnalysisService service;
    private final OCRService ocrService;
    private NewsAnalysisResult currentResult;

    // Inputs
    private JTextField urlField;
    private JTextField headlineField;
    private JTextArea contentArea;
    private JLabel wordCountLabel;
    private JLabel charCountLabel;
    private JButton uploadScreenshotButton;
    private JButton scanButton;
    private JButton clearButton;

    // Outputs
    private JLabel verdictBadge;
    private CircularGaugePanel confidenceGauge;
    private RiskMeterBar riskMeter;
    private JProgressBar factProbBar;
    private JProgressBar fakeProbBar;
    private JProgressBar sensationalismBar;
    private JProgressBar clickbaitBar;
    private JProgressBar emotionBar;
    private JProgressBar languageManipBar;
    private JLabel toneBadge;
    private JLabel readabilityBadge;
    private JLabel sourceTrustBadge;

    // Text & Claims
    private HighlightedEditorPane highlightedPane;
    private JTable claimsTable;
    private DefaultTableModel claimsTableModel;
    private JTextArea explainabilityArea;

    // Action buttons
    private JButton copyReportBtn;
    private JButton exportReportBtn;
    private JButton factCheckWebBtn;

    public LiveScannerPanel(Frame parent) {
        this.parentFrame = parent;
        this.service = NewsAnalysisService.getInstance();
        this.ocrService = new PlaceholderOCRService();

        setLayout(new BorderLayout(12, 12));
        setOpaque(false);
        setBorder(new EmptyBorder(10, 10, 10, 10));

        JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, createInputSection(), createOutputSection());
        splitPane.setResizeWeight(0.46);
        splitPane.setDividerSize(6);
        splitPane.setBorder(null);
        splitPane.setOpaque(false);

        add(splitPane, BorderLayout.CENTER);
    }

    private JPanel createInputSection() {
        RoundedPanel card = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        card.setLayout(new BorderLayout(10, 10));
        card.setBorder(new EmptyBorder(14, 14, 14, 14));

        // Top Row: Presets + Screenshot OCR
        JPanel topRow = new JPanel(new BorderLayout(8, 8));
        topRow.setOpaque(false);

        JLabel heading = new JLabel("🔍 News & Claim Input Studio");
        heading.setFont(ThemeManager.FONT_SECTION);
        heading.setForeground(ThemeManager.getTextPrimary());

        String[] presets = {
            "⚡ Quick Presets...",
            "📰 NASA: Deep Galaxy Discovery (Verified Real)",
            "🧬 WHO: Hypertension Health Guidelines (Verified Real)",
            "⚠️ Hoax: Lemon Peel Dissolves Cancer in 24h (Fake)",
            "👽 Conspiracy: Illuminati Apocalypse Leaked Audio (Fake)",
            "💰 Scam: 50,000 Free Bitcoin Giveaway (Fake)"
        };
        JComboBox<String> presetCombo = new JComboBox<>(presets);
        presetCombo.setFont(ThemeManager.FONT_REGULAR_12);
        presetCombo.addActionListener(e -> loadPreset(presetCombo.getSelectedIndex()));

        topRow.add(heading, BorderLayout.WEST);
        topRow.add(presetCombo, BorderLayout.EAST);

        // Fields
        JPanel fields = new JPanel();
        fields.setLayout(new BoxLayout(fields, BoxLayout.Y_AXIS));
        fields.setOpaque(false);

        // URL Field
        JLabel urlLbl = new JLabel("Source Website / URL (Optional Domain Check):");
        urlLbl.setFont(ThemeManager.FONT_BOLD_13);
        urlLbl.setForeground(ThemeManager.getTextPrimary());
        urlField = new JTextField();
        urlField.setFont(ThemeManager.FONT_REGULAR_13);
        urlField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 32));
        urlField.setBorder(BorderFactory.createCompoundBorder(
            new LineBorder(ThemeManager.getInputBorder(), 1, true),
            new EmptyBorder(4, 8, 4, 8)
        ));

        // Headline Field
        JLabel headLbl = new JLabel("News Headline / Claim Title:");
        headLbl.setFont(ThemeManager.FONT_BOLD_13);
        headLbl.setForeground(ThemeManager.getTextPrimary());
        headlineField = new JTextField();
        headlineField.setFont(ThemeManager.FONT_REGULAR_13);
        headlineField.setMaximumSize(new Dimension(Integer.MAX_VALUE, 32));
        headlineField.setBorder(BorderFactory.createCompoundBorder(
            new LineBorder(ThemeManager.getInputBorder(), 1, true),
            new EmptyBorder(4, 8, 4, 8)
        ));

        // Content Area
        JLabel contentLbl = new JLabel("Article Body / Claim Statement:");
        contentLbl.setFont(ThemeManager.FONT_BOLD_13);
        contentLbl.setForeground(ThemeManager.getTextPrimary());

        contentArea = new JTextArea(8, 20);
        contentArea.setFont(ThemeManager.FONT_REGULAR_13);
        contentArea.setLineWrap(true);
        contentArea.setWrapStyleWord(true);
        contentArea.setBorder(new EmptyBorder(6, 6, 6, 6));

        contentArea.getDocument().addDocumentListener(new javax.swing.event.DocumentListener() {
            public void insertUpdate(javax.swing.event.DocumentEvent e) { updateCounts(); }
            public void removeUpdate(javax.swing.event.DocumentEvent e) { updateCounts(); }
            public void changedUpdate(javax.swing.event.DocumentEvent e) { updateCounts(); }
        });

        JScrollPane scroll = new JScrollPane(contentArea);
        scroll.setBorder(new LineBorder(ThemeManager.getInputBorder(), 1, true));

        // Count + OCR Row
        JPanel subRow = new JPanel(new BorderLayout());
        subRow.setOpaque(false);

        uploadScreenshotButton = new JButton("📷 Upload Screenshot (OCR)");
        styleButton(uploadScreenshotButton, ThemeManager.getInputBackground(), ThemeManager.getTextPrimary());
        uploadScreenshotButton.setFont(ThemeManager.FONT_SMALL_11);
        uploadScreenshotButton.addActionListener(e -> handleScreenshotUpload());

        JPanel counts = new JPanel(new FlowLayout(FlowLayout.RIGHT, 6, 2));
        counts.setOpaque(false);
        wordCountLabel = new JLabel("0 words");
        wordCountLabel.setFont(ThemeManager.FONT_SMALL_11);
        wordCountLabel.setForeground(ThemeManager.getTextSecondary());
        charCountLabel = new JLabel("0 chars");
        charCountLabel.setFont(ThemeManager.FONT_SMALL_11);
        charCountLabel.setForeground(ThemeManager.getTextSecondary());
        counts.add(wordCountLabel);
        counts.add(new JLabel("|"));
        counts.add(charCountLabel);

        subRow.add(uploadScreenshotButton, BorderLayout.WEST);
        subRow.add(counts, BorderLayout.EAST);

        fields.add(urlLbl);
        fields.add(Box.createVerticalStrut(4));
        fields.add(urlField);
        fields.add(Box.createVerticalStrut(8));
        fields.add(headLbl);
        fields.add(Box.createVerticalStrut(4));
        fields.add(headlineField);
        fields.add(Box.createVerticalStrut(8));
        fields.add(contentLbl);
        fields.add(Box.createVerticalStrut(4));
        fields.add(scroll);
        fields.add(subRow);

        // Buttons
        JPanel actions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
        actions.setOpaque(false);

        clearButton = new JButton("🧹 Clear");
        styleButton(clearButton, ThemeManager.getInputBackground(), ThemeManager.getTextSecondary());
        clearButton.addActionListener(e -> clearInputs());

        scanButton = new JButton("⚡ Scan & Detect Misinformation");
        styleButton(scanButton, ThemeManager.ACCENT_BLUE, Color.WHITE);
        scanButton.setPreferredSize(new Dimension(260, 36));
        scanButton.addActionListener(e -> startAsyncScan());

        actions.add(clearButton);
        actions.add(scanButton);

        card.add(topRow, BorderLayout.NORTH);
        card.add(fields, BorderLayout.CENTER);
        card.add(actions, BorderLayout.SOUTH);

        return card;
    }

    private JPanel createOutputSection() {
        RoundedPanel card = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        card.setLayout(new BorderLayout(8, 8));
        card.setBorder(new EmptyBorder(12, 14, 12, 14));

        // Top Status Header (Verdict + Risk Meter + Confidence Gauge)
        JPanel topHeader = new JPanel(new BorderLayout(8, 0));
        topHeader.setOpaque(false);

        verdictBadge = new JLabel("READY TO SCAN", SwingConstants.CENTER);
        verdictBadge.setFont(new Font("Segoe UI", Font.BOLD, 15));
        verdictBadge.setOpaque(true);
        verdictBadge.setBackground(ThemeManager.getInputBackground());
        verdictBadge.setForeground(ThemeManager.getTextSecondary());
        verdictBadge.setPreferredSize(new Dimension(210, 48));
        verdictBadge.setBorder(new LineBorder(ThemeManager.getCardBorder(), 1, true));

        riskMeter = new RiskMeterBar();
        confidenceGauge = new CircularGaugePanel();

        topHeader.add(verdictBadge, BorderLayout.WEST);
        topHeader.add(riskMeter, BorderLayout.CENTER);
        topHeader.add(confidenceGauge, BorderLayout.EAST);

        // Sub-tabs for Forensic Inspection (Metrics, Highlighted Text, Claims, AI Rationale)
        JTabbedPane resultSubTabs = new JTabbedPane();
        resultSubTabs.setFont(ThemeManager.FONT_BOLD_13);

        // 1. Metric Breakdown Tab
        resultSubTabs.addTab("📊 10-Factor Metrics", createMetricsTab());

        // 2. Interactive Highlighted Text Tab
        highlightedPane = new HighlightedEditorPane();
        JScrollPane highlightScroll = new JScrollPane(highlightedPane);
        highlightScroll.setBorder(new EmptyBorder(4, 4, 4, 4));
        resultSubTabs.addTab("🖍️ Flagged Highlights & Tooltips", highlightScroll);

        // 3. Claims Verification Matrix
        resultSubTabs.addTab("🎯 Extracted Claims Matrix", createClaimsTab());

        // 4. Structured Explainability Tab
        explainabilityArea = new JTextArea();
        explainabilityArea.setFont(ThemeManager.FONT_REGULAR_12);
        explainabilityArea.setEditable(false);
        explainabilityArea.setBackground(ThemeManager.getInputBackground());
        explainabilityArea.setForeground(ThemeManager.getTextPrimary());
        JScrollPane explainScroll = new JScrollPane(explainabilityArea);
        resultSubTabs.addTab("🧠 Structured AI Rationale", explainScroll);

        // Bottom Action Toolbar
        JPanel bottomBar = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
        bottomBar.setOpaque(false);

        copyReportBtn = new JButton("📋 Copy Report");
        styleButton(copyReportBtn, ThemeManager.getInputBackground(), ThemeManager.getTextPrimary());
        copyReportBtn.addActionListener(e -> copyReport());

        exportReportBtn = new JButton("💾 Export Report");
        styleButton(exportReportBtn, ThemeManager.getInputBackground(), ThemeManager.getTextPrimary());
        exportReportBtn.addActionListener(e -> exportReport());

        factCheckWebBtn = new JButton("🌐 Fact-Check on Web");
        styleButton(factCheckWebBtn, ThemeManager.getInputBackground(), ThemeManager.ACCENT_BLUE);
        factCheckWebBtn.addActionListener(e -> openFactCheck());

        bottomBar.add(copyReportBtn);
        bottomBar.add(exportReportBtn);
        bottomBar.add(factCheckWebBtn);

        card.add(topHeader, BorderLayout.NORTH);
        card.add(resultSubTabs, BorderLayout.CENTER);
        card.add(bottomBar, BorderLayout.SOUTH);

        return card;
    }

    private JPanel createMetricsTab() {
        JPanel p = new JPanel(new GridLayout(4, 2, 10, 8));
        p.setOpaque(false);
        p.setBorder(new EmptyBorder(8, 8, 8, 8));

        factProbBar = createBar(ThemeManager.ACCENT_GREEN);
        fakeProbBar = createBar(ThemeManager.ACCENT_RED);
        sensationalismBar = createBar(ThemeManager.ACCENT_ORANGE);
        clickbaitBar = createBar(ThemeManager.ACCENT_PURPLE);
        emotionBar = createBar(new Color(236, 72, 153));
        languageManipBar = createBar(new Color(99, 102, 241));

        p.add(wrap("Verified Fact Likelihood:", factProbBar));
        p.add(wrap("Misinformation / Fake Probability:", fakeProbBar));
        p.add(wrap("Sensationalism Score:", sensationalismBar));
        p.add(wrap("Clickbait Index:", clickbaitBar));
        p.add(wrap("Emotional Manipulation Score:", emotionBar));
        p.add(wrap("Language Manipulation Score:", languageManipBar));

        toneBadge = createBadge("Tone: Neutral");
        readabilityBadge = createBadge("Readability: Standard");
        sourceTrustBadge = createBadge("Source Trust: 50%");

        JPanel badgeRow = new JPanel(new GridLayout(1, 3, 6, 0));
        badgeRow.setOpaque(false);
        badgeRow.add(toneBadge);
        badgeRow.add(readabilityBadge);
        badgeRow.add(sourceTrustBadge);

        p.add(badgeRow);

        return p;
    }

    private JPanel createClaimsTab() {
        JPanel p = new JPanel(new BorderLayout());
        p.setOpaque(false);
        p.setBorder(new EmptyBorder(6, 6, 6, 6));

        String[] cols = {"Claim Assertion", "Verification Status", "Risk Level"};
        claimsTableModel = new DefaultTableModel(cols, 0) {
            public boolean isCellEditable(int r, int c) { return false; }
        };
        claimsTable = new JTable(claimsTableModel);
        claimsTable.setFont(ThemeManager.FONT_REGULAR_12);
        claimsTable.setRowHeight(24);
        claimsTable.getTableHeader().setFont(ThemeManager.FONT_BOLD_13);

        JScrollPane scroll = new JScrollPane(claimsTable);
        p.add(scroll, BorderLayout.CENTER);
        return p;
    }

    private JPanel wrap(String title, JProgressBar bar) {
        JPanel p = new JPanel(new BorderLayout(2, 2));
        p.setOpaque(false);
        JLabel l = new JLabel(title);
        l.setFont(ThemeManager.FONT_SMALL_11);
        l.setForeground(ThemeManager.getTextSecondary());
        p.add(l, BorderLayout.NORTH);
        p.add(bar, BorderLayout.CENTER);
        return p;
    }

    private JProgressBar createBar(Color c) {
        JProgressBar bar = new JProgressBar(0, 100);
        bar.setStringPainted(true);
        bar.setFont(ThemeManager.FONT_BOLD_13);
        bar.setForeground(c);
        bar.setPreferredSize(new Dimension(120, 20));
        return bar;
    }

    private JLabel createBadge(String text) {
        JLabel l = new JLabel(text, SwingConstants.CENTER);
        l.setFont(ThemeManager.FONT_SMALL_11);
        l.setOpaque(true);
        l.setBackground(ThemeManager.getInputBackground());
        l.setForeground(ThemeManager.getTextSecondary());
        l.setBorder(new LineBorder(ThemeManager.getCardBorder(), 1, true));
        return l;
    }

    // ==========================================
    // ASYNC SCANNING PIPELINE
    // ==========================================
    private void startAsyncScan() {
        String headline = headlineField.getText().trim();
        String content = contentArea.getText().trim();
        String url = urlField.getText().trim();

        if (headline.isEmpty() && content.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Please enter a headline or article statement to analyze.", "Input Required", JOptionPane.WARNING_MESSAGE);
            return;
        }

        scanButton.setEnabled(false);
        StepProgressDialog progressDialog = new StepProgressDialog(parentFrame);

        SwingWorker<NewsAnalysisResult, Void> worker = new SwingWorker<NewsAnalysisResult, Void>() {
            @Override
            protected NewsAnalysisResult doInBackground() throws Exception {
                NewsInput input = new NewsInput(headline, content, url);
                return service.analyze(input, (stepIdx, desc) -> {
                    progressDialog.updateStep(stepIdx, desc);
                    try { Thread.sleep(90); } catch (Exception ignored) {} // smooth visual step pacing
                });
            }

            @Override
            protected void done() {
                try {
                    currentResult = get();
                    populateResults(currentResult);
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(LiveScannerPanel.this, "Analysis error: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
                } finally {
                    progressDialog.dispose();
                    scanButton.setEnabled(true);
                }
            }
        };

        worker.execute();
        progressDialog.setVisible(true);
    }

    private void populateResults(NewsAnalysisResult res) {
        // Verdict Badge
        verdictBadge.setText(res.getVerdict().getLabel());
        try {
            verdictBadge.setBackground(Color.decode(res.getVerdict().getColorHex()));
            verdictBadge.setForeground(Color.WHITE);
        } catch (Exception ex) {
            verdictBadge.setBackground(ThemeManager.getInputBackground());
            verdictBadge.setForeground(ThemeManager.getTextPrimary());
        }

        // Gauges & Bars
        confidenceGauge.setValue(res.getAiConfidence(), "Confidence", ThemeManager.ACCENT_BLUE);
        riskMeter.setRisk(res.getRiskScore(), res.getRiskLevel());

        factProbBar.setValue((int) Math.round(res.getRealProbability()));
        factProbBar.setString(String.format("%.1f%%", res.getRealProbability()));

        fakeProbBar.setValue((int) Math.round(res.getFakeProbability()));
        fakeProbBar.setString(String.format("%.1f%%", res.getFakeProbability()));

        sensationalismBar.setValue((int) Math.round(res.getSensationalismScore()));
        sensationalismBar.setString(String.format("%.0f%%", res.getSensationalismScore()));

        clickbaitBar.setValue((int) Math.round(res.getClickbaitScore()));
        clickbaitBar.setString(String.format("%.0f%%", res.getClickbaitScore()));

        emotionBar.setValue((int) Math.round(res.getEmotionalManipulationScore()));
        emotionBar.setString(String.format("%.0f%%", res.getEmotionalManipulationScore()));

        languageManipBar.setValue((int) Math.round(res.getLanguageManipulationScore()));
        languageManipBar.setString(String.format("%.1f%%", res.getLanguageManipulationScore()));

        toneBadge.setText("Tone: " + res.getEmotionalTone());
        readabilityBadge.setText("Readability: " + res.getReadabilityLevel());
        sourceTrustBadge.setText("Source Trust: " + res.getSourceTrustScore() + "%");

        // Highlights Tab
        String fullRaw = headlineField.getText() + "\n\n" + contentArea.getText();
        highlightedPane.renderTextWithHighlights(fullRaw, res.getHighlightedTriggers(), ThemeManager.isDarkMode());

        // Claims Matrix
        claimsTableModel.setRowCount(0);
        for (Claim c : res.getExtractedClaims()) {
            claimsTableModel.addRow(new Object[]{c.getText(), c.getVerificationStatus().getLabel(), c.getRiskLevel().getLabel()});
        }

        // Structured Explainability Rationale
        StringBuilder sb = new StringBuilder();
        sb.append("=== PRIMARY FINDINGS ===\n");
        for (String pf : res.getPrimaryFindings()) sb.append("• ").append(pf).append("\n");

        sb.append("\n=== SUSPICIOUS LANGUAGE & TRIGGERS ===\n");
        for (String sl : res.getSuspiciousLanguageNotes()) sb.append("• ").append(sl).append("\n");

        sb.append("\n=== SOURCE & DOMAIN ANALYSIS ===\n");
        for (String sa : res.getSourceAnalysisNotes()) sb.append("• ").append(sa).append("\n");

        sb.append("\n=== RECOMMENDED ACTION ===\n");
        sb.append(res.getRecommendedAction()).append("\n");

        explainabilityArea.setText(sb.toString());
    }

    private void handleScreenshotUpload() {
        JFileChooser chooser = new JFileChooser();
        int res = chooser.showOpenDialog(this);
        if (res == JFileChooser.APPROVE_OPTION) {
            File img = chooser.getSelectedFile();
            try {
                String extracted = ocrService.extractTextFromImage(img);
                contentArea.setText(extracted);
                JOptionPane.showMessageDialog(this,
                    "Screenshot loaded: " + img.getName() + "\n(OCR Engine interface active; ready for Tesseract linking)",
                    "OCR Processing", JOptionPane.INFORMATION_MESSAGE);
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "OCR Error: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void loadPreset(int idx) {
        List<NewsArticle> data = DefaultDataset.getTrainingData();
        if (data.isEmpty()) return;
        NewsArticle chosen;
        if (idx == 1) chosen = data.get(0);      // NASA Real
        else if (idx == 2) chosen = data.get(5); // WHO Real
        else if (idx == 3) chosen = data.get(16); // Lemon Peel Hoax
        else if (idx == 4) chosen = data.get(20); // Illuminati Hoax
        else if (idx == 5) chosen = data.get(25); // Bitcoin Scam
        else return;

        urlField.setText(chosen.getSourceUrl());
        headlineField.setText(chosen.getTitle());
        contentArea.setText(chosen.getContent());
        startAsyncScan();
    }

    private void updateCounts() {
        String t = contentArea.getText();
        charCountLabel.setText(t.length() + " chars");
        String trimmed = t.trim();
        wordCountLabel.setText(trimmed.isEmpty() ? "0 words" : trimmed.split("\\s+").length + " words");
    }

    public void clearInputs() {
        urlField.setText("");
        headlineField.setText("");
        contentArea.setText("");
        verdictBadge.setText("READY TO SCAN");
        verdictBadge.setBackground(ThemeManager.getInputBackground());
        verdictBadge.setForeground(ThemeManager.getTextSecondary());
        confidenceGauge.setValue(0, "Confidence", ThemeManager.ACCENT_BLUE);
        riskMeter.setRisk(0, com.veritasai.util.Constants.RiskLevel.LOW);
        factProbBar.setValue(0);
        factProbBar.setString("0%");
        fakeProbBar.setValue(0);
        fakeProbBar.setString("0%");
        sensationalismBar.setValue(0);
        sensationalismBar.setString("0%");
        clickbaitBar.setValue(0);
        clickbaitBar.setString("0%");
        emotionBar.setValue(0);
        emotionBar.setString("0%");
        languageManipBar.setValue(0);
        languageManipBar.setString("0%");
        toneBadge.setText("Tone: Neutral");
        readabilityBadge.setText("Readability: Standard");
        sourceTrustBadge.setText("Source Trust: 50%");
        highlightedPane.renderTextWithHighlights("", null, ThemeManager.isDarkMode());
        claimsTableModel.setRowCount(0);
        explainabilityArea.setText("");
    }

    public void triggerScan() {
        startAsyncScan();
    }

    private void copyReport() {
        if (currentResult == null) {
            JOptionPane.showMessageDialog(this, "Please perform an analysis first.", "No Report", JOptionPane.INFORMATION_MESSAGE);
            return;
        }
        String rep = ReportGenerator.generateTextReport(currentResult, headlineField.getText());
        Toolkit.getDefaultToolkit().getSystemClipboard().setContents(new StringSelection(rep), null);
        JOptionPane.showMessageDialog(this, "Analysis report copied to clipboard!", "Copied", JOptionPane.INFORMATION_MESSAGE);
    }

    private void exportReport() {
        if (currentResult == null) {
            JOptionPane.showMessageDialog(this, "Please perform an analysis first.", "No Report", JOptionPane.INFORMATION_MESSAGE);
            return;
        }
        JFileChooser chooser = new JFileChooser();
        chooser.setSelectedFile(new File("veritas_analysis_report.txt"));
        int res = chooser.showSaveDialog(this);
        if (res == JFileChooser.APPROVE_OPTION) {
            try {
                ReportGenerator.exportToFile(currentResult, headlineField.getText(), chooser.getSelectedFile());
                JOptionPane.showMessageDialog(this, "Report exported successfully!", "Exported", JOptionPane.INFORMATION_MESSAGE);
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Export Error: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void openFactCheck() {
        if (currentResult == null || currentResult.getFactCheckQueryUrl() == null) {
            JOptionPane.showMessageDialog(this, "Please scan a claim first.", "No Query", JOptionPane.INFORMATION_MESSAGE);
            return;
        }
        try {
            Desktop.getDesktop().browse(new URI(currentResult.getFactCheckQueryUrl()));
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Could not launch web browser: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void styleButton(JButton btn, Color bg, Color fg) {
        btn.setBackground(bg);
        btn.setForeground(fg);
        btn.setFocusPainted(false);
        btn.setFont(ThemeManager.FONT_BOLD_13);
        btn.setBorder(BorderFactory.createCompoundBorder(
            new LineBorder(ThemeManager.getCardBorder(), 1, true),
            new EmptyBorder(6, 12, 6, 12)
        ));
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
    }
}
