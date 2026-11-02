package com.veritasai.model;

/**
 * Encapsulates ML model performance metrics, training state, and confusion matrix.
 */
public class ModelMetrics {

    private String modelName;
    private String version;
    private String algorithm;
    private String trainingDate;
    private String datasetName;
    private boolean isTrained;

    // Performance Metrics
    private double accuracy;
    private double precision;
    private double recall;
    private double f1Score;

    // Confusion Matrix Counts
    private int truePositives;
    private int trueNegatives;
    private int falsePositives;
    private int falseNegatives;

    public ModelMetrics() {
        this.modelName = "Veritas-Multinomial-NB";
        this.version = "v1.2.0";
        this.algorithm = "TF-IDF + Multinomial Naive Bayes (Laplace Add-1)";
        this.trainingDate = "Active Session";
        this.datasetName = "Veritas Core Benchmark Corpus";
        this.isTrained = true;
    }

    public String getModelName() { return modelName; }
    public void setModelName(String modelName) { this.modelName = modelName; }

    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }

    public String getAlgorithm() { return algorithm; }
    public void setAlgorithm(String algorithm) { this.algorithm = algorithm; }

    public String getTrainingDate() { return trainingDate; }
    public void setTrainingDate(String trainingDate) { this.trainingDate = trainingDate; }

    public String getDatasetName() { return datasetName; }
    public void setDatasetName(String datasetName) { this.datasetName = datasetName; }

    public boolean isTrained() { return isTrained; }
    public void setTrained(boolean trained) { isTrained = trained; }

    public double getAccuracy() { return accuracy; }
    public void setAccuracy(double accuracy) { this.accuracy = accuracy; }

    public double getPrecision() { return precision; }
    public void setPrecision(double precision) { this.precision = precision; }

    public double getRecall() { return recall; }
    public void setRecall(double recall) { this.recall = recall; }

    public double getF1Score() { return f1Score; }
    public void setF1Score(double f1Score) { this.f1Score = f1Score; }

    public int getTruePositives() { return truePositives; }
    public void setTruePositives(int truePositives) { this.truePositives = truePositives; }

    public int getTrueNegatives() { return trueNegatives; }
    public void setTrueNegatives(int trueNegatives) { this.trueNegatives = trueNegatives; }

    public int getFalsePositives() { return falsePositives; }
    public void setFalsePositives(int falsePositives) { this.falsePositives = falsePositives; }

    public int getFalseNegatives() { return falseNegatives; }
    public void setFalseNegatives(int falseNegatives) { this.falseNegatives = falseNegatives; }
}
