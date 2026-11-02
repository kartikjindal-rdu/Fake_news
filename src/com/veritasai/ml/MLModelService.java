package com.veritasai.ml;

import com.veritasai.model.ModelMetrics;
import com.veritasai.model.NewsInput;

import java.util.Map;

/**
 * Interface for Machine Learning classification services.
 */
public interface MLModelService {

    void trainModel();

    Map<String, Double> predict(NewsInput input);

    ModelMetrics evaluateModel();

    ModelMetrics getModelMetrics();

    boolean isServiceAvailable();
}
