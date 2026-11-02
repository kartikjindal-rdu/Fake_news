# A Systematic Evaluation of Lightweight Hybrid Ensemble Learning for Fake News Detection

**Authors:** VeriNews AI Research Initiative  
**Date:** October 2026  
**Artifact Repository:** `E:\AI_Fake_news_detect`  
**Model Package:** `backend/Model/final_verinews_model_package.pkl`

---

## 1. Abstract
The rapid propagation of digital misinformation presents severe risks to democratic processes, public health communication, and institutional trust. While large language models (LLMs) and deep contextual transformers have emerged as standard paradigms in computational linguistics, their extensive inference latency, resource demands, and susceptibility to hallucination constrain their utility in high-throughput, real-time edge environments. This paper presents a systematic evaluation of lightweight hybrid ensemble learning for fake news detection, integrating term frequency-inverse document frequency (TF-IDF) n-gram vectorization with a majority-voting ensemble of Logistic Regression, Linear Support Vector Machines (LinearSVC), and Random Forest classifiers, coupled with an independent semantic Transformer representation branch. Rigorous source-neutral evaluations on 8,933 held-out test articles demonstrate that the hybrid ensemble achieves 98.79% accuracy, 98.15% precision, 99.31% recall, and an F1-score of 98.73%, with only 108 total classification errors. Crucially, we conduct an exhaustive data leakage and source-bias audit revealing that traditional political news datasets encode pronounced publisher artifacts: classifier training solely on source markers yields 99.25% accuracy, and metadata subject tokens yield 100% classification accuracy. Removing explicit publisher tokens preserves 98.71% accuracy, confirming that stylistic and lexical markers carry substantive predictive signal beyond publisher identity. We emphasize that classifier voting percentages represent consensus scores rather than calibrated factual truth and establish guidelines for deploying hybrid misinformation intelligence platforms.

---

## 2. Keywords
Misinformation Detection, Fake News Classification, Ensemble Learning, Source Bias, Data Leakage Audit, Natural Language Processing, Linear SVM, Model Explainability.

---

## 3. Introduction
Misinformation and synthetic disinformation campaigns exploit sensationalism, emotional manipulation, and linguistic ambiguity to accelerate transmission across digital networks. Automated verification systems are urgently required to assist journalists, intelligence analysts, and end users in assessing textual credibility. 

However, existing automated solutions encounter two fundamental challenges:
1. **Computational Overhead:** Massive Transformer models (e.g., RoBERTa-large, DeBERTa-v3) require specialized GPU infrastructure, limiting their viability for cost-effective local deployment, edge computing, and real-time news stream filtering.
2. **Conflation of Surface Wire Patterns with Factual Truth:** Machine learning classifiers trained on text corpora often learn dataset-specific reporting conventions (e.g., news agency datelines, standard editorial syntax) rather than genuine indicators of veracity.

To address these challenges, we evaluate **VeriNews AI 2.0**, an open, source-neutral hybrid architecture combining lightweight n-gram linear and tree-based ensembles with deep contextual representations. We evaluate performance across held-out splits, quantify source leakage, and analyze failure modes under adversarial clickbait.

---

## 4. Problem Statement
Given an arbitrary natural language news article or claim consisting of a sequence of tokens $T = \{t_1, t_2, \dots, t_N\}$, the objective is to determine a binary classification label $Y \in \{0, 1\}$, where $0$ denotes fabricated/unreliable content (FAKE) and $1$ denotes verified reporting (REAL). The core challenge is to formulate a decision rule $f(T) \to \hat{Y}$ that maximizes generalization across unseen journalistic domains while minimizing reliance on explicit publisher attribution tokens that introduce dataset leakage.

---

## 5. Research Objectives
1. **Architectural Evaluation:** Design and validate a lightweight, multi-classifier ensemble that operates within strict sub-50ms inference budgets on commodity CPUs.
2. **Source Neutrality:** Systematically strip wire service identifiers, publisher datelines, and metadata markers to isolate pure stylistic, syntactic, and lexical markers.
3. **Integrity and Leakage Audit:** Empirically quantify the degree to which baseline classifiers exploit publisher identity and metadata leakage versus underlying textual characteristics.
4. **Principled Consensus Semantics:** Differentiate classifier voting agreement from calibrated factual probability, ensuring transparent uncertainty communication to end users.

