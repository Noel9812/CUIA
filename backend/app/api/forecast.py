"""Forecast API routes."""

import logging
from fastapi import APIRouter, HTTPException

from app.services.forecast_engine import ForecastEngine

logger = logging.getLogger("cuia.api.forecast")

router = APIRouter()


@router.get("/forecast")
def get_org_forecast():
    """Get organization-wide forecast."""
    try:
        return ForecastEngine.get_forecast()
    except Exception as e:
        logger.error("Forecast error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "ForecastError", "message": str(e)})


@router.get("/forecast/team/{teamId}")
def get_team_forecast(teamId: str):
    """Get forecast for a specific team."""
    try:
        result = ForecastEngine.get_team_forecast(teamId)
        if "error" in result:
            raise HTTPException(status_code=404, detail={"error_type": "NotFound", "message": result["error"]})
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Team forecast error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "ForecastError", "message": str(e)})


@router.get("/forecast/manager/{managerId}")
def get_manager_forecast(managerId: str):
    """Get forecast for a delivery manager's teams."""
    try:
        result = ForecastEngine.get_manager_forecast(managerId)
        if "error" in result:
            raise HTTPException(status_code=404, detail={"error_type": "NotFound", "message": result["error"]})
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Manager forecast error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "ForecastError", "message": str(e)})
