"""Analytics API routes."""

import logging
from fastapi import APIRouter, HTTPException

from app.services.analytics_engine import AnalyticsEngine

logger = logging.getLogger("cuia.api.analytics")

router = APIRouter()


@router.get("/analytics")
def get_analytics():
    """Return full computed analytics."""
    try:
        return AnalyticsEngine.get_analytics()
    except Exception as e:
        logger.error("Analytics error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "AnalyticsError", "message": str(e)})


@router.post("/analytics/refresh")
def refresh_analytics():
    """Force recomputation of analytics from the dataset."""
    try:
        analytics = AnalyticsEngine.get_analytics(force_refresh=True)
        return {"status": "refreshed", "engineers": len(analytics.get("engineers", [])), "teams": len(analytics.get("teams", []))}
    except Exception as e:
        logger.error("Analytics refresh error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "AnalyticsError", "message": str(e)})
