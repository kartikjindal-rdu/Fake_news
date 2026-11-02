package com.veritasai.ui;

import com.fakenews.detector.gui.ThemeManager;
import com.fakenews.detector.gui.components.RoundedPanel;
import com.veritasai.model.ScanRecord;
import com.veritasai.repository.ScanRepository;
import com.veritasai.service.NewsAnalysisService;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.border.LineBorder;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.io.File;
import java.util.List;

/**
 * Scan History and Audit Log Panel backed by SQLite database with filtering, search, and CSV export.
 */
public class HistoryPanel extends JPanel {

    private static final long serialVersionUID = 1L;

    private final ScanRepository repository;
    private JTable historyTable;
    private DefaultTableModel tableModel;
    private JTextField searchField;
    private JComboBox<String> filterCombo;

    public HistoryPanel() {
        this.repository = NewsAnalysisService.getInstance().getRepository();
        setLayout(new BorderLayout(12, 12));
        setOpaque(false);
        setBorder(new EmptyBorder(10, 10, 10, 10));

        RoundedPanel card = new RoundedPanel(14, ThemeManager.getCardBackground(), ThemeManager.getCardBorder());
        card.setLayout(new BorderLayout(10, 10));
        card.setBorder(new EmptyBorder(14, 14, 14, 14));

        // Top Filter Toolbar
        JPanel topToolbar = new JPanel(new BorderLayout(8, 8));
        topToolbar.setOpaque(false);

        JPanel leftFilters = new JPanel(new FlowLayout(FlowLayout.LEFT, 8, 0));
        leftFilters.setOpaque(false);

        JLabel searchLbl = new JLabel("Search Audits:");
        searchLbl.setFont(ThemeManager.FONT_BOLD_13);
        searchLbl.setForeground(ThemeManager.getTextPrimary());

        searchField = new JTextField(16);
        searchField.setFont(ThemeManager.FONT_REGULAR_13);
        searchField.setBorder(BorderFactory.createCompoundBorder(
            new LineBorder(ThemeManager.getInputBorder(), 1, true),
            new EmptyBorder(4, 6, 4, 6)
        ));
        searchField.getDocument().addDocumentListener(new javax.swing.event.DocumentListener() {
            public void insertUpdate(javax.swing.event.DocumentEvent e) { applyFilters(); }
            public void removeUpdate(javax.swing.event.DocumentEvent e) { applyFilters(); }
            public void changedUpdate(javax.swing.event.DocumentEvent e) { applyFilters(); }
        });

        JLabel filterLbl = new JLabel("Verdict Filter:");
        filterLbl.setFont(ThemeManager.FONT_BOLD_13);
        filterLbl.setForeground(ThemeManager.getTextPrimary());

        filterCombo = new JComboBox<>(new String[]{"ALL", "VERIFIED REAL", "LIKELY FAKE", "SUSPICIOUS"});
        filterCombo.setFont(ThemeManager.FONT_REGULAR_12);
        filterCombo.addActionListener(e -> applyFilters());

        leftFilters.add(searchLbl);
        leftFilters.add(searchField);
        leftFilters.add(filterLbl);
        leftFilters.add(filterCombo);

        JPanel rightActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 8, 0));
        rightActions.setOpaque(false);

        JButton deleteBtn = new JButton("🗑️ Delete Selected");
        styleButton(deleteBtn, ThemeManager.getInputBackground(), new Color(239, 68, 68));
        deleteBtn.addActionListener(e -> deleteSelectedRecord());

        JButton clearAllBtn = new JButton("🧹 Clear All");
        styleButton(clearAllBtn, ThemeManager.getInputBackground(), ThemeManager.getTextSecondary());
        clearAllBtn.addActionListener(e -> clearAllRecords());

        JButton exportBtn = new JButton("📥 Export CSV");
        styleButton(exportBtn, ThemeManager.ACCENT_BLUE, Color.WHITE);
        exportBtn.addActionListener(e -> exportCsv());

        rightActions.add(deleteBtn);
        rightActions.add(clearAllBtn);
        rightActions.add(exportBtn);

        topToolbar.add(leftFilters, BorderLayout.WEST);
        topToolbar.add(rightActions, BorderLayout.EAST);

        // History Table
        String[] cols = {"Scan Reference ID", "Date & Timestamp", "Headline / Claim Statement", "Source Domain", "Verdict", "Fake %", "Risk Score (0-100)"};
        tableModel = new DefaultTableModel(cols, 0) {
            public boolean isCellEditable(int r, int c) { return false; }
        };
        historyTable = new JTable(tableModel);
        historyTable.setFont(ThemeManager.FONT_REGULAR_12);
        historyTable.setRowHeight(26);
        historyTable.getTableHeader().setFont(ThemeManager.FONT_BOLD_13);
        historyTable.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        JScrollPane scroll = new JScrollPane(historyTable);
        scroll.setBorder(new LineBorder(ThemeManager.getCardBorder(), 1));

        card.add(topToolbar, BorderLayout.NORTH);
        card.add(scroll, BorderLayout.CENTER);

        add(card, BorderLayout.CENTER);

        refreshTable();
    }

    public void refreshTable() {
        applyFilters();
    }

    private void applyFilters() {
        tableModel.setRowCount(0);
        String q = searchField != null ? searchField.getText().trim() : "";
        String f = filterCombo != null ? (String) filterCombo.getSelectedItem() : "ALL";

        List<ScanRecord> records = repository.search(q, f);
        for (ScanRecord r : records) {
            tableModel.addRow(new Object[]{
                r.getScanId(),
                r.getTimestamp(),
                r.getHeadline(),
                r.getSourceDomain(),
                r.getPrediction(),
                String.format("%.1f%%", r.getFakeProbability()),
                String.format("%.1f", r.getRiskScore())
            });
        }
    }

    private void deleteSelectedRecord() {
        int row = historyTable.getSelectedRow();
        if (row == -1) {
            JOptionPane.showMessageDialog(this, "Please select a scan record to delete.", "No Selection", JOptionPane.WARNING_MESSAGE);
            return;
        }

        String scanId = (String) tableModel.getValueAt(row, 0);
        int confirm = JOptionPane.showConfirmDialog(this,
            "Are you sure you want to delete scan record '" + scanId + "'?",
            "Confirm Deletion", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE);

        if (confirm == JOptionPane.YES_OPTION) {
            repository.delete(scanId);
            refreshTable();
            JOptionPane.showMessageDialog(this, "Record deleted successfully.", "Deleted", JOptionPane.INFORMATION_MESSAGE);
        }
    }

    private void clearAllRecords() {
        int confirm = JOptionPane.showConfirmDialog(this,
            "Are you sure you want to clear all historical scan records?",
            "Confirm Clear All", JOptionPane.YES_NO_OPTION, JOptionPane.WARNING_MESSAGE);

        if (confirm == JOptionPane.YES_OPTION) {
            repository.clearAll();
            refreshTable();
        }
    }

    private void exportCsv() {
        JFileChooser chooser = new JFileChooser();
        chooser.setSelectedFile(new File("veritas_scan_audit_log.csv"));
        int res = chooser.showSaveDialog(this);
        if (res == JFileChooser.APPROVE_OPTION) {
            try {
                repository.exportToCsv(chooser.getSelectedFile());
                JOptionPane.showMessageDialog(this, "Audit log exported to CSV successfully!", "Export Success", JOptionPane.INFORMATION_MESSAGE);
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Export Error: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
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
