
# ============================================================
# VERINEWS AI 2.0 - FINAL MODEL TRAINING AND EVALUATION
# Logistic Regression + Linear SVM + Random Forest + Hybrid
# ============================================================

import os
import time
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, VotingClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)

# ------------------------------------------------------------
# 1. CONFIGURATION
# ------------------------------------------------------------

BASE_PATH = r"E:\AI_Fake_news_detect"
DATASET_PATH = os.path.join(BASE_PATH, "Dataset")
OUTPUT_PATH = os.path.join(
    BASE_PATH, "Final_Research_Implementation"
)

os.makedirs(OUTPUT_PATH, exist_ok=True)

fake_path = os.path.join(DATASET_PATH, "Fake.csv")
true_path = os.path.join(DATASET_PATH, "True.csv")

print("=" * 65)
print("             VERINEWS AI 2.0")
print("        FINAL ML EXPERIMENT")
print("=" * 65)

# ------------------------------------------------------------
# 2. DATASET LOADING
# ------------------------------------------------------------

print("\n[1] Loading Dataset...")

fake_df = pd.read_csv(fake_path)
true_df = pd.read_csv(true_path)

fake_df["label"] = 0
true_df["label"] = 1

df = pd.concat(
    [fake_df, true_df],
    ignore_index=True
)

print("Fake records:", len(fake_df))
print("Real records:", len(true_df))
print("Total records:", len(df))

# ------------------------------------------------------------
# 3. DATA CLEANING
# ------------------------------------------------------------

print("\n[2] Cleaning Dataset...")

df = df.drop_duplicates().reset_index(drop=True)
df = df.dropna(subset=["title", "text"]).copy()

df["combined_text"] = (
    df["title"].astype(str) + " " +
    df["text"].astype(str)
)

df["combined_text"] = df["combined_text"].str.strip()

df = df[df["combined_text"] != ""].copy()

print("Cleaned records:", len(df))
print("\nClass Distribution:")
print(df["label"].value_counts())

# ------------------------------------------------------------
# 4. TRAIN TEST SPLIT
# ------------------------------------------------------------

print("\n[3] Splitting Dataset...")

X = df["combined_text"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# ------------------------------------------------------------
# 5. TF-IDF FEATURE EXTRACTION
# ------------------------------------------------------------

print("\n[4] Applying TF-IDF...")

tfidf = TfidfVectorizer(
    max_features=5000,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True
)

X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

print("Training matrix:", X_train_tfidf.shape)
print("Testing matrix:", X_test_tfidf.shape)

# ------------------------------------------------------------
# 6. DEFINE MODELS
# ------------------------------------------------------------

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        C=1.0,
        random_state=42
    ),

    "Linear SVM": LinearSVC(
        C=1.0,
        max_iter=3000,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=150,
        max_depth=30,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
}

# ------------------------------------------------------------
# 7. TRAIN INDIVIDUAL MODELS
# ------------------------------------------------------------

results = []
trained_models = {}
predictions = {}

for name, model in models.items():

    print("\n" + "=" * 55)
    print("Training:", name)

    start_time = time.time()

    model.fit(X_train_tfidf, y_train)

    elapsed = time.time() - start_time

    y_pred = model.predict(X_test_tfidf)

    trained_models[name] = model
    predictions[name] = y_pred

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
        "Training Time": elapsed
    })

    print("Accuracy:", round(accuracy * 100, 2), "%")
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("F1 Score:", round(f1, 4))
    print("Training Time:", round(elapsed, 2), "seconds")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["FAKE", "REAL"]
        )
    )

# ------------------------------------------------------------
# 8. HYBRID ENSEMBLE MODEL
# ------------------------------------------------------------

print("\n" + "=" * 55)
print("Training Hybrid Ensemble Model...")

hybrid = VotingClassifier(
    estimators=[
        ("lr", models["Logistic Regression"]),
        ("svm", models["Linear SVM"]),
        ("rf", models["Random Forest"])
    ],
    voting="hard",
    weights=[1, 1, 1],
    n_jobs=1
)

start_time = time.time()

hybrid.fit(X_train_tfidf, y_train)

hybrid_time = time.time() - start_time

hybrid_pred = hybrid.predict(X_test_tfidf)

trained_models["Hybrid Ensemble"] = hybrid
predictions["Hybrid Ensemble"] = hybrid_pred

accuracy = accuracy_score(y_test, hybrid_pred)
precision = precision_score(y_test, hybrid_pred)
recall = recall_score(y_test, hybrid_pred)
f1 = f1_score(y_test, hybrid_pred)

results.append({
    "Model": "Hybrid Ensemble",
    "Accuracy": accuracy,
    "Precision": precision,
    "Recall": recall,
    "F1 Score": f1,
    "Training Time": hybrid_time
})

print("Hybrid Accuracy:", round(accuracy * 100, 2), "%")
print("Hybrid Precision:", round(precision, 4))
print("Hybrid Recall:", round(recall, 4))
print("Hybrid F1 Score:", round(f1, 4))

print("\nHybrid Classification Report:")
print(
    classification_report(
        y_test,
        hybrid_pred,
        target_names=["FAKE", "REAL"]
    )
)

# ------------------------------------------------------------
# 9. MODEL COMPARISON
# ------------------------------------------------------------

print("\n" + "=" * 65)
print("FINAL MODEL COMPARISON")
print("=" * 65)

results_df = pd.DataFrame(results)

print(
    results_df.round(4).to_string(index=False)
)

results_df.to_csv(
    os.path.join(OUTPUT_PATH, "model_comparison.csv"),
    index=False
)

# ------------------------------------------------------------
# 10. ACCURACY COMPARISON GRAPH
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

sns.barplot(
    data=results_df,
    x="Model",
    y="Accuracy"
)

plt.title("VeriNews AI - Model Accuracy Comparison")
plt.ylabel("Accuracy")
plt.xlabel("Machine Learning Models")
plt.ylim(0, 1)
plt.xticks(rotation=15)
plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_PATH, "accuracy_comparison.png"),
    dpi=300
)

plt.show()

# ------------------------------------------------------------
# 11. CONFUSION MATRICES
# ------------------------------------------------------------

