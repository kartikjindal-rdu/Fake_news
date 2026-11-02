package com.veritasai;

import com.veritasai.model.NewsAnalysisResult;
import com.veritasai.model.NewsInput;
import com.veritasai.service.NewsAnalysisService;
import com.veritasai.ui.MainFrame;

import javax.swing.SwingUtilities;
import javax.swing.UIManager;

/**
 * Veritas AI Enterprise Application Entry Point.
 */
public class Main {

    public static void main(String[] args) {
        if (args != null && args.length > 0) {
            runHeadlessCli(args[0]);
            return;
        }

        // Start Embedded Web Server
        try {
            com.fakenews.detector.VeritasEmbeddedServer server = new com.fakenews.detector.VeritasEmbeddedServer();
            server.start();
            server.openBrowser();
        } catch (Exception e) {
            System.err.println("Notice: Server startup: " + e.getMessage());
        }

        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception ignored) {
            }

            MainFrame frame = new MainFrame();
            frame.setVisible(true);
        });
    }

    private static void runHeadlessCli(String text) {
        System.out.println("=========================================================================");
        System.out.println("            VERITAS AI ENTERPRISE - HEADLESS ANALYSIS ENGINE             ");
        System.out.println("=========================================================================");
        NewsAnalysisService service = NewsAnalysisService.getInstance();
        NewsInput input = new NewsInput("", text);
        NewsAnalysisResult result = service.analyze(input, (step, desc) -> System.out.println(" [Step " + step + "/10] " + desc));

        System.out.println("\n-------------------------- ANALYSIS RESULT ------------------------------");
        System.out.println("Verdict          : " + result.getVerdict().getLabel());
        System.out.println("Risk Level       : " + result.getRiskLevel().getLabel() + " (" + result.getRiskScore() + "/100)");
        System.out.println("AI Confidence    : " + result.getAiConfidence() + "%");
        System.out.println("Fake Probability : " + result.getFakeProbability() + "%");
        System.out.println("Real Probability : " + result.getRealProbability() + "%");
        System.out.println("Sensationalism   : " + result.getSensationalismScore() + "%");
        System.out.println("Clickbait Index  : " + result.getClickbaitScore() + "%");
        System.out.println("Emotional Bias   : " + result.getEmotionalManipulationScore() + "% (" + result.getEmotionalTone() + ")");
        System.out.println("Readability      : " + result.getReadabilityScore() + " (" + result.getReadabilityLevel() + ")");
        System.out.println("\nJSON Payload for Mobile/Web API:\n" + result.toJson());
        System.out.println("=========================================================================");
    }
}
