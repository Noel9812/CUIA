"""Recommendations API routes."""

import logging
from fastapi import APIRouter, HTTPException

from app.services.recommendation_engine import RecommendationEngine

logger = logging.getLogger("cuia.api.recommendations")

router = APIRouter()


@router.get("/recommendations")
def get_recommendations():
    """Return all generated recommendations."""
    try:
        recs = RecommendationEngine.get_recommendations()
        return [r.model_dump() for r in recs]
    except Exception as e:
        logger.error("Recommendations error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "RecommendationError", "message": str(e)})
