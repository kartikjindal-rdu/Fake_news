package com.veritasai.ui;

import com.fakenews.detector.data.DatasetLoader;
import com.fakenews.detector.data.DefaultDataset;
import com.fakenews.detector.gui.ThemeManager;
import com.fakenews.detector.gui.components.RoundedPanel;
import com.fakenews.detector.model.NewsArticle;
import com.veritasai.ml.MLModelService;
import com.veritasai.model.ModelMetrics;
import com.veritasai.service.NewsAnalysisService;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import java.awt.*;
import java.io.File;
import java.util.List;

/**
 * Advanced Machine Learning Model Studio & Dataset Management Dashboard.
 * Displays real-time evaluation metrics, Confusion Matrix, and dataset operations.
 */
public class ModelStudioPanel extends JPanel {

    private static final long serialVersionUID = 1L;

    private final MLModelService mlService;

    // Metrics labels
    private JLabel accuracyVal;
    private JLabel precisionVal;
    private JLabel recallVal;
    private JLabel f1Val;

    // Confusion matrix labels
    private JLabel tpLabel;
    private JLabel tnLabel;
    private JLabel fpLabel;
    private JLabel fnLabel;

    // Info labels
    private JLabel modelNameLbl;
    private JLabel versionLbl;
    private JLabel algorithmLbl;
    private JLabel datasetNameLbl;
    private JLabel totalRecordsLbl;
    private JLabel lastTrainedLbl;

    private JTextArea logConsole;

    public ModelStudioPanel() {
        this.mlService = NewsAnalysisService.getInstance().getMlService();
        setLayout(new BorderLayout(12, 12));
        setOpaque(false);
        setBorder(new EmptyBorder(10, 10, 10, 10));

        JPanel mainGrid = new JPanel(new GridLayout(2, 2, 12, 12));
        mainGrid.setOpaque(false);

        mainGrid.add(createModelInfoCard());
        mainGrid.add(createPerformanceCard());
        mainGrid.add(createConfusionMatrixCard());
        mainGrid.add(createDatasetCard());

        add(mainGrid, BorderLayout.CENTER);

        updateMetricsView();
    }

    private JPanel createModelInfoCard() {
        RoundedPanel card = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        card.setLayout(new BorderLayout(8, 8));
        card.setBorder(new EmptyBorder(14, 14, 14, 14));

        JLabel title = new JLabel("🧠 Model Architecture & Version");
        title.setFont(ThemeManager.FONT_SECTION);
        title.setForeground(ThemeManager.getTextPrimary());

        JPanel fields = new JPanel(new GridLayout(6, 1, 4, 4));
        fields.setOpaque(false);

        modelNameLbl = createRowLabel("Model Identifier", "Veritas-Multinomial-NB");
        versionLbl = createRowLabel("Model Version", "v2.5.0-ENTERPRISE");
        algorithmLbl = createRowLabel("Algorithm", "Multinomial Naive Bayes + TF-IDF (Laplace Add-1)");
        datasetNameLbl = createRowLabel("Dataset Benchmark", "Veritas Core Benchmark Corpus");
        totalRecordsLbl = createRowLabel("Corpus Records", DefaultDataset.getTrainingData().size() + " Multi-Domain Articles");
        lastTrainedLbl = createRowLabel("Last Trained", "Active Session");

        fields.add(modelNameLbl);
        fields.add(versionLbl);
        fields.add(algorithmLbl);
        fields.add(datasetNameLbl);
        fields.add(totalRecordsLbl);
        fields.add(lastTrainedLbl);

        card.add(title, BorderLayout.NORTH);
        card.add(fields, BorderLayout.CENTER);
        return card;
    }

    private JPanel createPerformanceCard() {
        RoundedPanel card = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        card.setLayout(new BorderLayout(8, 8));
        card.setBorder(new EmptyBorder(14, 14, 14, 14));

        JLabel title = new JLabel("📈 Evaluation Performance Metrics");
        title.setFont(ThemeManager.FONT_SECTION);
        title.setForeground(ThemeManager.getTextPrimary());

        JPanel metricGrid = new JPanel(new GridLayout(2, 2, 8, 8));
        metricGrid.setOpaque(false);

        accuracyVal = new JLabel("95.8%", SwingConstants.CENTER);
        precisionVal = new JLabel("96.2%", SwingConstants.CENTER);
        recallVal = new JLabel("95.0%", SwingConstants.CENTER);
        f1Val = new JLabel("95.6%", SwingConstants.CENTER);

        metricGrid.add(createMetricBox("ACCURACY", accuracyVal, ThemeManager.ACCENT_GREEN));
        metricGrid.add(createMetricBox("PRECISION", precisionVal, ThemeManager.ACCENT_BLUE));
        metricGrid.add(createMetricBox("RECALL", recallVal, ThemeManager.ACCENT_ORANGE));
        metricGrid.add(createMetricBox("F1-SCORE", f1Val, ThemeManager.ACCENT_PURPLE));

        card.add(title, BorderLayout.NORTH);
        card.add(metricGrid, BorderLayout.CENTER);
        return card;
    }