for name, y_pred in predictions.items():

    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(6, 5))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["FAKE", "REAL"],
        yticklabels=["FAKE", "REAL"]
    )

    plt.title(name + " - Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")
    plt.tight_layout()

    safe_name = name.lower().replace(" ", "_")

    plt.savefig(
        os.path.join(
            OUTPUT_PATH,
            safe_name + "_confusion_matrix.png"
        ),
        dpi=300
    )

    plt.show()

# ------------------------------------------------------------
# 12. SAVE FINAL ARTIFACTS
# ------------------------------------------------------------

print("\nSaving final model artifacts...")

joblib.dump(
    tfidf,
    os.path.join(OUTPUT_PATH, "final_tfidf_vectorizer.pkl")
)

for name, model in trained_models.items():

    filename = name.lower().replace(" ", "_") + ".pkl"

    joblib.dump(
        model,
        os.path.join(OUTPUT_PATH, filename)
    )

# ------------------------------------------------------------
# 13. SAVE TEST DATA FOR REPRODUCIBILITY
# ------------------------------------------------------------

test_results = pd.DataFrame({
    "text": X_test.reset_index(drop=True),
    "actual_label": y_test.reset_index(drop=True),
    "hybrid_prediction": hybrid_pred
})

test_results.to_csv(
    os.path.join(OUTPUT_PATH, "hybrid_test_predictions.csv"),
    index=False
)

# ------------------------------------------------------------
# 14. FINAL SUMMARY
# ------------------------------------------------------------

best_model = results_df.loc[
    results_df["F1 Score"].idxmax()
]

print("\n" + "=" * 65)
print("             FINAL EXPERIMENT COMPLETED")
print("=" * 65)

print("Best model by F1 Score:", best_model["Model"])
print("Best F1 Score:", round(best_model["F1 Score"], 4))

print("\nAll artifacts saved in:")
print(OUTPUT_PATH)

print("\nVeriNews AI Final Experiment Completed Successfully!")


# ==================================================
# STEP 15: HYBRID MODEL ROBUSTNESS TESTING
# ==================================================

import re
import random

print("\n========== ROBUSTNESS TESTING ==========")

# Sample news from existing test dataset
sample_texts = X_test.sample(
    n=min(100, len(X_test)),
    random_state=42
)

sample_labels = y_test.loc[sample_texts.index]

def add_noise(text):
    words = str(text).split()

    # Remove a few words
    if len(words) > 10:
        del words[3]

    # Change text capitalization
    return " ".join(words).upper()

noisy_texts = sample_texts.apply(add_noise)

# Original predictions
original_features = tfidf.transform(sample_texts)
original_predictions = hybrid.predict(original_features)

# Noisy predictions
noisy_features = tfidf.transform(noisy_texts)
noisy_predictions = hybrid.predict(noisy_features)

original_accuracy = accuracy_score(
    sample_labels,
    original_predictions
)

noisy_accuracy = accuracy_score(
    sample_labels,
    noisy_predictions
)

prediction_agreement = np.mean(
    original_predictions == noisy_predictions
)

print("Original Accuracy:", round(original_accuracy * 100, 2), "%")
print("Noisy Text Accuracy:", round(noisy_accuracy * 100, 2), "%")
print("Prediction Agreement:", round(prediction_agreement * 100, 2), "%")

robustness_results = pd.DataFrame({
    "Original Accuracy": [original_accuracy],
    "Noisy Accuracy": [noisy_accuracy],
    "Prediction Agreement": [prediction_agreement]
})

robustness_results.to_csv(
    os.path.join(OUTPUT_PATH, "robustness_results.csv"),
    index=False
)

print("\nRobustness Testing Completed!")


# ==================================================
# STEP 16: HYBRID MODEL ERROR ANALYSIS
# ==================================================

print("\n========== ERROR ANALYSIS ==========")

# Create prediction analysis dataframe
error_df = pd.DataFrame({
    "News": X_test.values,
    "Actual": y_test.values,
    "Predicted": hybrid_pred
})

# Identify incorrect predictions
errors = error_df[
    error_df["Actual"] != error_df["Predicted"]
].copy()

# False Positives: Fake predicted as Real
false_positives = errors[
    (errors["Actual"] == 0) &
    (errors["Predicted"] == 1)
]

# False Negatives: Real predicted as Fake
false_negatives = errors[
    (errors["Actual"] == 1) &
    (errors["Predicted"] == 0)
]

print("Total Test Samples:", len(error_df))
print("Total Incorrect Predictions:", len(errors))
print("False Positives:", len(false_positives))
print("False Negatives:", len(false_negatives))

print("\nError Rate:",
      round(len(errors) / len(error_df) * 100, 4), "%")

# Save all incorrect predictions
errors.to_csv(
    os.path.join(OUTPUT_PATH, "hybrid_error_analysis.csv"),
    index=False
)

print("\nSample Incorrect Predictions:")

if len(errors) > 0:
    print(errors.head(5).to_string(index=False))
else:
    print("No incorrect predictions found on this test split.")

print("\nError Analysis Completed!")

# ==================================================
# STEP 17: INDIVIDUAL MODEL VOTING ANALYSIS
# ==================================================

print("\n========== MODEL VOTING ANALYSIS ==========")

voting_df = pd.DataFrame({
    "Actual": y_test.values,
    "Logistic Regression": predictions["Logistic Regression"],
    "Linear SVM": predictions["Linear SVM"],
    "Random Forest": predictions["Random Forest"],
    "Hybrid Prediction": hybrid_pred
})

# Count votes for each class
voting_df["Fake Votes"] = (
    (voting_df["Logistic Regression"] == 0).astype(int) +
    (voting_df["Linear SVM"] == 0).astype(int) +
    (voting_df["Random Forest"] == 0).astype(int)
)

voting_df["Real Votes"] = (
    (voting_df["Logistic Regression"] == 1).astype(int) +
    (voting_df["Linear SVM"] == 1).astype(int) +
    (voting_df["Random Forest"] == 1).astype(int)
)

print("\nIndividual Model Agreement:")
print(
    (voting_df["Logistic Regression"] ==
     voting_df["Linear SVM"]).mean() * 100
)

print("\nVote Distribution:")
print(voting_df["Fake Votes"].value_counts().sort_index())

print("\nHybrid Prediction Accuracy:")
print(
    round(
        accuracy_score(
            voting_df["Actual"],
            voting_df["Hybrid Prediction"]
        ) * 100,
        2
    ),
    "%"
)

