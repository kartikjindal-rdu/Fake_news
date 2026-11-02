"""
transformer_service.py
======================
Semantic NLP branch for the VeriNews AI 2.0 Hybrid Architecture.

Loads and evaluates a pretrained or fine-tuned Transformer encoder
(BERT / RoBERTa / DistilBERT) for text classification.

Features:
- Configurable model path and HuggingFace model identifier.
- Device auto-selection (CUDA if available, else CPU).
- Safe sequence truncation (max 512 tokens).
- Softmax probability calibration.
- Graceful fallback when PyTorch/Transformers are not installed or
  model weights are not found.
- Zero silent fabrication of model outputs.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# State
_transformer_loaded = False
_transformer_model = None
_transformer_tokenizer = None
_transformer_device = "cpu"
_transformer_error: Optional[str] = None
_model_source: Optional[str] = None

# Configuration defaults
DEFAULT_MODEL_ID = "mrm8488/bert-tiny-finetuned-fake-news-detection"
MAX_TOKEN_LENGTH = 512


def _resolve_transformer_path() -> Optional[Path]:
    """Find a local directory containing Transformer model weights and config."""
    env_path = os.environ.get("VERINEWS_TRANSFORMER_PATH", "").strip()
    if env_path:
        p = Path(env_path).expanduser()
        if p.is_dir() and (p / "config.json").is_file():
            return p

    # Standard candidate directories
    candidates = [
        Path(r"E:\AI_Fake_news_detect\backend\models\transformer"),
        Path(r"C:\Users\HP\OneDrive\Desktop\Model_train\models\transformer"),
        Path(__file__).resolve().parents[2] / "models" / "transformer",
    ]

    for c in candidates:
        if c.is_dir() and (c / "config.json").is_file():
            return c

    return None


def load_transformer_model() -> Dict[str, Any]:
    """
    Attempt to load the Transformer model and tokenizer.
    Returns status dictionary. Never raises uncaught exceptions.
    """
    global _transformer_loaded, _transformer_model, _transformer_tokenizer
    global _transformer_device, _transformer_error, _model_source

    if _transformer_loaded:
        return {
            "status": "already_loaded",
            "model_source": _model_source,
            "device": _transformer_device,
        }

    # Check if Transformer branch is enabled via environment
    enabled = os.environ.get("VERINEWS_ENABLE_TRANSFORMER", "true").strip().lower()
    if enabled in ("false", "0", "no", "off"):
        _transformer_error = "Transformer branch disabled by VERINEWS_ENABLE_TRANSFORMER=false"
        logger.info(_transformer_error)
        return {"status": "disabled", "detail": _transformer_error}

    # Check if required libraries are installed
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
    except ImportError as e:
        _transformer_error = (
            f"PyTorch or HuggingFace Transformers library not installed ({e}). "
            "Install with: pip install torch transformers"
        )
        logger.warning("Semantic Transformer branch unavailable: %s", _transformer_error)
        return {"status": "error", "detail": _transformer_error}

    # Select device
    device_override = os.environ.get("VERINEWS_TRANSFORMER_DEVICE", "").strip().lower()
    if device_override in ("cuda", "cpu"):
        _transformer_device = device_override
    else:
        _transformer_device = "cuda" if torch.cuda.is_available() else "cpu"

    # Check local path first
    local_path = _resolve_transformer_path()
    model_identifier = None

    if local_path:
        model_identifier = str(local_path)
        _model_source = f"local:{local_path.name}"
        logger.info("Found local Transformer checkpoint at %s", local_path)
    else:
        # Check configured Hugging Face model ID
        env_id = os.environ.get("VERINEWS_TRANSFORMER_MODEL_ID", "").strip()
        if env_id:
            model_identifier = env_id
            _model_source = f"hub:{env_id}"
        else:
            # Check if default local directory was expected
            expected_dir = Path(__file__).resolve().parents[2] / "models" / "transformer"
            _transformer_error = (
                f"No local Transformer checkpoint found at {expected_dir}. "
                "Fine-tune a model using train_hybrid.py or configure VERINEWS_TRANSFORMER_PATH / VERINEWS_TRANSFORMER_MODEL_ID."
            )
            logger.info("Semantic Transformer branch not loaded: %s", _transformer_error)
            return {"status": "missing_checkpoint", "detail": _transformer_error}

    try:
        logger.info("Loading Transformer model from %s on device %s...", model_identifier, _transformer_device)
        tokenizer = AutoTokenizer.from_pretrained(model_identifier, local_files_only=bool(local_path))
        model = AutoModelForSequenceClassification.from_pretrained(model_identifier, local_files_only=bool(local_path))
        
        model.to(_transformer_device)
        model.eval()

        _transformer_tokenizer = tokenizer
        _transformer_model = model
        _transformer_loaded = True
        _transformer_error = None

        logger.info("Semantic Transformer model loaded successfully (%s on %s)", _model_source, _transformer_device)
        return {
            "status": "loaded",
            "model_source": _model_source,
            "device": _transformer_device,
        }

    except Exception as e:
        _transformer_loaded = False
        _transformer_model = None
        _transformer_tokenizer = None
        _transformer_error = f"Failed to load Transformer model '{model_identifier}': {str(e)}"
        logger.warning(_transformer_error)
        return {"status": "error", "detail": _transformer_error}


def get_transformer_status() -> Dict[str, Any]:
    """Return status of the Transformer branch without initiating a load."""
    return {
        "available": _transformer_loaded,
        "device": _transformer_device if _transformer_loaded else None,
        "model_source": _model_source if _transformer_loaded else None,
        "error": _transformer_error if not _transformer_loaded else None,
    }


def predict_semantic(text: str) -> Dict[str, Any]:
    """
    Run semantic sequence classification through the Transformer encoder.

    Returns:
        dict containing:
            available: bool
            prediction: 'FAKE' | 'REAL' | None
            fake_prob: float (0.0 to 1.0)
            real_prob: float (0.0 to 1.0)
            confidence: float (0.0 to 100.0)
            latency_ms: float
            error: Optional[str]
    """
    if not _transformer_loaded:
        return {
            "available": False,
            "prediction": None,
            "fake_prob": None,
            "real_prob": None,
            "confidence": None,
            "error": _transformer_error or "Transformer model is not loaded.",
        }

    if not text or not isinstance(text, str) or not text.strip():
        return {
            "available": False,
            "prediction": None,
            "fake_prob": None,
            "real_prob": None,
            "confidence": None,
            "error": "Input text is empty or invalid.",
        }

    try:
        import torch

        t0 = time.time()
        # Tokenize with truncation to MAX_TOKEN_LENGTH (512 tokens)
        inputs = _transformer_tokenizer(
            text,
            max_length=MAX_TOKEN_LENGTH,
            truncation=True,
            padding=True,
            return_tensors="pt",
        )
        inputs = {k: v.to(_transformer_device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = _transformer_model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1).squeeze(0).cpu().numpy()

        latency_ms = round((time.time() - t0) * 1000.0, 2)

        # Determine class label mapping:
        # Standard: 0 = FAKE, 1 = REAL
        # Also inspect model id2label mapping if present
        id2label = getattr(_transformer_model.config, "id2label", None) or {}
        
        # Check if id2label indicates class index meanings
        fake_idx = 0
        real_idx = 1
        if isinstance(id2label, dict):
            for idx, label_name in id2label.items():
                lbl_upper = str(label_name).upper()
                if "FAKE" in lbl_upper or "FALSE" in lbl_upper or "HOAX" in lbl_upper:
                    fake_idx = int(idx)
                elif "REAL" in lbl_upper or "TRUE" in lbl_upper or "RELIABLE" in lbl_upper:
                    real_idx = int(idx)

        # Validate probability vector length
        if len(probs) >= 2:
            fake_prob = float(probs[fake_idx])
            real_prob = float(probs[real_idx])
            # Normalize in case probabilities are over >2 classes
            total_p = fake_prob + real_prob
            if total_p > 0:
                fake_prob = fake_prob / total_p
                real_prob = real_prob / total_p
        else:
            fake_prob = float(probs[0])
            real_prob = 1.0 - fake_prob

        prediction = "FAKE" if fake_prob >= 0.50 else "REAL"
        confidence = round(max(fake_prob, real_prob) * 100.0, 1)

        return {
            "available": True,
            "prediction": prediction,
            "fake_prob": round(fake_prob, 4),
            "real_prob": round(real_prob, 4),
            "confidence": confidence,
            "model_source": _model_source,
            "latency_ms": latency_ms,
            "error": None,
        }

    except Exception as e:
        logger.exception("Transformer prediction failed: %s", e)
        return {
            "available": False,
            "prediction": None,
            "fake_prob": None,
            "real_prob": None,
            "confidence": None,
            "error": f"Transformer inference error: {str(e)}",
        }