---

## 6. Claim and Uniqueness of the Project
- **Dual-Branch Decoupled Hybrid:** Rather than forcing opaque probability blending between heterogeneous models, the VeriNews AI architecture decouples traditional lexical consensus from semantic Transformer representations, preserving transparent voting consensus while exposing independent semantic validation.
- **Source-Neutral Preprocessing Standard:** All feature extractors and classifiers utilize a unified regex normalization pipeline that excises high-leakage tokens (e.g., Reuters, AP, BBC, CNN, AFP, New York Times, Washington Post, formal datelines, and contact emails).
- **Honest Empirical Reporting:** Unlike commercial platforms that market statistical classifiers as "truth detectors," this work empirically documents dataset constraints, showing that metadata alone achieves 100% separation and that stylistic classification does not replace external evidence verification.

---

## 7. Dataset Description
The empirical evaluation was conducted using the ISOT Fake News Dataset (University of Victoria) alongside verified contemporary multi-publisher corpora:
- **Total Corpus Size:** 44,898 curated articles (23,481 FAKE samples, 21,417 REAL samples).
- **Evaluation Split:** An 80% training / 20% held-out test split was established via stratified group-aware sampling ($N_{\text{test}} = 8,933$ samples).
- **Exact Overlap Audit:** Following normalized deduplication, the exact text overlap between training and test sets is **0.00%**, preventing memorization leakage.
- **Class Balance in Test Split:** Approximately 52.3% FAKE ($N = 4,672$) and 47.7% REAL ($N = 4,261$).

---

## 8. Data Preprocessing
Text normalization applies the source-neutral cleaning pipeline:
$$\text{Clean}(T) = \text{WhitespaceNormalize}(\text{RegexFilter}(T))$$
Specific regex patterns eliminate:
1. Publisher names: `\breuters\b`, `\bassociated press\b`, `\bbbc\b`, `\bcnn\b`, `\bafp\b`, `\bnew york times\b`, `\bwashington post\b` (case-insensitive).
2. Wire datelines: `\b[A-Z][A-Z\s,.-]{2,40}\s*\([A-Z][a-zA-Z\s]+\)\s*[-:]\s*`.
3. Hyperlinks and protocols: `https?://\S+|www\.\S+`.
4. Electronic contact addresses: `\S+@\S+`.

The cleaned text is transformed into a 50,000-dimensional sparse feature space using sublinear TF-IDF term weighting:
$$\text{TF-IDF}(t, d, D) = (1 + \log(\text{TF}(t, d))) \times \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
n-gram boundaries span unigrams and bigrams ($1, 2$) with English stop-word filtering.

---

## 9. Methodology
Our methodology integrates four stages:
1. **Feature Engineering:** 50,000 top n-gram TF-IDF representations for linear models; top 5,000 feature subspace for the Random Forest classifier to constrain tree variance and prevent overfitting.
2. **Individual Classifier Training:**
   - **Logistic Regression:** Log-loss minimization with L2 regularization ($C = 1.0$, `max_iter = 1000`).
   - **Linear SVM (LinearSVC):** Squared hinge loss optimization with primal/dual coordinate descent.
   - **Random Forest:** Ensemble of 100 decorrelated decision trees evaluated across the 5,000 feature subspace.
3. **Ensemble Aggregation:** Hard-voting decision layer:
   $$\hat{Y}_{\text{ens}} = \mathbb{I}\left(\sum_{k=1}^K \mathbb{I}(\hat{y}_k = 1) \ge \left\lceil \frac{K+1}{2} \right\rceil\right)$$
4. **Semantic Transformer Integration:** An optional sequence classification head (fine-tuned DistilBERT / RoBERTa) provides deep contextual verification as an independent signal.

---

