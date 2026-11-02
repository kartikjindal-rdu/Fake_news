# VeriNews AI — IBM Cognos Analytics Data Dictionary

**Project:** VeriNews AI – AI-Based Fake News Detection System  
**Deliverable Directory:** `E:\AI_Fake_news_detect\IBM_Cognos_Deliverables`  
**Compatibility:** IBM Cognos Analytics 11.1 / 11.2 / 12.0+ (Data Modules, Dashboards, Reports)

---

## 1. Overview of Cognos Datasets

The VeriNews AI Cognos Data Package consists of five clean, structured, verified datasets designed for multidimensional business intelligence and scientific performance analysis:

1. `cognos_kpi_summary.csv` — High-level executive KPI metrics for dashboard summary cards.
2. `cognos_dataset_distribution.csv` — ISOT research corpus class and category breakdowns.
3. `cognos_model_performance.csv` — Verified evaluation metrics across all four ML classifiers.
4. `cognos_confusion_matrix.csv` — Error matrix breakdown (TP, TN, FP, FN) on 8,933 test samples.
5. `cognos_dataset_bias_audit.csv` — Empirical data leakage and source-marker shortcut audit results.
6. `cognos_scan_intelligence_history.csv` — Operational telemetry logs from the live forensic scanner.

---

## 2. Table-by-Table Data Dictionary

### Table 1: `cognos_kpi_summary.csv` (Executive Metric Table)
| Field Name | Cognos Data Type | Usage / Role | Description | Example Values |
|:---|:---|:---|:---|:---|
| `kpi_id` | Text (Varchar) | Identifier | Unique key for KPI metric | `KPI-001`, `KPI-006` |
| `kpi_metric` | Text (Varchar) | Attribute | Business/Technical label of the metric | `Total Dataset Records`, `Best Individual Accuracy` |
| `metric_value` | Decimal / Float | Measure | Numeric magnitude for calculations | `44898`, `98.84` |
| `formatted_value` | Text (Varchar) | Attribute | Display-ready string with commas or percent signs | `"44,898"`, `"98.84%"` |
| `unit` | Text (Varchar) | Attribute | Unit of measurement | `Articles`, `Percentage`, `Classifiers` |
| `category` | Text (Varchar) | Attribute | Thematic grouping | `Corpus`, `Performance`, `Architecture` |
| `benchmark_context` | Text (Varchar) | Attribute | Scientific or operational context | `"Held-out 20% group-aware stratified split"` |

---

### Table 2: `cognos_dataset_distribution.csv` (Corpus Composition Table)
| Field Name | Cognos Data Type | Usage / Role | Description | Example Values |
|:---|:---|:---|:---|:---|
| `category_id` | Text (Varchar) | Identifier | Primary key for dataset slice | `CAT-001`, `CAT-006` |
| `class_label` | Text (Varchar) | Attribute | Binary classification ground truth | `FAKE`, `REAL` |
| `subject_category` | Text (Varchar) | Attribute | Original metadata topic category | `politics`, `worldnews`, `Government News` |
| `record_count` | Integer | Measure | Number of articles in category | `11500`, `11272` |
| `percentage_of_class` | Text (Varchar) | Attribute | Percentage within fake or real class | `48.98%`, `52.63%` |
| `percentage_of_total` | Text (Varchar) | Attribute | Percentage relative to entire corpus (44,898) | `25.61%`, `25.11%` |
| `source_leakage_risk` | Text (Varchar) | Attribute | Assessed severity of metadata shortcut | `High`, `Critical` |

---

### Table 3: `cognos_model_performance.csv` (ML Performance Fact Table)
| Field Name | Cognos Data Type | Usage / Role | Description | Example Values |
|:---|:---|:---|:---|:---|
| `model_id` | Text (Varchar) | Identifier | Primary key for classifier | `MOD-001`, `MOD-004` |
| `model_name` | Text (Varchar) | Attribute | Algorithm name | `Logistic Regression`, `Linear SVM`, `Hybrid Ensemble` |
| `architecture_branch` | Text (Varchar) | Attribute | System branch tier | `Traditional ML`, `Ensemble Decision Layer` |
| `feature_dimension` | Text (Varchar) | Attribute | Dimensionality of input representation | `50000`, `5000`, `Multi-Classifier Consensus` |
| `accuracy` | Decimal (2) | Measure | Overall classification accuracy percentage | `98.68`, `98.84`, `97.38`, `98.79` |
| `precision` | Decimal (2) | Measure | Positive predictive value percentage | `98.15`, `98.31`, `95.74` |
| `recall` | Decimal (2) | Measure | Sensitivity / true positive rate percentage | `99.08`, `99.24`, `98.87`, `99.31` |
| `f1_score` | Decimal (2) | Measure | Harmonic mean of precision and recall | `98.61`, `98.78`, `97.28`, `98.73` |
| `misclassifications` | Integer | Measure | Absolute count of classification errors | `118`, `104`, `234`, `108` |
| `evaluation_samples` | Integer | Measure | Total held-out test split size | `8933` |
| `error_rate_pct` | Text (Varchar) | Attribute | Error rate string | `1.16%`, `1.21%` |
| `loss_optimization` | Text (Varchar) | Attribute | Mathematical loss / splitting criterion | `Squared Hinge`, `Log-loss (L2 penalty)` |
| `avg_inference_latency_ms`| Decimal (1) | Measure | CPU execution latency per document (ms) | `2.8`, `3.2`, `4.5`, `28.5` |

---