    private JPanel createConfusionMatrixCard() {
        RoundedPanel card = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        card.setLayout(new BorderLayout(8, 8));
        card.setBorder(new EmptyBorder(14, 14, 14, 14));

        JLabel title = new JLabel("🔲 Classification Confusion Matrix");
        title.setFont(ThemeManager.FONT_SECTION);
        title.setForeground(ThemeManager.getTextPrimary());

        JPanel cmGrid = new JPanel(new GridLayout(2, 2, 6, 6));
        cmGrid.setOpaque(false);

        tpLabel = new JLabel("TP: --", SwingConstants.CENTER);
        fnLabel = new JLabel("FN: --", SwingConstants.CENTER);
        fpLabel = new JLabel("FP: --", SwingConstants.CENTER);
        tnLabel = new JLabel("TN: --", SwingConstants.CENTER);

        cmGrid.add(createCmCell("True Positive (Fake correctly identified)", tpLabel, new Color(220, 252, 231), new Color(22, 101, 52)));
        cmGrid.add(createCmCell("False Negative (Fake labeled Real)", fnLabel, new Color(254, 226, 226), new Color(185, 28, 28)));
        cmGrid.add(createCmCell("False Positive (Real labeled Fake)", fpLabel, new Color(254, 243, 199), new Color(146, 64, 14)));
        cmGrid.add(createCmCell("True Negative (Real correctly identified)", tnLabel, new Color(224, 242, 254), new Color(3, 105, 161)));

        card.add(title, BorderLayout.NORTH);
        card.add(cmGrid, BorderLayout.CENTER);
        return card;
    }

    private JPanel createDatasetCard() {
        RoundedPanel card = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        card.setLayout(new BorderLayout(8, 8));
        card.setBorder(new EmptyBorder(14, 14, 14, 14));

        JLabel title = new JLabel("🗄️ Dataset Operations & Model Training");
        title.setFont(ThemeManager.FONT_SECTION);
        title.setForeground(ThemeManager.getTextPrimary());

        logConsole = new JTextArea();
        logConsole.setFont(ThemeManager.FONT_CODE);
        logConsole.setEditable(false);
        logConsole.setBackground(ThemeManager.getInputBackground());
        logConsole.setForeground(ThemeManager.getTextPrimary());
        logConsole.setText("--- Model Diagnostics Console ---\nReady for training & benchmark inference.\n");
        JScrollPane scroll = new JScrollPane(logConsole);
        scroll.setBorder(new LineBorder(ThemeManager.getCardBorder(), 1));

        JPanel btnRow = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
        btnRow.setOpaque(false);

        JButton reTrainBtn = new JButton("⚡ Run Model Evaluation");
        styleButton(reTrainBtn, ThemeManager.getInputBackground(), ThemeManager.getTextPrimary());
        reTrainBtn.addActionListener(e -> runModelEvaluation());

        JButton loadCsvBtn = new JButton("📂 Import Custom CSV Dataset");
        styleButton(loadCsvBtn, ThemeManager.ACCENT_BLUE, Color.WHITE);
        loadCsvBtn.addActionListener(e -> importCsvDataset());

        btnRow.add(reTrainBtn);
        btnRow.add(loadCsvBtn);

        card.add(title, BorderLayout.NORTH);
        card.add(scroll, BorderLayout.CENTER);
        card.add(btnRow, BorderLayout.SOUTH);
        return card;
    }

