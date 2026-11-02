# VeriNews AI 2.0 — Model Architecture Diagram

This document illustrates the end-to-end architecture of the VeriNews AI 2.0 source-neutral hybrid prediction and verification pipeline.

---

## 1. Complete System Architecture

```mermaid
flowchart TD
    User["User News Submission (Text / Headline / Claim)"] --> Clean["Source-Neutral Normalizer (_source_neutral_clean)"]
    
    subgraph Preprocessing ["Stage 1: Source-Neutral Sanitation"]
        Clean --> R1["Strip Wire Publishers (Reuters, AP, BBC, CNN, AFP, NYT, WaPo)"]
        R1 --> R2["Strip Standard Datelines & Geographical Markers"]
        R2 --> R3["Strip URLs & Email Identifiers"]
        R3 --> CleanedText["Sanitized Text Stream"]
    end

    CleanedText --> BranchA["Branch A: Source-Neutral Traditional ML"]
    CleanedText --> BranchB["Branch B: Semantic Transformer (Optional)"]

    subgraph BranchA_Flow ["Branch A: Traditional Feature Space (50k TF-IDF)"]
        BranchA --> TFIDF["TF-IDF Vectorizer (50,000 max features, unigrams+bigrams)"]
        TFIDF --> LR["Logistic Regression (Full 50k Features)"]
        TFIDF --> SVM["Linear SVM (Full 50k Features)"]
        TFIDF --> RF["Random Forest (Top 5k Feature Slice)"]
        
        LR --> VoteLR["LR Vote (FAKE/REAL)"]
        SVM --> VoteSVM["SVM Vote (FAKE/REAL)"]
        RF --> VoteRF["RF Vote (FAKE/REAL)"]

        VoteLR --> HardVote["Hard Voting Consensus Layer"]
        VoteSVM --> HardVote
        VoteRF --> HardVote

        HardVote --> TradConsensus["Consensus Probability (0%, 33%, 67%, 100%)"]
        HardVote --> TradVerdict["Traditional Ensemble Verdict"]
    end

    subgraph BranchB_Flow ["Branch B: Semantic Transformer"]
        BranchB --> Tok["Transformer Tokenizer (512 tokens max)"]
        Tok --> BERT["BERT / RoBERTa Sequence Classifier"]
        BERT --> TransVote["Transformer Vote & Probability"]
    end

    subgraph Decision_Synthesis ["Stage 3: Decision Synthesis Layer"]
        TradConsensus --> Synthesis["Orchestrator (hybrid_ensemble_service)"]
        TradVerdict --> Synthesis
        TransVote -.->|Independent Signal| Synthesis

        Synthesis --> CheckFallback{"Is Transformer Available?"}
        CheckFallback -- "No (Offline)" --> FallbackOutput["Fallback Mode: Source-Neutral 3-Model Ensemble"]
        CheckFallback -- "Yes (Online)" --> HybridOutput["Hybrid Mode: 4-Classifier Agreement + Independent Transformer Signal"]
    end

    subgraph API_Output ["Stage 4: API Response & Explainability"]
        FallbackOutput --> FinalResponse["API Response (/api/analyze/text)"]
        HybridOutput --> FinalResponse
        CleanedText --> Explain["Linear Explainability (Coefficients x TF-IDF)"]
        Explain --> FinalResponse
    end
```

---

## 2. Decision Logic and Consensus States

```mermaid
stateDiagram-v2
    [*] --> IngestText
    IngestText --> SourceNeutralPreprocessing
    SourceNeutralPreprocessing --> TFIDF_Extraction
    
    state "Voting Consensus Evaluation" as Voting {
        TFIDF_Extraction --> ComputeVotes
        ComputeVotes --> ThreeZeroAgreement: 3-0 Unanimous
        ComputeVotes --> TwoOneAgreement: 2-1 Majority
    }

    ThreeZeroAgreement --> ConsensusState: MODEL_CONSENSUS (100% Agreement)
    TwoOneAgreement --> DisagreementState: MODEL_DISAGREEMENT (66.7% Agreement)

    state "Dual Signal Aggregation" as DualSignal {
        ConsensusState --> CheckTransformer
        DisagreementState --> CheckTransformer
        CheckTransformer --> FallbackMode: Transformer Offline
        CheckTransformer --> IndependentSignal: Transformer Online
    }

    FallbackMode --> EmitAPI
    IndependentSignal --> EmitAPI
    EmitAPI --> [*]
```

---

## 3. Explainability Pipeline

```mermaid
flowchart LR
    Cleaned["Cleaned Text"] --> TFIDF_Transform["TF-IDF Vector Transform"]
    TFIDF_Transform --> NonZero["Extract Non-Zero Features"]
    NonZero --> Multiply["Multiply: TF-IDF Value x LogReg Learned Coef"]
    Multiply --> Rank["Rank Absolute Magnitudes (Top 10)"]
    Rank --> ClassifyDirection["Assign Direction (FAKE if Coef < 0, REAL if Coef > 0)"]
    ClassifyDirection --> OutputJSON["Expose to UI (/api/analyze/text)"]
```