## 10. Proposed Architecture
```
                           [ Raw News Text / Claim ]
                                       │
                                       ▼
                     [ Source-Neutral Text Normalizer ]
                        (Strips Datelines, URLs, Wire)
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
      [ TF-IDF Vectorizer (50k) ]            [ Contextual Tokenizer ]
                    │                                     │
       ┌────────────┼────────────┐                        ▼
       ▼            ▼            ▼             [ Semantic Transformer ]
   [Linear LR]  [Linear SVC]  [Random Forest]     (Sequence Classifier)
    (50k dim)    (50k dim)     (5k dim slice)             │
       │            │            │                        │
       └────────────┼────────────┘                        │
                    ▼                                     │
        [ Hard Voting Consensus ]                         │
           (0%, 33%, 67%, 100%)                           │
                    │                                     │
                    ▼                                     ▼
        [ Consensus Score & Verdict ] ────────► [ Independent Dual Signal ]
                                                  (VeriNews AI 2.0 API)
```

---

## 11. Model Implementation
The production architecture is serialized in `final_verinews_model_package.pkl` and served via `final_model_service.py` within FastAPI. 

Key attributes:
- **`Logistic Regression`**: 50,000 coefficients mapped to vocabulary features for local linear explainability ($w_i \cdot x_i$).
- **`Linear SVM`**: Decision hyperplane margin optimization with signed distance thresholding.
- **`Random Forest`**: 100 tree estimators capped at 5,000 features, providing non-linear partitioning.
- **`Hybrid Ensemble`**: Scikit-Learn `VotingClassifier` consolidating predictions.

---

## 12. Experimental Setup and Environment
- **Platform:** Windows Server / Workstation (x86_64 architecture).
- **Environment:** Python 3.11 virtual environment (`backend/.venv`), Scikit-Learn, Joblib, NumPy, SciPy, FastAPI, PyTest.
- **Inference Budget:** Target CPU latency $< 25$ ms per document.
- **Testing Protocol:** Deterministic seeds (`random_state = 42`) across stratified splits; no overlapping documents between train and test splits.

---

## 13. Evaluation Metrics
Evaluations rely on standard classification performance metrics:
$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$
$$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}$$
$$F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
Consensus Agreement Rate among $K$ models:
$$A = \frac{\max(\text{Votes}_{\text{FAKE}}, \text{Votes}_{\text{REAL}})}{K} \times 100\%$$

---

## 14. Results and Comparative Analysis

### Verified Empirical Performance ($N = 8,933$ Held-Out Test Samples)

| Model Architecture | Accuracy | Precision | Recall | F1-Score | Total Errors |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Logistic Regression** | 98.68% | 98.15% | 99.08% | 98.61% | 118 |
| **Linear SVM (LinearSVC)** | **98.84%** | **98.31%** | 99.24% | **98.78%** | **104** |
| **Random Forest (5k features)** | 97.38% | 95.74% | 98.87% | 97.28% | 234 |
| **Hybrid Majority Ensemble** | 98.79% | 98.15% | **99.31%** | 98.73% | 108 |

### Confusion Matrix of Hybrid Ensemble ($N = 8,933$)
- **True Negatives (Correct FAKE):** 4,592
- **False Positives (FAKE predicted as REAL):** 80
- **False Negatives (REAL predicted as FAKE):** 28
- **True Positives (Correct REAL):** 4,233
- **Total Misclassifications:** 108 (1.21% error rate)

---

## 15. Data Leakage and Source Bias Analysis
A critical contribution of this research is quantifying dataset artifacts that inflate benchmark metrics:

1. **Subject Metadata Leakage:**
   - Training a classifier solely on article subject categories (e.g., `politicsNews` vs `News`) yielded **100.00% accuracy**. This demonstrates that dataset publishers often assign distinct categories to real and fake articles, creating catastrophic leakage if metadata is exposed.
2. **Publisher Wire Marker Leakage:**
   - Classifiers trained on text containing explicit publisher headers (e.g., `WASHINGTON (Reuters) -`) achieved **99.25% accuracy** using wire markers alone as a shortcut.
