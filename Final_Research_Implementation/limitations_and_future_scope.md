# Limitations & Future Scope — VeriNews AI 2.0

## 1. Limitations

### A. Surface Stylistic Representation vs Real-World Factuality
- **Lexical Proxy Limitation:** The traditional ML classifiers (Logistic Regression, Linear SVM, Random Forest) evaluate n-gram word choices, punctuation frequencies, and syntactic patterns. They **do not** possess world models or access real-time event truth.
- **Adversarial Synthesis:** A fabricated news claim crafted in the restrained, objective wire style of a traditional news agency will be classified as `REAL` by lexical models. Conversely, a factual blog post written with emotional or urgent phrasing may trigger clickbait warnings.
- **Epistemic Clarity:** High model agreement ($100\%$) indicates strong voting consensus across classifiers; it does not constitute philosophical or legal proof of truth.

### B. Dataset Artifacts and Domain Bias
- **Publisher Memorization:** Benchmark datasets like ISOT contain significant publisher markers (e.g. `Reuters`, `Associated Press`). While VeriNews AI 2.0's source-neutral regex pipeline removes known explicit wire markers, subtle editorial syntax may persist.
- **Subject Classification Shortcut:** In the ISOT dataset, the article category alone achieved 100% classification accuracy, proving that dataset curators partitioned categories along label boundaries.
- **Temporal Distribution Invariance:** News claims from 2026 onwards reference entities, conflicts, and technologies that did not exist during training (2016-2017).

### C. Multilingual and Regional Boundaries
- **English-Only Training:** The four trained classifiers were trained exclusively on English news text.
- **Transliteration Noise:** Hindi and Hinglish inputs are flagged with warnings by `language_service.py` to prevent users from relying on uncalibrated English model inferences.

---

## 2. Future Scope

### A. Real-Time Dynamic Knowledge Retrieval
- Connect the classification pipeline to live factual databases (Wikidata, Google Fact Check Tools API, ClaimReview schema) to cross-reference extracted entities and assertions against verified fact-check registries.

### B. Dense Contextual & Cross-Lingual Transformers
- Integrate multilingual Transformer checkpoints (XLM-RoBERTa, IndicBERT, mDeBERTa) capable of processing Hindi, Hinglish, Bengali, and Tamil news without script transliteration loss.

### C. Active Learning & Human-in-the-Loop Feedback
- Implement an active learning loop where disputed or low-confidence scans (`MODEL_DISAGREEMENT`) can be reviewed by domain experts and incorporated into incremental retraining batches.

### D. Multi-Modal Verification (Image & Metadata Forensics)
- Expand the screenshot analysis module to verify reverse image search results, EXIF metadata manipulation, and generative AI watermarks (C2PA standard).
