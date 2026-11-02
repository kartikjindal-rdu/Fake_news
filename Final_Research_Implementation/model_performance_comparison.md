# Model Performance Comparison & Statistical Breakdown

**Project:** VeriNews AI 2.0  
**Artifact Evaluated:** `backend/Model/final_verinews_model_package.pkl`  
**Held-Out Evaluation Split:** 8,933 samples (Stratified, Group-Aware, 0% Overlap)

---

## 1. Primary Classification Performance Comparison

| Model Architecture | Features / Parameters | Accuracy | Precision | Recall | F1-Score | Misclassifications |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression** | 50,000 TF-IDF n-grams (L2 regularized) | 98.68% | 98.15% | 99.08% | 98.61% | 118 |
| **Linear SVM (LinearSVC)** | 50,000 TF-IDF n-grams (Squared Hinge) | **98.84%** | **98.31%** | 99.24% | **98.78%** | **104** |
| **Random Forest** | 5,000 TF-IDF subspace (100 Trees) | 97.38% | 95.74% | 98.87% | 97.28% | 234 |
| **Hybrid Majority Ensemble** | 3-Model Hard Voting Consensus | 98.79% | 98.15% | **99.31%** | 98.73% | 108 |

---

## 2. Confusion Matrix (Hybrid Ensemble on Held-Out Split)

```
                       Predicted FAKE (0)       Predicted REAL (1)
 Actual FAKE (0)              4,592                     80
 Actual REAL (1)                 28                  4,233
```

- **True Negatives (TN):** 4,592 articles correctly identified as FAKE.
- **False Positives (FP):** 80 FAKE articles misclassified as REAL (Type I error).
- **False Negatives (FN):** 28 REAL articles misclassified as FAKE (Type II error).
- **True Positives (TP):** 4,233 articles correctly identified as REAL.
- **Overall Error Rate:** $\frac{108}{8,933} = 1.21\%$.

---

## 3. Dataset Leakage & Bias Impact Summary

| Audit Experiment | Input Features Used | Accuracy Achieved | Scientific Interpretation |
|:---|:---|:---:|:---|
| **Subject Metadata Shortcut** | Metadata tag only (`subject`) | **100.00%** | Catastrophic metadata leakage. Training on raw dataset fields produces 100% artificial accuracy without inspecting text. |
| **Publisher Header Shortcut** | Publisher tokens only (e.g., `(Reuters)`) | **99.25%** | Benchmark datasets inadvertently train classifiers to detect wire attribution rather than truth. |
| **Source-Neutral Cleaned Text** | Cleaned body (no publisher/datelines) | **98.71%** | Validated stylistic and grammatical signal. Models maintain high accuracy through lexical and rhetorical patterns. |
| **Temporal Split Evaluation** | Date-partitioned train/test | *Not Feasible* | Date distributions in legacy corpora lack overlapping two-class windows, preventing temporal evaluation. |

---

## 4. Key Takeaways
1. **Linear Separation in High Dimensions:** With 50,000 n-gram features, linear boundary methods (Linear SVM and Logistic Regression) outperform Random Forest both in accuracy (98.84% vs 97.38%) and inference latency ($<5$ ms vs $>40$ ms).
2. **Subspace Optimization:** Restricting Random Forest to 5,000 features maintains stability and prevents catastrophic memory consumption, while the ensemble voting layer absorbs individual classifier errors.
3. **Recall Optimization:** The Hybrid Ensemble achieves the highest recall (99.31%), minimizing the false negative rate (only 28 genuine news stories flagged as fake).
