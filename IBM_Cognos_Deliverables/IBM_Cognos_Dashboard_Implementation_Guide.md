# IBM Cognos Analytics Dashboard Implementation Guide

**Dashboard Title:** VeriNews AI – Fake News Detection & Intelligence Analytics  
**Target Environment:** IBM Cognos Analytics (v11.1 / 11.2 / 12.0+)  
**Deliverables Folder:** `E:\AI_Fake_news_detect\IBM_Cognos_Deliverables`  
**Theme Style:** Enterprise Dark Blue (`#0B132B` / `#1C2541` / `#3A506B`)

---

## 1. Executive Summary

This implementation guide outlines the exact, end-to-end procedure for building the enterprise Business Intelligence dashboard **"VeriNews AI – Fake News Detection & Intelligence Analytics"** in **IBM Cognos Analytics**. 

The dashboard provides institutional transparency into:
- The composition and scale of the underlying ISOT research corpus ($44,898$ articles).
- Empirical comparative performance across all four machine learning classifiers.
- The 4-quadrant diagnostic confusion matrix on the held-out test split ($8,933$ samples).
- Groundbreaking empirical audit results exposing dataset metadata leakage and source-attribution bias.
- Operational telemetry and risk scoring from the live forensic scanner.

---

## 2. Step-by-Step Data Onboarding in IBM Cognos Analytics

### Step 2.1: Upload Data Files
1. Launch IBM Cognos Analytics portal (`http://<cognos-server>:<port>/bi/`).
2. Navigate to **Manage** (bottom left) or click the **+ (New)** button in the navigation bar.
3. Select **Upload files**.
4. In the file picker, navigate to `E:\AI_Fake_news_detect\IBM_Cognos_Deliverables\` and select:
   - `cognos_kpi_summary.csv`
   - `cognos_dataset_distribution.csv`
   - `cognos_model_performance.csv`
   - `cognos_confusion_matrix.csv`
   - `cognos_dataset_bias_audit.csv`
   - `cognos_scan_intelligence_history.csv`
5. Click **Open**. Cognos will parse each CSV into your **My Content** folder.

### Step 2.2: Create the Unified Data Module
1. Click **+ (New)** -> **Data module**.
2. Under **Select sources**, navigate to **My Content** and select all 6 uploaded CSV tables.
3. Click **Start**.
4. In the Data Module modeling view:
   - Verify that column usage types are correctly recognized (e.g. `sample_count`, `record_count`, `accuracy` set as **Measure**, while `model_name`, `class_label` set as **Identifier / Attribute**).
   - Set aggregation rule for `accuracy`, `precision`, `recall`, `f1_score` to **Average** (or **None** for raw comparison rows).
   - Set aggregation rule for `sample_count`, `record_count`, `misclassifications` to **Total / Sum**.
5. Click **Save** in the upper toolbar and name the module:  
   `VeriNews_AI_Cognos_Data_Module`.

---

## 3. Dashboard Layout & Visual Architecture

### Canvas Layout Grid (12-Column Responsive Blueprint)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  HEADER BANNER: VeriNews AI – Fake News Detection & Intelligence Analytics (Dark Navy Blue #0B132B)    │
│  Global Interactive Filters: [Model Selector] [Class Filter: ALL/FAKE/REAL] [Date Range Picker]        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ROW 1: EXECUTIVE KPI SUMMARY CARDS                                                                    │
│  [Total Corpus: 44,898] [Fake News: 23,481] [Real News: 21,417] [Test: 8,933] [Models: 4] [Peak: 98.8%]│
├───────────────────────────────────────────────────────────────────┬────────────────────────────────────┤
│  ROW 2: VISUALIZATION 1 (Donut Chart)                             │  ROW 2: VISUALIZATION 2 (Column)   │
│  Fake vs Real News Distribution                                   │  Model Accuracy Comparison         │
│  (Fake: 52.3% | Real: 47.7% breakdown)                            │  (LR: 98.68% | SVM: 98.84% | RF...)│
├───────────────────────────────────────────────────────────────────┴────────────────────────────────────┤
│  ROW 3: VISUALIZATION 3 (Grouped Bar Chart - Model Performance Analysis)                               │
│  Comparison of Accuracy, Precision, Recall, and F1-score across all 4 candidate algorithms             │
├───────────────────────────────────────────────────┬────────────────────────────────────────────────────┤
│  ROW 4: VISUALIZATION 4 (Confusion Matrix Table)  │  ROW 4: VISUALIZATION 5 (Dataset Bias Audit)       │
│  Actual vs Predicted Diagnostic Quadrants         │  Horizontal Bar Chart of Leakage Experiments       │
│  (4,592 TN | 80 FP | 28 FN | 4,233 TP)            │  (Subject: 100% | Source: 99.25% | Cleaned: 98.7%) │
├───────────────────────────────────────────────────┴────────────────────────────────────────────────────┤
│  ROW 5: VISUALIZATION 6 (Model Comparison Detail Table)                                                │
│  Full algorithmic specifications, loss functions, parameters, misclassifications, and CPU latencies     │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Detailed Component Configuration

### A. Global Theme Settings
- **Page Background:** Dark `#0B132B` (Hex: `0B132B`)
- **Card / Widget Background:** Dark Slate Blue `#1C2541` (Hex: `1C2541`)
- **Card Borders:** Subtle Border `#3A506B` (Hex: `3A506B`, 1px solid)
- **Primary Accent / Metrics:** Cyan `#48CAE4`
- **Verified / Real News Accent:** Emerald `#38B000` / `#5BC0BE`
- **Fake / Misinformation Accent:** Coral / Crimson `#E63946` / `#F26419`
- **Text Typography:** Segoe UI / Roboto, Clean White `#FFFFFF` for primary titles, Light Silver `#CBD5E1` for labels.

