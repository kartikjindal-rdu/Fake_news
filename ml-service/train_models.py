import os
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def train_and_evaluate():
    dataset_path = os.path.join(os.path.dirname(__file__), "datasets", "news_corpus.csv")
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)

    df = pd.read_csv(dataset_path)
    df["text"] = df["title"].fillna("") + " " + df["content"].fillna("")
    df["target"] = (df["label"] == "FAKE").astype(int)

    X = df["text"]
    y = df["target"]

    print("=========================================================")
    print("      VERITAS AI — MACHINE LEARNING TRAINING SUITE       ")
    print("=========================================================")
    print(f"Total Training Samples: {len(df)}")
    print(f"Real News Count       : {sum(y == 0)}")
    print(f"Fake News Count       : {sum(y == 1)}")
    print("---------------------------------------------------------")

    # 1. Feature Extraction: TF-IDF
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=5000)
    X_vec = vectorizer.fit_transform(X)

    models = {
        "Multinomial Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(),
        "Linear SVM": LinearSVC(random_state=42),
        "Random Forest (100 Trees)": RandomForestClassifier(n_estimators=100, random_state=42)
    }

    results = {}
    for name, model in models.items():
        model.fit(X_vec, y)
        preds = model.predict(X_vec)

        acc = accuracy_score(y, preds) * 100.0
        prec = precision_score(y, preds, zero_division=0) * 100.0
        rec = recall_score(y, preds, zero_division=0) * 100.0
        f1 = f1_score(y, preds, zero_division=0) * 100.0
        cm = confusion_matrix(y, preds)

        results[name] = {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "cm": cm}

        print(f"Model: {name}")
        print(f"  • Accuracy : {acc:.1f}%")
        print(f"  • Precision: {prec:.1f}%")
        print(f"  • Recall   : {rec:.1f}%")
        print(f"  • F1-Score : {f1:.1f}%")
        print(f"  • Confusion Matrix [TN, FP; FN, TP]:\n{cm}\n")

    # Save Vectorizer and Best Classifier
    joblib.dump(vectorizer, os.path.join(models_dir, "tfidf_vectorizer.joblib"))
    joblib.dump(models["Random Forest (100 Trees)"], os.path.join(models_dir, "random_forest_model.joblib"))
    joblib.dump(models["Multinomial Naive Bayes"], os.path.join(models_dir, "naive_bayes_model.joblib"))

    print("=========================================================")
    print("  Successfully exported vectorizer and model artifacts!  ")
    print("=========================================================")

if __name__ == "__main__":
    train_and_evaluate()