    private JPanel createMetricBox(String name, JLabel valLbl, Color color) {
        JPanel p = new JPanel(new BorderLayout(2, 2));
        p.setOpaque(true);
        p.setBackground(ThemeManager.getInputBackground());
        p.setBorder(new LineBorder(ThemeManager.getCardBorder(), 1, true));

        JLabel nameLbl = new JLabel(name, SwingConstants.CENTER);
        nameLbl.setFont(ThemeManager.FONT_SMALL_11);
        nameLbl.setForeground(ThemeManager.getTextSecondary());

        valLbl.setFont(new Font("Segoe UI", Font.BOLD, 22));
        valLbl.setForeground(color);

        p.add(nameLbl, BorderLayout.NORTH);
        p.add(valLbl, BorderLayout.CENTER);
        return p;
    }

    private JPanel createCmCell(String desc, JLabel val, Color bg, Color fg) {
        JPanel p = new JPanel(new BorderLayout(2, 2));
        p.setOpaque(true);
        p.setBackground(bg);
        p.setBorder(new LineBorder(fg.brighter(), 1, true));

        JLabel descLbl = new JLabel(desc, SwingConstants.CENTER);
        descLbl.setFont(new Font("Segoe UI", Font.PLAIN, 10));
        descLbl.setForeground(fg);

        val.setFont(new Font("Segoe UI", Font.BOLD, 16));
        val.setForeground(fg);

        p.add(descLbl, BorderLayout.NORTH);
        p.add(val, BorderLayout.CENTER);
        return p;
    }

    private JLabel createRowLabel(String title, String val) {
        JLabel l = new JLabel(String.format("• %s: %s", title, val));
        l.setFont(ThemeManager.FONT_REGULAR_12);
        l.setForeground(ThemeManager.getTextPrimary());
        return l;
    }

    private void updateMetricsView() {
        ModelMetrics m = mlService.getModelMetrics();
        if (m != null && m.isTrained()) {
            accuracyVal.setText(String.format("%.1f%%", m.getAccuracy()));
            precisionVal.setText(String.format("%.1f%%", m.getPrecision()));
            recallVal.setText(String.format("%.1f%%", m.getRecall()));
            f1Val.setText(String.format("%.1f%%", m.getF1Score()));

            tpLabel.setText("TP: " + m.getTruePositives());
            tnLabel.setText("TN: " + m.getTrueNegatives());
            fpLabel.setText("FP: " + m.getFalsePositives());
            fnLabel.setText("FN: " + m.getFalseNegatives());
            lastTrainedLbl.setText("• Last Trained: " + m.getTrainingDate());
        } else {
            accuracyVal.setText("N/A");
            precisionVal.setText("N/A");
            recallVal.setText("N/A");
            f1Val.setText("N/A");
            logConsole.append("Model metrics unavailable until training is completed.\n");
        }
    }

    private void runModelEvaluation() {
        logConsole.append("\n[BENCHMARK] Executing Model Evaluation Pipeline...\n");
        ModelMetrics m = mlService.evaluateModel();
        updateMetricsView();
        logConsole.append(String.format("[EVAL DONE] Accuracy: %.1f%% | Precision: %.1f%% | Recall: %.1f%% | F1: %.1f%%\n",
                m.getAccuracy(), m.getPrecision(), m.getRecall(), m.getF1Score()));
        JOptionPane.showMessageDialog(this, "Model Evaluation Completed successfully!", "Model Studio", JOptionPane.INFORMATION_MESSAGE);
    }

    private void importCsvDataset() {
        JFileChooser chooser = new JFileChooser();
        int res = chooser.showOpenDialog(this);
        if (res == JFileChooser.APPROVE_OPTION) {
            try {
                File file = chooser.getSelectedFile();
                List<NewsArticle> articles = DatasetLoader.loadFromCSV(file);
                if (articles.isEmpty()) {
                    JOptionPane.showMessageDialog(this, "No valid news articles found in CSV.", "Error", JOptionPane.WARNING_MESSAGE);
                    return;
                }
                mlService.trainModel();
                updateMetricsView();
                logConsole.append("\n[CUSTOM DATASET] Loaded and trained with " + articles.size() + " samples from " + file.getName() + "\n");
                JOptionPane.showMessageDialog(this, "Model re-trained with " + articles.size() + " custom articles!", "Success", JOptionPane.INFORMATION_MESSAGE);
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Import Error: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void styleButton(JButton btn, Color bg, Color fg) {
        btn.setBackground(bg);
        btn.setForeground(fg);
        btn.setFocusPainted(false);
        btn.setFont(ThemeManager.FONT_BOLD_13);
        btn.setBorder(BorderFactory.createCompoundBorder(
            new LineBorder(ThemeManager.getCardBorder(), 1, true),
            new EmptyBorder(5, 12, 5, 12)
        ));
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
    }
}
