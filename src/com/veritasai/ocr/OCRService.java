package com.veritasai.ocr;

import java.io.File;

/**
 * Interface for Optical Character Recognition (OCR) screenshot text extraction.
 */
public interface OCRService {

    String extractTextFromImage(File imageFile) throws Exception;

    boolean isTesseractInstalled();
}
