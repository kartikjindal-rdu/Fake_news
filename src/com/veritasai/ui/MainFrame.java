package com.veritasai.ui;

import com.fakenews.detector.gui.ThemeManager;
import com.veritasai.util.Constants;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;

/**
 * Main application frame for Veritas AI Enterprise.
 * Manages global shortcuts, theme switching, tab navigation, and lifecycle.
 */
public class MainFrame extends JFrame {

    private static final long serialVersionUID = 1L;

    private JTabbedPane tabbedPane;
    private LiveScannerPanel scannerPanel;
    private HistoryPanel historyPanel;
    private ModelStudioPanel modelStudioPanel;
    private DomainCheckerPanel domainCheckerPanel;
    private DashboardPanel dashboardPanel;

    private JButton themeToggleBtn;

    public MainFrame() {
        initFrame();
        initShortcuts();
    }

    private void initFrame() {
        setTitle(Constants.APP_NAME + " - " + Constants.APP_TITLE + " [" + Constants.APP_VERSION + "]");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1240, 860);
        setMinimumSize(new Dimension(1080, 740));
        setLocationRelativeTo(null);

        JPanel root = new JPanel(new BorderLayout());
        root.setBackground(ThemeManager.getBackground());

        // Top Navigation Bar
        root.add(createNavBar(), BorderLayout.NORTH);

        // Main Tabbed Navigation
        tabbedPane = new JTabbedPane();
        tabbedPane.setFont(ThemeManager.FONT_BOLD_13);
        tabbedPane.setBorder(new EmptyBorder(6, 12, 6, 12));

        scannerPanel = new LiveScannerPanel(this);
        historyPanel = new HistoryPanel();
        modelStudioPanel = new ModelStudioPanel();
        domainCheckerPanel = new DomainCheckerPanel();
        dashboardPanel = new DashboardPanel();

        tabbedPane.addTab("🔍 Live AI Scanner", scannerPanel);
        tabbedPane.addTab("📊 Scan History & Audit", historyPanel);
        tabbedPane.addTab("🧠 Model & Dataset Studio", modelStudioPanel);
        tabbedPane.addTab("🌐 Domain Credibility Checker", domainCheckerPanel);
        tabbedPane.addTab("⚙️ System & Admin Dashboard", dashboardPanel);

        tabbedPane.addChangeListener(e -> {
            int sel = tabbedPane.getSelectedIndex();
            if (sel == 1) historyPanel.refreshTable();
            if (sel == 4) dashboardPanel.refreshDashboard();
        });

        root.add(tabbedPane, BorderLayout.CENTER);

        // Status Footer
        JPanel footer = new JPanel(new BorderLayout());
        footer.setBackground(ThemeManager.getCardBackground());
        footer.setBorder(new EmptyBorder(6, 16, 6, 16));

        JLabel statusLbl = new JLabel("● Veritas AI Engine Online | Embedded Naive Bayes NLP active | Shortcuts: Ctrl+Enter (Scan), Ctrl+L (Clear)");
        statusLbl.setFont(ThemeManager.FONT_SMALL_11);
        statusLbl.setForeground(ThemeManager.getTextSecondary());

        JLabel copyLbl = new JLabel("Veritas AI Enterprise • College & Research Edition");
        copyLbl.setFont(ThemeManager.FONT_SMALL_11);
        copyLbl.setForeground(ThemeManager.getTextSecondary());

        footer.add(statusLbl, BorderLayout.WEST);
        footer.add(copyLbl, BorderLayout.EAST);

        root.add(footer, BorderLayout.SOUTH);

        add(root);
    }

    private JPanel createNavBar() {
        JPanel nav = new JPanel(new BorderLayout(15, 0));
        nav.setBackground(ThemeManager.getCardBackground());
        nav.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createMatteBorder(0, 0, 1, 0, ThemeManager.getCardBorder()),
            new EmptyBorder(10, 20, 10, 20)
        ));

        // Brand Logo & Title
        JPanel brandPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        brandPanel.setOpaque(false);
        JLabel logo = new JLabel("🛡️");
        logo.setFont(new Font("Segoe UI Emoji", Font.PLAIN, 28));

        JPanel textPanel = new JPanel(new GridLayout(2, 1));
        textPanel.setOpaque(false);
        JLabel title = new JLabel(Constants.APP_NAME);
        title.setFont(ThemeManager.FONT_TITLE);
        title.setForeground(ThemeManager.getTextPrimary());

        JLabel subtitle = new JLabel(Constants.APP_TITLE);
        subtitle.setFont(ThemeManager.FONT_SUBTITLE);
        subtitle.setForeground(ThemeManager.getTextSecondary());

        textPanel.add(title);
        textPanel.add(subtitle);
        brandPanel.add(logo);
        brandPanel.add(textPanel);

        // Right Actions
        JPanel rightActions = new JPanel(new FlowLayout(FlowLayout.RIGHT, 10, 0));
        rightActions.setOpaque(false);

        themeToggleBtn = new JButton("🌙 Dark Mode");
        styleButton(themeToggleBtn, ThemeManager.getInputBackground(), ThemeManager.getTextPrimary());
        themeToggleBtn.addActionListener(e -> toggleTheme());

        rightActions.add(themeToggleBtn);

        nav.add(brandPanel, BorderLayout.WEST);
        nav.add(rightActions, BorderLayout.EAST);
        return nav;
    }

    private void toggleTheme() {
        boolean dark = !ThemeManager.isDarkMode();
        ThemeManager.setDarkMode(dark);
        themeToggleBtn.setText(dark ? "☀️ Light Mode" : "🌙 Dark Mode");
        SwingUtilities.updateComponentTreeUI(this);
        repaint();
    }

    private void initShortcuts() {
        JRootPane root = getRootPane();

        // Ctrl + Enter: Trigger Scan
        KeyStroke scanStroke = KeyStroke.getKeyStroke(KeyEvent.VK_ENTER, KeyEvent.CTRL_DOWN_MASK);
        root.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(scanStroke, "triggerScan");
        root.getActionMap().put("triggerScan", new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if (tabbedPane.getSelectedIndex() != 0) {
                    tabbedPane.setSelectedIndex(0);
                }
                scannerPanel.triggerScan();
            }
        });

        // Ctrl + L: Clear Inputs
        KeyStroke clearStroke = KeyStroke.getKeyStroke(KeyEvent.VK_L, KeyEvent.CTRL_DOWN_MASK);
        root.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(clearStroke, "clearScanner");
        root.getActionMap().put("clearScanner", new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if (tabbedPane.getSelectedIndex() == 0) {
                    scannerPanel.clearInputs();
                }
            }
        });
    }

    private void styleButton(JButton btn, Color bg, Color fg) {
        btn.setBackground(bg);
        btn.setForeground(fg);
        btn.setFocusPainted(false);
        btn.setFont(ThemeManager.FONT_BOLD_13);
        btn.setBorder(BorderFactory.createCompoundBorder(
            BorderFactory.createLineBorder(ThemeManager.getCardBorder(), 1),
            new EmptyBorder(6, 14, 6, 14)
        ));
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
    }
}
