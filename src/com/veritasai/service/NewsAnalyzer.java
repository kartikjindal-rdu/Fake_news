package com.veritasai.service;

import com.veritasai.model.NewsAnalysisResult;
import com.veritasai.model.NewsInput;

/**
 * Interface defining the contract for the core news analysis engine.
 */
public interface NewsAnalyzer {

    NewsAnalysisResult analyze(NewsInput input, AnalysisProgressListener listener);

    interface AnalysisProgressListener {
        void onProgressStep(int stepIndex, String stepDescription);
    }
}