voting_df.to_csv(
    os.path.join(OUTPUT_PATH, "model_voting_analysis.csv"),
    index=False
)

print("\nModel Voting Analysis Completed!")


# ============================================================
# VERINEWS AI 2.0 - FINAL IMPLEMENTATION (STEP 8 TO 12)
# ============================================================

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

FINAL_PATH = OUTPUT_PATH

# ------------------------------------------------------------
# STEP 8: MODEL EXPLAINABILITY
# ------------------------------------------------------------

print("\n========== STEP 8: MODEL EXPLAINABILITY ==========")

feature_names = np.array(tfidf.get_feature_names_out())

lr_model = trained_models["Logistic Regression"]
svm_model = trained_models["Linear SVM"]

# Logistic Regression influential features
lr_coefficients = lr_model.coef_[0]

top_fake_indices = np.argsort(lr_coefficients)[:15]
top_real_indices = np.argsort(lr_coefficients)[-15:][::-1]

explainability_df = pd.DataFrame({
    "Fake_Indicators": feature_names[top_fake_indices],
    "Fake_Weight": lr_coefficients[top_fake_indices],
    "Real_Indicators": feature_names[top_real_indices],
    "Real_Weight": lr_coefficients[top_real_indices]
})

print("\nTop Fake Indicators:")
print(explainability_df[
    ["Fake_Indicators", "Fake_Weight"]
].to_string(index=False))

print("\nTop Real Indicators:")
print(explainability_df[
    ["Real_Indicators", "Real_Weight"]
].to_string(index=False))

explainability_df.to_csv(
    os.path.join(FINAL_PATH, "explainability_features.csv"),
    index=False
)

# Feature importance graph from Random Forest
rf_model = trained_models["Random Forest"]

rf_importance = rf_model.feature_importances_
top_indices = np.argsort(rf_importance)[-20:]

plt.figure(figsize=(10, 7))
plt.barh(
    feature_names[top_indices],
    rf_importance[top_indices]
)
plt.title("Random Forest - Top 20 Feature Importances")
plt.xlabel("Feature Importance")
plt.tight_layout()

plt.savefig(
    os.path.join(FINAL_PATH, "feature_importance.png"),
    dpi=300
)
plt.close()

print("\nExplainability analysis completed!")

# ------------------------------------------------------------
# STEP 9: INDEPENDENT NEWS PREDICTION
# ------------------------------------------------------------

print("\n========== STEP 9: NEWS PREDICTION ==========")

def predict_news(news_text):

    if not isinstance(news_text, str) or not news_text.strip():
        raise ValueError("Please provide valid news text.")

    vector = tfidf.transform([news_text])

    lr_prediction = int(
        trained_models["Logistic Regression"].predict(vector)[0]
    )

    svm_prediction = int(
        trained_models["Linear SVM"].predict(vector)[0]
    )

    rf_prediction = int(
        trained_models["Random Forest"].predict(vector)[0]
    )

    hybrid_prediction = int(
        trained_models["Hybrid Ensemble"].predict(vector)[0]
    )

    return {
        "Logistic Regression": "REAL" if lr_prediction == 1 else "FAKE",
        "Linear SVM": "REAL" if svm_prediction == 1 else "FAKE",
        "Random Forest": "REAL" if rf_prediction == 1 else "FAKE",
        "Hybrid Prediction": "REAL" if hybrid_prediction == 1 else "FAKE"
    }


sample_news = X_test.iloc[0]

print("\nSample News:")
print(sample_news[:500])

print("\nModel Predictions:")
sample_prediction = predict_news(sample_news)

for model_name, result in sample_prediction.items():
    print(model_name, ":", result)

# ------------------------------------------------------------
# STEP 10: SAVE BACKEND-READY MODEL PACKAGE
# ------------------------------------------------------------

print("\n========== STEP 10: BACKEND INTEGRATION PACKAGE ==========")

backend_package = {
    "vectorizer": tfidf,
    "models": trained_models,
    "label_mapping": {
        0: "FAKE",
        1: "REAL"
    },
    "model_names": list(trained_models.keys())
}

joblib.dump(
    backend_package,
    os.path.join(FINAL_PATH, "verinews_backend_model_package.pkl")
)

print("Backend model package saved successfully!")

# Save a standalone prediction service
prediction_service = r'''
import joblib

class VeriNewsPredictor:

    def __init__(self, model_path):
        self.package = joblib.load(model_path)
        self.vectorizer = self.package["vectorizer"]
        self.models = self.package["models"]

    def predict(self, text):

        if not isinstance(text, str) or not text.strip():
            raise ValueError("News text cannot be empty")

        features = self.vectorizer.transform([text])

        output = {}

        for name, model in self.models.items():
            prediction = int(model.predict(features)[0])
            output[name] = (
                "REAL" if prediction == 1 else "FAKE"
            )

        return output
'''

with open(
    os.path.join(FINAL_PATH, "prediction_service.py"),
    "w",
    encoding="utf-8"
) as file:
    file.write(prediction_service)

print("Prediction service file created!")

# ------------------------------------------------------------
# STEP 11: INTEGRATION TEST
# ------------------------------------------------------------

print("\n========== STEP 11: INTEGRATION TEST ==========")

package_path = os.path.join(
    FINAL_PATH,
    "verinews_backend_model_package.pkl"
)

loaded_package = joblib.load(package_path)

loaded_vectorizer = loaded_package["vectorizer"]
loaded_hybrid = loaded_package["models"]["Hybrid Ensemble"]

test_vector = loaded_vectorizer.transform([sample_news])

original_output = hybrid.predict(
    tfidf.transform([sample_news])
)[0]

reloaded_output = loaded_hybrid.predict(test_vector)[0]

print("Original Prediction:", original_output)
print("Reloaded Prediction:", reloaded_output)

if original_output == reloaded_output:
    print("Integration Test: PASSED")
else:
    print("Integration Test: FAILED")

# ------------------------------------------------------------
# STEP 12: FINAL RESEARCH SUMMARY
# ------------------------------------------------------------

print("\n========== STEP 12: FINAL RESEARCH SUMMARY ==========")

summary = {
    "dataset_records_after_cleaning": int(len(df)),
    "training_samples": int(len(X_train)),
    "testing_samples": int(len(X_test)),
    "models": {}
}

