package com.veritasai.ui.components;

import com.veritasai.gui.ThemeManager;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import java.awt.*;

/**
 * Modern modal dialog showing live 10-step pipeline progress during news analysis.
 */
public class StepProgressDialog extends JDialog {

    private static final long serialVersionUID = 1L;

    private JProgressBar overallProgress;
    private JLabel currentStepLabel;
    private DefaultListModel<String> stepListModel;
    private JList<String> stepList;

    public StepProgressDialog(Frame owner) {
        super(owner, "Veritas AI - Pipeline Execution", true);
        setSize(460, 360);
        setLocationRelativeTo(owner);
        setUndecorated(true);

        JPanel content = new JPanel(new BorderLayout(12, 12));
        content.setBackground(ThemeManager.getCardBackground());
        content.setBorder(BorderFactory.createCompoundBorder(
            new LineBorder(ThemeManager.ACCENT_BLUE, 2, true),
            new EmptyBorder(16, 20, 16, 20)
        ));

        // Header
        JPanel header = new JPanel(new BorderLayout(5, 5));
        header.setOpaque(false);
        JLabel title = new JLabel("🛡️ Veritas AI Analysis Pipeline");
        title.setFont(new Font("Segoe UI", Font.BOLD, 15));
        title.setForeground(ThemeManager.getTextPrimary());

        currentStepLabel = new JLabel("Initializing analysis...");
        currentStepLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        currentStepLabel.setForeground(ThemeManager.getTextSecondary());

        header.add(title, BorderLayout.NORTH);
        header.add(currentStepLabel, BorderLayout.SOUTH);

        // Progress Bar
        overallProgress = new JProgressBar(0, 10);
        overallProgress.setStringPainted(true);
        overallProgress.setForeground(ThemeManager.ACCENT_BLUE);
        overallProgress.setPreferredSize(new Dimension(100, 20));

        // Step List
        stepListModel = new DefaultListModel<>();
        stepList = new JList<>(stepListModel);
        stepList.setFont(new Font("Segoe UI", Font.PLAIN, 11));
        stepList.setBackground(ThemeManager.getInputBackground());
        stepList.setForeground(ThemeManager.getTextPrimary());
        stepList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        JScrollPane scroll = new JScrollPane(stepList);
        scroll.setBorder(new LineBorder(ThemeManager.getCardBorder(), 1));

        content.add(header, BorderLayout.NORTH);
        content.add(scroll, BorderLayout.CENTER);
        content.add(overallProgress, BorderLayout.SOUTH);

        setContentPane(content);
    }

    public void updateStep(int stepIndex, String stepDescription) {
        SwingUtilities.invokeLater(() -> {
            overallProgress.setValue(stepIndex);
            overallProgress.setString(stepIndex + " / 10 Steps (" + (stepIndex * 10) + "%)");
            currentStepLabel.setText(stepDescription);
            String item = String.format("✓ Step %d: %s", stepIndex, stepDescription);
            if (!stepListModel.contains(item)) {
                stepListModel.addElement(item);
                stepList.ensureIndexIsVisible(stepListModel.size() - 1);
            }
        });
    }
}