### Table 4: `cognos_confusion_matrix.csv` (Classification Error Matrix)
| Field Name | Cognos Data Type | Usage / Role | Description | Example Values |
|:---|:---|:---|:---|:---|
| `matrix_id` | Text (Varchar) | Identifier | Quadrant identifier | `CM-001` through `CM-004` |
| `actual_class` | Text (Varchar) | Attribute | Ground-truth binary class label | `Actual FAKE (0)`, `Actual REAL (1)` |
| `predicted_class`| Text (Varchar) | Attribute | Ensemble predicted class label | `Predicted FAKE (0)`, `Predicted REAL (1)` |
| `quadrant_type` | Text (Varchar) | Attribute | Standard diagnostic metric quadrant | `True Negative (TN)`, `False Positive (FP)`, etc. |
| `sample_count` | Integer | Measure | Total articles in quadrant ($N=8,933$) | `4592`, `80`, `28`, `4233` |
| `percentage_of_test_set`| Text (Varchar)| Attribute | Proportional share of total test set | `51.40%`, `0.90%`, `0.31%`, `47.39%` |
| `percentage_of_actual_class`| Text| Attribute | Proportional accuracy within true class | `98.29%`, `99.34%` |
| `clinical_forensic_interpretation`| Text| Attribute| Operational meaning of the outcome | `"Type I Error: Fake news slipped through as real"` |

---

### Table 5: `cognos_dataset_bias_audit.csv` (Integrity & Leakage Audit Table)
| Field Name | Cognos Data Type | Usage / Role | Description | Example Values |
|:---|:---|:---|:---|:---|
| `experiment_id` | Text (Varchar) | Identifier | Audit experiment code | `EXP-001` through `EXP-005` |
| `audit_experiment` | Text (Varchar) | Attribute | Name of the ablation/leakage test | `Subject-Only Classification`, `Source-Marker-Only` |
| `feature_scope_tested` | Text (Varchar) | Attribute | Features fed into classifier | `Metadata 'subject' column only`, `Cleaned body text` |
| `evaluated_accuracy` | Decimal (2) | Measure | Empirical accuracy percentage | `100.00`, `99.25`, `98.71`, `0.00` |
| `leakage_risk_level` | Text (Varchar) | Attribute | Risk of model shortcutting | `Critical`, `High`, `Minimal`, `None` |
| `scientific_finding` | Text (Varchar) | Attribute | Consequence of experiment | `"Dataset categories correlate 100% with fake/real"` |
| `mitigation_in_verinews`| Text (Varchar)| Attribute | Architectural defense applied | `"Exclude subject metadata entirely from vectorizer"` |

---

### Table 6: `cognos_scan_intelligence_history.csv` (Forensic Telemetry Fact Table)
| Field Name | Cognos Data Type | Usage / Role | Description | Example Values |
|:---|:---|:---|:---|:---|
| `scan_id` | Text (Varchar) | Identifier | Primary key for scan event | `VERITAS-2026-001001` |
| `timestamp` | DateTime (ISO) | Attribute (Time) | Exact UTC timestamp of inference | `2026-09-09T11:57:31+05:30` |
| `domain` | Text (Varchar) | Attribute | Source publication domain | `reuters.com`, `who.int`, `conspiracy-daily-leak.net` |
| `headline` | Text (Varchar) | Attribute | Analyzed article headline | `"NASA James Webb Space Telescope..."` |
| `final_risk_level` | Text (Varchar) | Attribute | 4-tier risk classification | `LOW`, `MODERATE`, `HIGH`, `CRITICAL` |
| `risk_score` | Decimal (1) | Measure | Composite risk index (0 - 100) | `12.4`, `88.5`, `74.0` |
| `analysis_confidence` | Decimal (1) | Measure | AI confidence level (0 - 100) | `94.8`, `96.2`, `91.5` |
| `clickbait_score` | Decimal (1) | Measure | Clickbait heuristic index (0 - 100) | `5.0`, `95.0`, `88.0` |
| `sensationalism_score`| Decimal (1) | Measure | Hyperbole index (0 - 100) | `8.0`, `90.0`, `75.0` |
| `emotional_score` | Decimal (1) | Measure | Emotion/fear manipulation index | `10.0`, `85.0`, `70.0` |
| `urgency_score` | Decimal (1) | Measure | Artificial urgency markers index | `5.0`, `92.0`, `65.0` |
| `domain_risk_score` | Decimal (1) | Measure | Domain trust inverse index | `5.0`, `90.0`, `70.0` |
| `headline_consistency_score`| Decimal (1)| Measure| Semantic alignment score | `92.5`, `24.0`, `38.0` |
| `writing_style` | Text (Varchar) | Attribute | Forensic writing style label | `Formal`, `Urgent`, `Aggressive`, `Academic` |
| `ml_verdict` | Text (Varchar) | Attribute | Ensemble classification label | `REAL`, `FAKE` |

---

## 3. Cognos Data Module & Relationship Model

In IBM Cognos Analytics, import these files into a unified **Data Module**:
- **Fact Table 1:** `cognos_model_performance` (Central model evaluation fact table).
- **Fact Table 2:** `cognos_scan_intelligence_history` (Live operational forensic event fact table).
- **Dimension 1:** `cognos_dataset_distribution` (Joined on class label or filtered by corpus slice).
- **Dimension 2:** `cognos_confusion_matrix` (Linked to `Hybrid Ensemble` metrics).
- **Dimension 3:** `cognos_dataset_bias_audit` (Standalone comparative audit analysis).
- **Card Feed:** `cognos_kpi_summary` (Direct scalar metric binding for top KPI cards).