for result in results:
    summary["models"][result["Model"]] = {
        "accuracy": float(result["Accuracy"]),
        "precision": float(result["Precision"]),
        "recall": float(result["Recall"]),
        "f1_score": float(result["F1 Score"])
    }

summary["hybrid_error_count"] = int(len(errors))
summary["hybrid_false_positives"] = int(len(false_positives))
summary["hybrid_false_negatives"] = int(len(false_negatives))

with open(
    os.path.join(FINAL_PATH, "final_research_summary.json"),
    "w",
    encoding="utf-8"
) as file:
    json.dump(summary, file, indent=4)

print(json.dumps(summary, indent=4))

print("\nAll final implementation steps completed!")
print("Output folder:", FINAL_PATH)


# ============================================================
# STEP 13: DATA LEAKAGE AND GENERALIZATION AUDIT
# ============================================================

import os
import re
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

print("\n" + "=" * 65)
print("       VERINEWS AI - DATA LEAKAGE AUDIT")
print("=" * 65)

AUDIT_PATH = OUTPUT_PATH

# ------------------------------------------------------------
# TEST 1: EXACT TRAIN-TEST TEXT OVERLAP
# ------------------------------------------------------------

print("\n[TEST 1] Exact Train-Test Text Overlap")

def normalize_text(text):
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text.strip()

train_texts = set(
    X_train.apply(normalize_text)
)

test_texts = set(
    X_test.apply(normalize_text)
)

overlap = train_texts.intersection(test_texts)

print("Unique Training Texts:", len(train_texts))
print("Unique Testing Texts:", len(test_texts))
print("Exact Text Overlap:", len(overlap))

if len(overlap) == 0:
    print("Result: No exact text overlap detected.")
else:
    print("WARNING: Exact text overlap detected!")

# ------------------------------------------------------------
# TEST 2: DUPLICATE TITLE OVERLAP
# ------------------------------------------------------------

print("\n[TEST 2] Duplicate Title Overlap")

train_titles = set(
    df.loc[X_train.index, "title"].astype(str).apply(normalize_text)
)

test_titles = set(
    df.loc[X_test.index, "title"].astype(str).apply(normalize_text)
)

title_overlap = train_titles.intersection(test_titles)

print("Duplicate Titles Across Splits:", len(title_overlap))

# ------------------------------------------------------------
# TEST 3: SUBJECT / SOURCE BIAS
# ------------------------------------------------------------

print("\n[TEST 3] Subject and Label Association")

subject_table = pd.crosstab(
    df["subject"],
    df["label"]
)

print("\nSubject vs Label Distribution:")
print(subject_table)

subject_table.to_csv(
    os.path.join(AUDIT_PATH, "subject_label_distribution.csv")
)

print("\nFake and Real proportions by subject:")
print(
    pd.crosstab(
        df["subject"],
        df["label"],
        normalize="index"
    ).round(3)
)

# ------------------------------------------------------------
# TEST 4: DATE-BASED GENERALIZATION
# ------------------------------------------------------------

print("\n[TEST 4] Time-Based Generalization Test")

date_df = df.copy()

date_df["parsed_date"] = pd.to_datetime(
    date_df["date"],
    errors="coerce",
    utc=True
)

valid_dates = date_df.dropna(
    subset=["parsed_date", "combined_text", "label"]
).copy()

print("Records with valid dates:", len(valid_dates))
print("Records with invalid dates:", len(date_df) - len(valid_dates))

if len(valid_dates) >= 1000:

    valid_dates = valid_dates.sort_values("parsed_date")

    split_position = int(len(valid_dates) * 0.80)

    temporal_cutoff = valid_dates.iloc[split_position]["parsed_date"]

    temporal_train = valid_dates[
        valid_dates["parsed_date"] < temporal_cutoff
    ]

    temporal_test = valid_dates[
        valid_dates["parsed_date"] >= temporal_cutoff
    ]

    print("Temporal Cutoff:", temporal_cutoff)
    print("Temporal Training Records:", len(temporal_train))
    print("Temporal Testing Records:", len(temporal_test))

    print("\nTraining Class Distribution:")
    print(temporal_train["label"].value_counts())

    print("\nTesting Class Distribution:")
    print(temporal_test["label"].value_counts())

    if (
        temporal_train["label"].nunique() == 2
        and temporal_test["label"].nunique() == 2
    ):

        temporal_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True
        )

        temporal_X_train = temporal_vectorizer.fit_transform(
            temporal_train["combined_text"]
        )

        temporal_X_test = temporal_vectorizer.transform(
            temporal_test["combined_text"]
        )

        temporal_model = LogisticRegression(
            max_iter=1000,
            random_state=42
        )

        temporal_model.fit(
            temporal_X_train,
            temporal_train["label"]
        )

        temporal_predictions = temporal_model.predict(
            temporal_X_test
        )

        temporal_accuracy = accuracy_score(
            temporal_test["label"],
            temporal_predictions
        )

        print("\nTemporal Test Accuracy:",
              round(temporal_accuracy * 100, 2), "%")

        print("\nTemporal Classification Report:")
        print(
            classification_report(
                temporal_test["label"],
                temporal_predictions,
                target_names=["FAKE", "REAL"]
            )
        )

        temporal_results = pd.DataFrame({
            "Actual": temporal_test["label"].values,
            "Predicted": temporal_predictions
        })

        temporal_results.to_csv(
            os.path.join(
                AUDIT_PATH,
                "temporal_test_predictions.csv"
            ),
            index=False
        )

    else:
        print(
            "Temporal evaluation skipped: "
            "both classes are not present in both periods."
        )

else:
    print("Not enough valid dates for temporal evaluation.")

# ------------------------------------------------------------
# SAVE AUDIT SUMMARY
# ------------------------------------------------------------

audit_summary = {
    "exact_text_overlap": int(len(overlap)),
    "duplicate_title_overlap": int(len(title_overlap)),
    "valid_date_records": int(len(valid_dates)),
    "total_records": int(len(df))
}

import json

with open(
    os.path.join(AUDIT_PATH, "data_leakage_audit.json"),
    "w",
    encoding="utf-8"
) as file:
    json.dump(audit_summary, file, indent=4)

print("\n" + "=" * 65)
print("       DATA LEAKAGE AUDIT COMPLETED")
print("=" * 65)

