"""API route definitions."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import ClassificationResponse, HealthResponse, TicketRequest
from app.services.classifier import ModelNotTrainedError, classify_ticket

router = APIRouter()


@router.post("/classify", response_model=ClassificationResponse, tags=["Tickets"])
def classify(ticket: TicketRequest):
    """Classify a support ticket into a category and priority level."""
    try:
        full_text = f"{ticket.subject}. {ticket.text}" if ticket.subject else ticket.text
        result = classify_ticket(full_text)
        return result
    except ModelNotTrainedError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Classification failed: {e}")


@router.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Basic health check, also reports whether trained models are present."""
    try:
        classify_ticket("health check probe")
        models_loaded = True
    except Exception:
        models_loaded = False
    return {"status": "ok", "models_loaded": models_loaded}