3. **Source-Neutral Filtering Impact:**
   - When all explicit publisher names and datelines are excised, accuracy stabilizes at **98.71% - 98.79%**. This demonstrates that while publisher markers were readily exploited, the residual lexical and stylistic choices (hedging, hyperbolic syntax, attribution structure) provide genuine discriminative signal.
4. **Temporal Partitioning Limitations:**
   - A temporal split could not be performed due to non-overlapping date ranges between real and fake subsets in the legacy ISOT corpus, highlighting the necessity for modern multi-source live feeds.

---

## 16. Discussion
1. **Linear SVM Superiority:** Linear SVM achieved the single highest accuracy (98.84%), highlighting the linearly separable nature of high-dimensional TF-IDF spaces (50,000 features).
2. **Random Forest Subspace Behavior:** Constraining Random Forest to 5,000 features reduced accuracy slightly (97.38%), but prevented severe memory exhaustion and tree overfitting.
3. **Consensus vs Probability:** Real-world testing revealed that users frequently misinterpret 66.7% or 100% ensemble voting agreement as a mathematical probability of truth. VeriNews AI 2.0 explicitly separates **model consensus** from **calibrated credibility**, preventing epistemic overconfidence.

---

## 17. Limitations
1. **Linguistic Scope:** Models are trained on English-language syntax; non-English and Hinglish inputs require dedicated cross-lingual representations.
2. **Context Blindness of Lexical Models:** N-gram models evaluate stylistic patterns, not real-time world events. A syntactically impeccable fake article written in Reuters style will be classified as REAL.
3. **Evolving Disinformation Tactics:** Modern generative AI tools can emulate formal journalistic tone, diminishing stylistic differences between verified reporting and synthetic propaganda.

---

## 18. Conclusion
This study systematically evaluated a lightweight, source-neutral hybrid ensemble for misinformation classification. By combining Logistic Regression, Linear SVM, and Random Forest classifiers with source-neutral normalization, the system achieves 98.79% test accuracy with 108 errors across 8,933 test samples. Our leakage audit exposes the profound vulnerability of benchmark datasets to publisher shortcuts. By establishing strict source neutrality, transparent consensus semantics, and decoupled semantic verification, VeriNews AI 2.0 delivers a robust, scientifically defensible platform for computational misinformation intelligence.

---

## 19. Future Scope
1. **Cross-Domain Transfer Benchmarking:** Evaluating zero-shot transfer against modern corpora (e.g., LIAR-Plus, MultiFC, COVID-19 misinformation).
2. **Dense Multilingual Embeddings:** Incorporating multilingual embeddings (XLM-RoBERTa, IndicBERT) for Hindi and regional news streams.
3. **Automated Fact-Checking Graph Integration:** Augmenting stylistic classification with real-time knowledge graph queries and claim retrieval APIs.

---

## 20. References
1. Ahmed, H., Traore, I., & Saad, S. (2017). Detection of online fake news using n-gram analysis and machine learning techniques. *Intelligent, Secure, and Dependable Systems in Distributed Infrastructure*, 127-138.
2. Shu, K., Sliva, A., Wang, S., Tang, J., & Liu, H. (2017). Fake news detection on social media: A data mining perspective. *ACM SIGKDD Explorations Newsletter*, 19(1), 22-36.
3. Wang, W. Y. (2017). "Liar, Liar Pants on Fire": A New Benchmark Dataset for Fake News Detection. *Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (ACL)*, 422-426.
4. Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. *Proceedings of NAACL-HLT*, 4171-4186.
5. Thorne, J., Vlachos, A., Christodoulopoulos, C., & Mittal, A. (2018). FEVER: a large-scale dataset for Fact Extraction and VERification. *Proceedings of NAACL-HLT*, 809-819.
6. Zellers, R., Holtzman, A., Rashkin, H., Bisk, Y., Farhadi, A., Roesner, F., & Choi, Y. (2019). Defending against neural fake news. *Advances in Neural Information Processing Systems (NeurIPS)*, 32.
7. Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *International Conference on Machine Learning (ICML)*, 1321-1330.