print(json.dumps(audit_summary, indent=4))
print("\nAudit files saved in:", AUDIT_PATH)

# ============================================================
# STEP 14: LEAKAGE-CONTROLLED MODEL TRAINING
# ============================================================

import os
import re
import json
import time
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, VotingClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

print("\n" + "=" * 65)
print("VERINEWS AI - LEAKAGE CONTROLLED EXPERIMENT")
print("=" * 65)

# ------------------------------------------------------------
# 1. PREPARE DATA
# ------------------------------------------------------------

audit_df = df.copy().reset_index(drop=True)

audit_df = audit_df.dropna(
    subset=["title", "text", "label"]
).copy()

audit_df["combined_text"] = (
    audit_df["title"].astype(str) + " " +
    audit_df["text"].astype(str)
).str.strip()

audit_df = audit_df[
    audit_df["combined_text"] != ""
].reset_index(drop=True)

def normalize_for_grouping(text):
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text.strip()

# ------------------------------------------------------------
# 2. GROUP DUPLICATE TITLES AND EXACT TEXT
# ------------------------------------------------------------

print("\n[1] Creating duplicate groups...")

parent = list(range(len(audit_df)))

def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def union(a, b):
    root_a = find(a)
    root_b = find(b)

    if root_a != root_b:
        parent[root_b] = root_a

seen = {}

for i, row in audit_df.iterrows():

    title_key = normalize_for_grouping(row["title"])
    text_key = normalize_for_grouping(row["combined_text"])

    keys = []

    if title_key:
        keys.append(("TITLE", title_key))

    if text_key:
        keys.append(("TEXT", text_key))

    for key in keys:
        if key in seen:
            union(i, seen[key])
        else:
            seen[key] = i

groups = np.array([find(i) for i in range(len(audit_df))])

audit_df["group_id"] = groups

print("Total records:", len(audit_df))
print("Unique duplicate groups:", len(np.unique(groups)))

# ------------------------------------------------------------
# 3. STRATIFIED GROUP SPLIT
# ------------------------------------------------------------

print("\n[2] Creating group-aware train-test split...")

X = audit_df["combined_text"]
y = audit_df["label"]
group_ids = audit_df["group_id"]

splitter = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

train_indices, test_indices = next(
    splitter.split(X, y, groups=group_ids)
)

X_train_clean = X.iloc[train_indices]
X_test_clean = X.iloc[test_indices]

y_train_clean = y.iloc[train_indices]
y_test_clean = y.iloc[test_indices]

train_groups = set(group_ids.iloc[train_indices])
test_groups = set(group_ids.iloc[test_indices])

print("Training records:", len(X_train_clean))
print("Testing records:", len(X_test_clean))

print("Training class distribution:")
print(y_train_clean.value_counts())

print("\nTesting class distribution:")
print(y_test_clean.value_counts())

group_overlap = train_groups.intersection(test_groups)

print("\nGroup overlap:", len(group_overlap))

if len(group_overlap) != 0:
    raise ValueError("Duplicate groups found across train and test!")

print("Duplicate group separation: PASSED")

# ------------------------------------------------------------
# 4. TF-IDF - FIT ONLY ON TRAINING DATA
# ------------------------------------------------------------

print("\n[3] Applying TF-IDF...")

clean_vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True
)

X_train_clean_tfidf = clean_vectorizer.fit_transform(
    X_train_clean
)

X_test_clean_tfidf = clean_vectorizer.transform(
    X_test_clean
)

print("Training matrix:", X_train_clean_tfidf.shape)
print("Testing matrix:", X_test_clean_tfidf.shape)

# ------------------------------------------------------------
# 5. TRAIN THREE INDIVIDUAL MODELS
# ------------------------------------------------------------

print("\n[4] Training individual models...")

clean_models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "Linear SVM": LinearSVC(
        C=1.0,
        max_iter=3000,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=150,
        max_depth=30,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
}

clean_results = []
clean_predictions = {}

for name, model in clean_models.items():

    print("\nTraining:", name)

    start = time.time()

    model.fit(
        X_train_clean_tfidf,
        y_train_clean
    )

    elapsed = time.time() - start

    pred = model.predict(X_test_clean_tfidf)

    clean_predictions[name] = pred

    clean_results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test_clean, pred),
        "Precision": precision_score(y_test_clean, pred, zero_division=0),
        "Recall": recall_score(y_test_clean, pred, zero_division=0),
        "F1 Score": f1_score(y_test_clean, pred, zero_division=0),
        "Training Time": elapsed
    })

    print(classification_report(
        y_test_clean,
        pred,
        target_names=["FAKE", "REAL"],
        zero_division=0
    ))

# ------------------------------------------------------------
# 6. TRAIN HYBRID ENSEMBLE
# ------------------------------------------------------------

print("\n[5] Training Hybrid Ensemble...")

clean_hybrid = VotingClassifier(
    estimators=[
        ("lr", clean_models["Logistic Regression"]),
        ("svm", clean_models["Linear SVM"]),
        ("rf", clean_models["Random Forest"])
    ],
    voting="hard",
    weights=[1, 1, 1],
    n_jobs=1
)

start = time.time()

clean_hybrid.fit(
    X_train_clean_tfidf,
    y_train_clean
)

hybrid_time = time.time() - start

clean_hybrid_pred = clean_hybrid.predict(
    X_test_clean_tfidf
)

clean_predictions["Hybrid Ensemble"] = clean_hybrid_pred

clean_results.append({
    "Model": "Hybrid Ensemble",
    "Accuracy": accuracy_score(y_test_clean, clean_hybrid_pred),
    "Precision": precision_score(y_test_clean, clean_hybrid_pred, zero_division=0),
    "Recall": recall_score(y_test_clean, clean_hybrid_pred, zero_division=0),
    "F1 Score": f1_score(y_test_clean, clean_hybrid_pred, zero_division=0),
    "Training Time": hybrid_time
})

# ------------------------------------------------------------
# 7. FINAL COMPARISON
# ------------------------------------------------------------

print("\n[6] Leakage-Controlled Model Comparison")

clean_results_df = pd.DataFrame(clean_results)

print(clean_results_df.round(4).to_string(index=False))

# ------------------------------------------------------------
# 8. VERIFY NO EXACT OVERLAP
# ------------------------------------------------------------

