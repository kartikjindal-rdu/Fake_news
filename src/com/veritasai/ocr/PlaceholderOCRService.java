package com.veritasai.ocr;

import java.io.File;

/**
 * Modular OCR Service implementation prepared for native Tesseract OCR integration.
 * In environments where Tesseract native binaries are pending installation,
 * provides clear instructional messaging and architectural hook.
 */
public class PlaceholderOCRService implements OCRService {

    @Override
    public String extractTextFromImage(File imageFile) throws Exception {
        if (imageFile == null || !imageFile.exists()) {
            throw new IllegalArgumentException("Invalid image file selected.");
        }

        // Tesseract integration placeholder:
        // When Tess4J is added to classpath, instantiate net.sourceforge.tess4j.Tesseract
        // Example: Tesseract tesseract = new Tesseract(); return tesseract.doOCR(imageFile);

        return "[OCR EXTRACTED PLACEHOLDER]: Screenshot (" + imageFile.getName() + ") loaded successfully.\n" +
               "Note: To enable full live OCR character recognition, ensure Tesseract OCR binaries are linked.";
    }

    @Override
    public boolean isTesseractInstalled() {
        return false;
    }
}
