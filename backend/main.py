
# Load .env before any module reads os.environ (must be first).
from dotenv import load_dotenv
load_dotenv()

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analyze, scans, model_info, health, auth, news, claims, export
from app.services import ml_prediction_service


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load existing trained models when the backend starts.

    If model loading fails, keep the API available so that
    non-ML endpoints can still operate.
    """
    try:
        result = ml_prediction_service.load_models()

        if result.get("status") in ("loaded", "already_loaded"):
            logger.info(
                "ML models are available. Feature count: %s",
                result.get("feature_count", "already loaded"),
            )
        else:
            logger.warning(
                "ML models are unavailable: %s",
                result.get("detail", "Unknown loading error"),
            )

    except Exception:
        logger.exception(
            "Unexpected error while loading ML models. "
            "The API will attempt to remain available."
        )

    yield

    logger.info("VeriNews AI 2.0 backend is shutting down.")


app = FastAPI(
    title="VeriNews AI 2.0 — Misinformation Intelligence API",
    description=(
        "Misinformation analysis using trained ML classifiers, "
        "linguistic heuristics, explainability, evidence retrieval, "
        "and language detection. Model predictions and heuristic "
        "scores do not independently verify factual accuracy."
    ),
    version="2.0.0",
    lifespan=lifespan,
)


# CORS configuration
# For production, replace "*" with the actual frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API routers
app.include_router(
    analyze.router,
    prefix="/api/analyze",
    tags=["Analysis"],
)

app.include_router(
    scans.router,
    prefix="/api/scans",
    tags=["Scans & History"],
)

app.include_router(
    model_info.router,
    prefix="/api/model",
    tags=["ML Studio"],
)

app.include_router(
    health.router,
    prefix="/api/health",
    tags=["Health"],
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Auth"],
)

app.include_router(
    news.router,
    prefix="/api/news",
    tags=["Live News Feed"],
)

app.include_router(
    claims.router,
    prefix="/api/claims",
    tags=["Claim Intelligence"],
)

app.include_router(
    export.router,
    prefix="/api/export",
    tags=["Report Export"],
)


@app.get("/")
def root():
    ml_status = ml_prediction_service.get_model_status()

    return {
        "service": "VeriNews AI 2.0 Enterprise Backend",
        "status": "Operational",
        "version": "2.0.0",
        "ml_models_available": ml_status["available"],
        "ml_model_error": ml_status.get("error"),
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