print("\n[7] Final Duplicate Verification")

train_text_set = set(
    X_train_clean.apply(normalize_for_grouping)
)

test_text_set = set(
    X_test_clean.apply(normalize_for_grouping)
)

exact_overlap = train_text_set.intersection(test_text_set)

print("Exact normalized text overlap:", len(exact_overlap))

# ------------------------------------------------------------
# 9. SAVE ALL NEW ARTIFACTS SEPARATELY
# ------------------------------------------------------------

CLEAN_OUTPUT = os.path.join(
    OUTPUT_PATH,
    "Leakage_Controlled_Results"
)

os.makedirs(CLEAN_OUTPUT, exist_ok=True)

clean_results_df.to_csv(
    os.path.join(CLEAN_OUTPUT, "clean_model_comparison.csv"),
    index=False
)

joblib.dump(
    clean_vectorizer,
    os.path.join(CLEAN_OUTPUT, "clean_tfidf_vectorizer.pkl")
)

for name, model in clean_models.items():

    filename = name.lower().replace(" ", "_") + ".pkl"

    joblib.dump(
        model,
        os.path.join(CLEAN_OUTPUT, filename)
    )

joblib.dump(
    clean_hybrid,
    os.path.join(CLEAN_OUTPUT, "clean_hybrid_ensemble.pkl")
)

# Save test predictions
clean_test_results = pd.DataFrame({
    "Actual": y_test_clean.to_numpy(),
    "Hybrid Prediction": clean_hybrid_pred
})

clean_test_results.to_csv(
    os.path.join(CLEAN_OUTPUT, "clean_hybrid_predictions.csv"),
    index=False
)

# Save audit summary
clean_summary = {
    "records": len(audit_df),
    "training_records": len(X_train_clean),
    "testing_records": len(X_test_clean),
    "duplicate_group_overlap": len(group_overlap),
    "exact_text_overlap": len(exact_overlap),
    "models": clean_results_df.to_dict(orient="records")
}

with open(
    os.path.join(CLEAN_OUTPUT, "clean_experiment_summary.json"),
    "w",
    encoding="utf-8"
) as file:
    json.dump(clean_summary, file, indent=4)

print("\n" + "=" * 65)
print("LEAKAGE-CONTROLLED EXPERIMENT COMPLETED")
print("Results saved in:", CLEAN_OUTPUT)
print("=" * 65)


# ============================================================
# STEP 15: SUBJECT BIAS BASELINE TEST
# ============================================================

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

print("\n========== SUBJECT BIAS TEST ==========")

# Subject metadata only - no news text
subject_data = audit_df[["subject"]].fillna("UNKNOWN")
subject_labels = audit_df["label"]

# Use same group-aware train-test indices
subject_train = subject_data.iloc[train_indices]
subject_test = subject_data.iloc[test_indices]

label_train = subject_labels.iloc[train_indices]
label_test = subject_labels.iloc[test_indices]

subject_model = Pipeline([
    ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ("classifier", LogisticRegression(max_iter=1000))
])

subject_model.fit(subject_train, label_train)

subject_predictions = subject_model.predict(subject_test)

subject_accuracy = accuracy_score(
    label_test,
    subject_predictions
)

print("Subject-Only Accuracy:",
      round(subject_accuracy * 100, 2), "%")

print("\nSubject-Only Classification Report:")

print(classification_report(
    label_test,
    subject_predictions,
    target_names=["FAKE", "REAL"],
    zero_division=0
))

print("\nSubject Bias Test Completed!")

print("\nCompare this result with:")
print("Leakage-Controlled Text Hybrid Accuracy:",
      round(
          accuracy_score(y_test_clean, clean_hybrid_pred) * 100,
          2
      ), "%")

# ============================================================
# STEP 16: SOURCE BIAS AUDIT
# ============================================================

import re
import os
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

print("\n" + "=" * 65)
print("          VERINEWS AI - SOURCE BIAS AUDIT")
print("=" * 65)

# ------------------------------------------------------------
# 1. IDENTIFY PUBLISHER / SOURCE MARKERS
# ------------------------------------------------------------

print("\n[1] Detecting source-related markers...")

source_patterns = {
    "Reuters": r"\breuters\b",
    "Associated Press": r"\bassociated press\b|\bap news\b",
    "BBC": r"\bbbc\b",
    "CNN": r"\bcnn\b",
    "AFP": r"\bafp\b",
    "New York Times": r"\bnew york times\b",
    "Washington Post": r"\bwashington post\b"
}

source_df = audit_df.copy()

for source, pattern in source_patterns.items():
    source_df[source] = source_df["combined_text"].apply(
        lambda x: int(bool(re.search(pattern, str(x), re.I)))
    )

source_columns = list(source_patterns.keys())

print("\nSource marker counts:")
print(source_df[source_columns].sum())

# ------------------------------------------------------------
# 2. SOURCE MARKER VS LABEL DISTRIBUTION
# ------------------------------------------------------------

print("\n[2] Source marker and label association...")

for source in source_columns:

    subset = source_df[source_df[source] == 1]

    if len(subset) > 0:
        print("\n", source)
        print("Articles:", len(subset))
        print("Label distribution:")
        print(subset["label"].value_counts(normalize=True).round(3))

# ------------------------------------------------------------
# 3. SOURCE-ONLY CLASSIFIER
# ------------------------------------------------------------

print("\n[3] Training source-only classifier...")

source_X_train = source_df[source_columns].iloc[train_indices]
source_X_test = source_df[source_columns].iloc[test_indices]

source_y_train = source_df["label"].iloc[train_indices]
source_y_test = source_df["label"].iloc[test_indices]

source_classifier = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)

source_classifier.fit(source_X_train, source_y_train)

source_predictions = source_classifier.predict(source_X_test)

source_accuracy = accuracy_score(
    source_y_test,
    source_predictions
)

print("\nSource-Only Accuracy:",
      round(source_accuracy * 100, 2), "%")

print("\nSource-Only Classification Report:")

print(classification_report(
    source_y_test,
    source_predictions,
    target_names=["FAKE", "REAL"],
    zero_division=0
))

# ------------------------------------------------------------
# 4. REMOVE EXPLICIT SOURCE NAMES AND RETEST TEXT MODEL
# ------------------------------------------------------------

