
from fastapi import APIRouter
from app.services import ml_prediction_service

router = APIRouter()


@router.get("")
def check_health():
    try:
        ml_status = ml_prediction_service.get_model_status()
        ml_available = bool(ml_status.get("available", False))
        ml_message = (
            "Trained models loaded"
            if ml_available
            else "Trained models unavailable"
        )
    except Exception:
        ml_available = False
        ml_message = "ML status check failed"

    return {
        "status": "Operational",
        "service": "VeriNews AI FastAPI Backend",
        "mlEngine": {
            "status": "Available" if ml_available else "Unavailable",
            "available": ml_available,
            "message": ml_message,
        },
        "database": {
            "status": "Not verified",
            "message": "Database connectivity has not been checked by this endpoint",
        },
        "ocrEngine": {
            "status": "Not verified",
            "message": "OCR availability has not been checked by this endpoint",
        },
        "cloud": {
            "status": "Not verified",
            "message": "Container runtime has not been checked by this endpoint",
        },
    }
