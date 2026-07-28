"""Simulation API routes."""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from app.services.simulation_engine import SimulationEngine

logger = logging.getLogger("cuia.api.simulation")

router = APIRouter()


class SimulationRequest(BaseModel):
    """Request body for running a what-if simulation."""
    type: str
    engineerId: Optional[str] = None
    leaveHours: Optional[float] = None
    newCapacity: Optional[float] = None
    engineer: Optional[Dict[str, Any]] = None
    issues: Optional[List[Dict[str, Any]]] = None
    issueKeys: Optional[List[str]] = None
    fromEngineerId: Optional[str] = None
    toEngineerId: Optional[str] = None
    newTeamId: Optional[str] = None


@router.post("/simulation")
def run_simulation(request: SimulationRequest):
    """
    Run a what-if simulation.
    
    Supported types:
    - engineer_leave
    - engineer_join
    - engineer_depart
    - capacity_change
    - add_issues
    - remove_issues
    - redistribute_work
    - team_restructure
    """
    try:
        scenario = request.model_dump(exclude_none=True)
        result = SimulationEngine.simulate(scenario)
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail={"error_type": "SimulationError", "message": result["error"]}
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Simulation error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={"error_type": "SimulationError", "message": str(e)}
        )