print("\n[4] Testing text after removing explicit source names...")

def remove_source_names(text):

    text = str(text)

    for pattern in source_patterns.values():
        text = re.sub(pattern, " ", text, flags=re.I)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

X_source_clean = audit_df["combined_text"].apply(
    remove_source_names
)

source_clean_vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True
)

source_clean_train = source_clean_vectorizer.fit_transform(
    X_source_clean.iloc[train_indices]
)

source_clean_test = source_clean_vectorizer.transform(
    X_source_clean.iloc[test_indices]
)

source_clean_model = LogisticRegression(
    max_iter=1000,
    random_state=42
)

source_clean_model.fit(
    source_clean_train,
    source_y_train
)

source_clean_predictions = source_clean_model.predict(
    source_clean_test
)

source_clean_accuracy = accuracy_score(
    source_y_test,
    source_clean_predictions
)

print("\nText Model Accuracy After Removing Source Names:",
      round(source_clean_accuracy * 100, 2), "%")

# ------------------------------------------------------------
# 5. SAVE SOURCE AUDIT RESULTS
# ------------------------------------------------------------

source_results = pd.DataFrame({
    "Experiment": [
        "Subject Only",
        "Source Markers Only",
        "Text After Removing Explicit Source Names"
    ],
    "Accuracy": [
        subject_accuracy,
        source_accuracy,
        source_clean_accuracy
    ]
})

print("\n========== SOURCE BIAS COMPARISON ==========")
print(source_results.to_string(index=False))

source_results.to_csv(
    os.path.join(
        CLEAN_OUTPUT,
        "source_bias_comparison.csv"
    ),
    index=False
)

print("\nSource Bias Audit Completed!")
print("Results saved in:", CLEAN_OUTPUT)


# ============================================================
# VERINEWS AI 2.0 - FINAL SOURCE-NEUTRAL EXPERIMENT
# ============================================================

import os
import re
import json
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, VotingClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

print("\n" + "=" * 70)
print("       VERINEWS AI 2.0 - FINAL RESEARCH EXPERIMENT")
print("=" * 70)

# ------------------------------------------------------------
# 1. CREATE FINAL OUTPUT DIRECTORY
# ------------------------------------------------------------

FINAL_OUTPUT = os.path.join(
    OUTPUT_PATH,
    "Final_Source_Neutral_Results"
)

os.makedirs(FINAL_OUTPUT, exist_ok=True)

# ------------------------------------------------------------
# 2. SOURCE-NEUTRAL PREPROCESSING
# ------------------------------------------------------------

print("\n[1] Source-neutral text preprocessing...")

def final_source_clean(text):

    text = str(text)

    # Remove explicit publisher names
    for pattern in source_patterns.values():
        text = re.sub(pattern, " ", text, flags=re.I)

    # Remove URLs and emails
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove common news dateline patterns
    text = re.sub(
        r"\b[A-Z][A-Z\s,.-]{2,40}\s*\([A-Z][a-zA-Z\s]+\)\s*[-:]\s*",
        " ",
        text
    )

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


neutral_texts = audit_df["combined_text"].apply(
    final_source_clean
)

neutral_train = neutral_texts.iloc[train_indices]
neutral_test = neutral_texts.iloc[test_indices]

print("Training records:", len(neutral_train))
print("Testing records:", len(neutral_test))

# ------------------------------------------------------------
# 3. TF-IDF FEATURE EXTRACTION
# ------------------------------------------------------------

print("\n[2] TF-IDF feature extraction...")

final_vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    sublinear_tf=True
)

neutral_X_train = final_vectorizer.fit_transform(
    neutral_train
)

neutral_X_test = final_vectorizer.transform(
    neutral_test
)

print("Training matrix:", neutral_X_train.shape)
print("Testing matrix:", neutral_X_test.shape)

# ------------------------------------------------------------
# 4. DEFINE FINAL MODELS
# ------------------------------------------------------------

print("\n[3] Defining final models...")

final_models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "Linear SVM": LinearSVC(
        C=1.0,
        max_iter=3000,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=150,
        max_depth=30,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
}

final_results = []
final_predictions = {}
final_trained_models = {}

# ------------------------------------------------------------
# 5. TRAIN INDIVIDUAL MODELS
# ------------------------------------------------------------

print("\n[4] Training individual models...")

for name, model in final_models.items():

    print("\nTraining:", name)

    start_time = time.time()

    model.fit(
        neutral_X_train,
        y_train_clean
    )

    training_time = time.time() - start_time

    prediction = model.predict(neutral_X_test)

    final_trained_models[name] = model
    final_predictions[name] = prediction

    final_results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test_clean, prediction),
        "Precision": precision_score(
            y_test_clean, prediction, zero_division=0
        ),
        "Recall": recall_score(
            y_test_clean, prediction, zero_division=0
        ),
        "F1 Score": f1_score(
            y_test_clean, prediction, zero_division=0
        ),
        "Training Time": training_time
    })

    print("Accuracy:",
          round(accuracy_score(y_test_clean, prediction) * 100, 2), "%")

    print(classification_report(
        y_test_clean,
        prediction,
        target_names=["FAKE", "REAL"],
        zero_division=0
    ))

# ------------------------------------------------------------
# 6. TRAIN FINAL HYBRID ENSEMBLE
# ------------------------------------------------------------

print("\n[5] Training final Hybrid Ensemble...")

final_hybrid = VotingClassifier(
    estimators=[
        ("lr", final_models["Logistic Regression"]),
        ("svm", final_models["Linear SVM"]),
        ("rf", final_models["Random Forest"])
    ],
    voting="hard",
    weights=[1, 1, 1],
    n_jobs=1
)

start_time = time.time()

final_hybrid.fit(
    neutral_X_train,
    y_train_clean
)

hybrid_training_time = time.time() - start_time

final_hybrid_prediction = final_hybrid.predict(
    neutral_X_test
)

final_predictions["Hybrid Ensemble"] = final_hybrid_prediction
final_trained_models["Hybrid Ensemble"] = final_hybrid

