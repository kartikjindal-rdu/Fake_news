# Veritas AI - Enterprise Fake News & Misinformation Detection Platform

A multi-factor, high-performance AI Fake News and Misinformation Detection Platform built in pure Java (100% compatible with Eclipse, Android Studio, and Spring Boot).

---

## 🌟 Key Features

### 1. 🧠 Multi-Factor AI & NLP Engine
- **TF-IDF + Multinomial Naive Bayes ML**: Log-posterior calculation with Laplace add-1 smoothing.
- **Sentiment & Emotional Bias Analyzer**: Detects panic induction, outrage, artificial urgency, and hyperbole.
- **Linguistic & Sensationalism Index**: Analyzes clickbait syntax, exclamation clusters (`!!!`), question clusters (`???`), and capitalization ratios.
- **Readability & Complexity Index**: Computes Flesch Reading Ease score to distinguish structured journalism from low-quality spam.
- **Domain & Source Credibility Verifier**: 100+ cataloged authoritative news domains (Reuters, AP, BBC, Nature, WHO, etc.) vs flagged hoax/satire/unreliable domains with spoofing detection.
- **Fact-Check Query Generator**: Deep-links to Google Fact Check Tools, Snopes, and PolitiFact.

### 2. 🎨 Ultra-Modern Dashboard GUI
- **Dark Mode & Light Mode**: Instant dynamic theme toggle.
- **Circular Accuracy Gauge & Metric Progress Bars**: Visual probability indicators (Real %, Fake %, Sensationalism %, Emotional Bias %).
- **Interactive Pill Tags**: Highlights suspicious words and emotional triggers.
- **Multi-Tab Workspace**:
  1. 🔍 **Live AI Scanner**: Inspect articles, URLs, and claims with 1-click sample presets.
  2. 📊 **Scan History & Audit**: Session history table with filtering, search, and CSV export.
  3. 🧠 **Model & Dataset Studio**: Real-time vocabulary stats, diagnostic accuracy benchmark, and custom CSV dataset importer.
  4. 🌐 **Domain Credibility Checker**: Lookup editorial trust ratings for any news outlet.
  5. 📱 **Mobile & Backend API Guide**: Ready-to-use code snippets for Android (Java/Kotlin) and Spring Boot.

### 3. 📱 Future App Portability (Android & Spring Boot)
- **Zero Heavy Dependencies**: Pure Java with zero external native C++/Python requirements.
- **Headless Service API**: Call `NewsDetectionService.getInstance().detectNews(...)` anywhere.
- **JSON Serialization**: Call `result.toJson()` to send clean JSON payloads across REST APIs or mobile view models.

---

## 🚀 How to Run in Eclipse IDE

1. Open **Eclipse IDE**.
2. Right-click on the project in **Package Explorer** and press **Refresh (F5)**.
3. Open `src` -> `com.fakenews.detector` -> [`Main.java`](file:///e:/AI_Fake_news_detect/src/com/fakenews/detector/Main.java).
4. Right-click [`Main.java`](file:///e:/AI_Fake_news_detect/src/com/fakenews/detector/Main.java) -> **Run As** -> **Java Application**.

---

## 📱 How to Reuse in Android Studio

1. Copy the packages (`api`, `classifier`, `data`, `model`, `nlp`) into your Android project (`app/src/main/java/`).
2. In your Android Activity or ViewModel:
```java
NewsDetectionService service = NewsDetectionService.getInstance();
PredictionResult result = service.detectNews(title, content, url);

// Use in Android UI:
String verdict = result.getVerdict().getLabel();
double confidence = result.getConfidenceScore();
String jsonOutput = result.toJson();
```

---

## 📁 Project Architecture

```
AI_Fake_news_detect/
├── README.md
└── src/
    ├── module-info.java
    └── com/fakenews/detector/
        ├── Main.java                          (Launcher & CLI runner)
        ├── api/
        │   ├── NewsDetectionService.java      (Headless API for Android / Web)
        │   └── ReportExporter.java            (JSON & Forensic Text Reports)
        ├── model/
        │   ├── NewsArticle.java
        │   ├── PredictionResult.java
        │   ├── DomainReputation.java
        │   └── HistoryRecord.java
        ├── nlp/
        │   ├── TextPreprocessor.java
        │   ├── TFIDFVectorizer.java
        │   ├── SentimentAnalyzer.java
        │   ├── ReadabilityCalculator.java
        │   ├── StopWords.java
        │   └── PorterStemmer.java
        ├── classifier/
        │   ├── NaiveBayesClassifier.java
        │   ├── LinguisticAnalyzer.java
        │   ├── DomainCredibilityChecker.java
        │   └── FakeNewsDetector.java
        ├── data/
        │   ├── DefaultDataset.java
        │   ├── DatasetLoader.java
        │   └── HistoryManager.java
        └── gui/
            ├── FakeNewsDetectorGUI.java       (Dashboard UI)
            ├── ThemeManager.java              (Dark / Light theme)
            └── components/
                ├── RoundedPanel.java
                └── CircularGaugePanel.java
```