---

### B. KPI Cards (Top Row)
Create 6 **Summary / KPI Card** widgets using `cognos_kpi_summary`:
1. **Total Dataset Records:**
   - Field: `metric_value` (where `kpi_id = 'KPI-001'`)
   - Label: `Total Dataset Records`
   - Value: `44,898`
   - Subtitle: `ISOT Benchmark Corpus`
2. **Fake News Records:**
   - Field: `metric_value` (where `kpi_id = 'KPI-002'`)
   - Label: `Fake News Records`
   - Value: `23,481` (52.3% share, Coral border)
3. **Real News Records:**
   - Field: `metric_value` (where `kpi_id = 'KPI-003'`)
   - Label: `Real News Records`
   - Value: `21,417` (47.7% share, Emerald border)
4. **Evaluation Split:**
   - Field: `metric_value` (where `kpi_id = 'KPI-004'`)
   - Label: `Held-Out Test Samples`
   - Value: `8,933` (0.00% exact text overlap)
5. **Ensemble Size:**
   - Field: `metric_value` (where `kpi_id = 'KPI-005'`)
   - Label: `Evaluated Classifiers`
   - Value: `4` (LR, LinearSVC, RF, Voting Ensemble)
6. **Best Classifier Accuracy:**
   - Field: `metric_value` (where `kpi_id = 'KPI-006'`)
   - Label: `Peak Model Accuracy`
   - Value: `98.84%` (Linear SVM) / `98.79%` (Ensemble)

---

### C. Visualization 1: Fake vs Real News Distribution (Donut Chart)
- **Chart Type:** `Donut` (or `Pie`)
- **Data Source:** `cognos_dataset_distribution`
- **Segments / Categories:** `class_label` (`FAKE`, `REAL`)
- **Size / Values:** `record_count`
- **Color Palette:**
  - `FAKE`: Crimson / Coral `#E63946`
  - `REAL`: Emerald `#38B000`
- **Center Label:** `44,898 Articles`
- **Drill-down:** Clicking `FAKE` or `REAL` filters the entire canvas to category breakdowns (`politics`, `worldnews`, etc.).

---

### D. Visualization 2: Model Accuracy Comparison (Bar / Column Chart)
- **Chart Type:** `Column Chart`
- **Data Source:** `cognos_model_performance`
- **Bars (X-Axis):** `model_name` (Logistic Regression, Linear SVM, Random Forest, Hybrid Ensemble)
- **Length (Y-Axis):** `accuracy` (Range formatted: 95% to 100%)
- **Data Labels:** Enabled (`98.68%`, `98.84%`, `97.38%`, `98.79%`)
- **Color:** Gradient Cyan to Deep Navy (`#48CAE4`)

---

### E. Visualization 3: Model Performance Analysis (Grouped Bar Chart)
- **Chart Type:** `Grouped Bar Chart` (Clustered Column)
- **Data Source:** `cognos_model_performance`
- **Categories (X-Axis):** `model_name`
- **Series (Color Cluster):**
  - Metric 1: `accuracy` (Color: `#48CAE4` Cyan)
  - Metric 2: `precision` (Color: `#5BC0BE` Teal)
  - Metric 3: `recall` (Color: `#F39C12` Amber)
  - Metric 4: `f1_score` (Color: `#8E44AD` Purple)