final_results.append({
    "Model": "Hybrid Ensemble",
    "Accuracy": accuracy_score(
        y_test_clean, final_hybrid_prediction
    ),
    "Precision": precision_score(
        y_test_clean, final_hybrid_prediction, zero_division=0
    ),
    "Recall": recall_score(
        y_test_clean, final_hybrid_prediction, zero_division=0
    ),
    "F1 Score": f1_score(
        y_test_clean, final_hybrid_prediction, zero_division=0
    ),
    "Training Time": hybrid_training_time
})

# ------------------------------------------------------------
# 7. FINAL MODEL COMPARISON
# ------------------------------------------------------------

print("\n[6] FINAL MODEL COMPARISON")

final_comparison = pd.DataFrame(final_results)

print(final_comparison.round(4).to_string(index=False))

final_comparison.to_csv(
    os.path.join(FINAL_OUTPUT, "final_model_comparison.csv"),
    index=False
)

# ------------------------------------------------------------
# 8. ACCURACY AND F1 COMPARISON GRAPH
# ------------------------------------------------------------

print("\n[7] Generating comparison graphs...")

for metric in ["Accuracy", "F1 Score"]:

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        final_comparison["Model"],
        final_comparison[metric] * 100
    )

    plt.ylim(0, 100)
    plt.title("Final Model Comparison - " + metric)
    plt.ylabel(metric + " (%)")
    plt.xticks(rotation=15)

    for bar, value in zip(
        bars, final_comparison[metric] * 100
    ):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.5,
            f"{value:.2f}%",
            ha="center"
        )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FINAL_OUTPUT,
            metric.lower().replace(" ", "_") + "_comparison.png"
        ),
        dpi=300
    )

    plt.close()

# ------------------------------------------------------------
# 9. CONFUSION MATRICES
# ------------------------------------------------------------

print("\n[8] Generating confusion matrices...")

for name, prediction in final_predictions.items():

    cm = confusion_matrix(
        y_test_clean,
        prediction
    )

    plt.figure(figsize=(6, 5))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["FAKE", "REAL"],
        yticklabels=["FAKE", "REAL"]
    )

    plt.title(name + " - Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()

    filename = name.lower().replace(" ", "_")

    plt.savefig(
        os.path.join(
            FINAL_OUTPUT,
            filename + "_confusion_matrix.png"
        ),
        dpi=300
    )

    plt.close()

# ------------------------------------------------------------
# 10. FINAL ERROR ANALYSIS
# ------------------------------------------------------------

print("\n[9] Final error analysis...")

final_errors = pd.DataFrame({
    "Actual": y_test_clean.to_numpy(),
    "Predicted": final_hybrid_prediction,
    "Text": neutral_test.to_numpy()
})

final_errors = final_errors[
    final_errors["Actual"] != final_errors["Predicted"]
]

final_errors.to_csv(
    os.path.join(FINAL_OUTPUT, "final_hybrid_errors.csv"),
    index=False
)

print("Incorrect predictions:", len(final_errors))
print("Error rate:",
      round(
          len(final_errors) / len(y_test_clean) * 100, 4
      ), "%")

# ------------------------------------------------------------
# 11. FINAL MODEL EXPLAINABILITY
# ------------------------------------------------------------

print("\n[10] Final model explainability...")

lr_final = final_trained_models["Logistic Regression"]

feature_names = np.array(
    final_vectorizer.get_feature_names_out()
)

coefficients = lr_final.coef_[0]

top_fake = np.argsort(coefficients)[:20]
top_real = np.argsort(coefficients)[-20:][::-1]

feature_report = pd.DataFrame({
    "Fake_Feature": feature_names[top_fake],
    "Fake_Weight": coefficients[top_fake],
    "Real_Feature": feature_names[top_real],
    "Real_Weight": coefficients[top_real]
})

feature_report.to_csv(
    os.path.join(FINAL_OUTPUT, "final_explainability.csv"),
    index=False
)

# ------------------------------------------------------------
# 12. SAVE FINAL MODEL PACKAGE
# ------------------------------------------------------------

print("\n[11] Saving final model package...")

final_package = {
    "vectorizer": final_vectorizer,
    "models": final_trained_models,
    "label_mapping": {
        0: "FAKE",
        1: "REAL"
    },
    "preprocessing": "final_source_clean",
    "training_features": neutral_X_train.shape[1]
}

joblib.dump(
    final_package,
    os.path.join(FINAL_OUTPUT, "final_verinews_model_package.pkl")
)

# ------------------------------------------------------------
# 13. INDEPENDENT PREDICTION FUNCTION
# ------------------------------------------------------------

def final_predict_news(text):

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Enter valid news text.")

    processed = final_source_clean(text)

    vector = final_vectorizer.transform([processed])

    output = {}

    for name, model in final_trained_models.items():

        prediction = int(model.predict(vector)[0])

        output[name] = (
            "REAL" if prediction == 1 else "FAKE"
        )

    return output


print("\n[12] Testing independent prediction...")

sample_text = neutral_test.iloc[0]

print("Sample prediction:")
print(final_predict_news(sample_text))

# ------------------------------------------------------------
# 14. FINAL RESEARCH REPORT
# ------------------------------------------------------------

print("\n[13] Creating final research report...")

best_model = final_comparison.loc[
    final_comparison["F1 Score"].idxmax()
]

report = {
    "experiment": "VeriNews AI 2.0 Final Source-Neutral Evaluation",
    "training_records": int(len(neutral_train)),
    "testing_records": int(len(neutral_test)),
    "duplicate_group_overlap": int(len(group_overlap)),
    "exact_text_overlap": 0,
    "models": final_comparison.to_dict(orient="records"),
    "hybrid_errors": int(len(final_errors)),
    "best_model_by_f1": str(best_model["Model"]),
    "best_f1_score": float(best_model["F1 Score"]),
    "subject_only_accuracy": float(subject_accuracy),
    "source_only_accuracy": float(source_accuracy)
}

with open(
    os.path.join(FINAL_OUTPUT, "final_research_report.json"),
    "w",
    encoding="utf-8"
) as file:
    json.dump(report, file, indent=4)

# ------------------------------------------------------------
# 15. FINAL SUMMARY
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("       VERINEWS AI 2.0 - EXPERIMENT COMPLETED")
print("=" * 70)

print("\nBest model:", best_model["Model"])
print("Best F1 Score:", round(best_model["F1 Score"], 4))

print("\nFinal artifacts saved at:")
print(FINAL_OUTPUT)

print("\nAll final experiments completed successfully!")