- **Y-Axis Scale:** Minimum $94.0\%$, Maximum $100.0\%$
- **Purpose:** Highlights that while Linear SVM has the highest raw accuracy ($98.84\%$), the Hybrid Ensemble achieves the highest recall ($99.31\%$), which is critical for minimizing false negatives in misinformation surveillance.

---

### F. Visualization 4: Confusion Matrix (Crosstab / Matrix Heatmap)
- **Chart Type:** `Crosstab` or `Heatmap Table`
- **Data Source:** `cognos_confusion_matrix`
- **Rows:** `actual_class` (`Actual FAKE (0)`, `Actual REAL (1)`)
- **Columns:** `predicted_class` (`Predicted FAKE (0)`, `Predicted REAL (1)`)
- **Values / Cell Measure:** `sample_count`
- **Cell Breakdown:**
  - Top-Left (TN): `4,592` (98.29% correct fake detection)
  - Top-Right (FP): `80` (1.71% false alarms)
  - Bottom-Left (FN): `28` (0.66% missed real news)
  - Bottom-Right (TP): `4,233` (99.34% correct real detection)
- **Conditional Color Formatting:**
  - Diagonal cells (TN, TP): Dark Green background (`#1B4332`)
  - Off-diagonal cells (FP, FN): Dark Red/Amber background (`#7F1D1D`)

---

### G. Visualization 5: Dataset Bias & Leakage Audit (Horizontal Bar Chart)
- **Chart Type:** `Horizontal Bar Chart`
- **Data Source:** `cognos_dataset_bias_audit`
- **Y-Axis (Experiments):** `audit_experiment`
- **X-Axis (Accuracy):** `evaluated_accuracy`
- **Bar Values:**
  - `Subject-Only Classification`: **100.00%** (Catastrophic Metadata Leakage)
  - `Source-Marker-Only Classification`: **99.25%** (Publisher Shortcut)
  - `Source-Neutral Removal Evaluation`: **98.71%** (Stylistic / Lexical Signal)
- **Data Markers / Annotations:** Red callout badge on 100% and 99.25% indicating "Leakage Artifacts". Green badge on 98.71% indicating "Sanitized Robust Generalization".

---

### H. Visualization 6: Comprehensive Model Comparison Detail Table
- **Chart Type:** `List` / `Data Table`
- **Data Source:** `cognos_model_performance`
- **Columns:**
  1. `model_name` (Algorithm Name)
  2. `feature_dimension` (Feature Space)
  3. `accuracy` (Accuracy %)
  4. `precision` (Precision %)
  5. `recall` (Recall %)
  6. `f1_score` (F1 Score %)
  7. `misclassifications` (Error Count out of 8,933)
  8. `loss_optimization` (Mathematical Optimization Rule)
  9. `avg_inference_latency_ms` (Latency per document)

---

## 5. Interactive Filtering & Drill-Down Configuration

In IBM Cognos Analytics Dashboard edit mode:
1. **Model Filter Dropdown:**
   - Create a **List filter** widget tied to `model_name`.
   - Allows users to isolate single classifier metrics across all performance charts.
2. **Ground Truth Class Filter:**
   - Link `cognos_dataset_distribution.class_label` to cross-filter scan telemetry and category breakdowns.
3. **Interactive Chart Selection:**
   - Enable **Dashboard communication** (enabled by default in Cognos 11.2/12.0) so clicking on a slice in the Donut Chart automatically filters the audit and confusion matrix views.
4. **Time & Forensic Risk Filters:**
   - Connect `cognos_scan_intelligence_history.final_risk_level` (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`) as a side navigation filter to inspect live scanner distribution.

---

## 6. Deployment Verification & Status Disclosure

- **CSV Package Readiness:** Complete and verified in `E:\AI_Fake_news_detect\IBM_Cognos_Deliverables`.
- **Cognos Server Status:** IBM Cognos Analytics is an external enterprise Business Intelligence suite. Because this development workstation runs the local Python/React AI stack without an active IBM Cognos Server daemon running on port 9300, the complete datasets, data module schemas, and layout configurations are provided for immediate upload and deployment into the institution's Cognos environment.
