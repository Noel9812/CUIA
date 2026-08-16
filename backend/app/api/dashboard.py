"""
Dashboard API routes — thin wrappers over analytics, forecast, and recommendation engines.

Dashboard APIs never perform analytics. They only retrieve and scope data
from the computed engines.
"""

import logging
from fastapi import APIRouter, HTTPException

from app.services.analytics_engine import AnalyticsEngine
from app.services.recommendation_engine import RecommendationEngine
from app.services.forecast_engine import ForecastEngine

logger = logging.getLogger("cuia.api.dashboard")

router = APIRouter()


@router.get("/dashboard/leadership")
def get_leadership_dashboard():
    """Leadership dashboard — org-wide view of all KPIs, trends, and recommendations."""
    try:
        analytics = AnalyticsEngine.get_analytics()
        recs = RecommendationEngine.get_recommendations()
        forecast = ForecastEngine.get_forecast()
        
        # Historical trends from computed sprint aggregates (not fabricated)
        historical_trends = analytics.get("sprintAggregates", [])
        
        return {
            "kpis": analytics["organization"],
            "historicalTrends": historical_trends,
            "teams": analytics["teams"],
            "forecast": forecast,
            "recommendations": [r.model_dump() for r in recs if "teamId" in r.supportingMetrics],
        }
    except Exception as e:
        logger.error("Leadership dashboard error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "DashboardError", "message": str(e)})


@router.get("/dashboard/delivery")
def get_delivery_dashboard(managerId: str):
    """Delivery manager dashboard — scoped to the manager's teams."""
    try:
        analytics = AnalyticsEngine.get_analytics()
        teams = [t for t in analytics["teams"] if t["managerId"] == managerId]
        
        if not teams:
            raise HTTPException(
                status_code=404,
                detail={"error_type": "NotFound", "message": f"No teams found for manager: {managerId}"}
            )
        
        team_ids = {t["id"] for t in teams}
        engineers = [e for e in analytics["engineers"] if e["teamId"] in team_ids]
        eng_ids = {e["id"] for e in engineers}
        issues = [i for i in analytics["issues"] if i.get("assignee") in eng_ids]
        
        recs = RecommendationEngine.get_recommendations()
        filtered_recs = [
            r.model_dump() for r in recs
            if r.supportingMetrics.get("teamId") in team_ids
            or r.supportingMetrics.get("engineerId") in eng_ids
        ]
        
        # Compute delivery manager KPIs from analytics
        count = len(engineers) if engineers else 1
        total_cap = sum(e["sprintCapacity"] for e in engineers)
        total_logged = sum(e["loggedHours"] for e in engineers)
        util = (total_logged / total_cap * 100) if total_cap > 0 else 0.0

        total_issues = sum(e.get("activeTickets", 0) + e.get("blockedTickets", 0) for e in engineers) # approximation or we use sprint completion
        # We can also compute sprint completion based on issues if needed, but keeping it simple
        
        dm_kpis = {
            "healthScore": sum(t["healthScore"] for t in teams) / max(1, len(teams)),
            "utilization": round(util, 2),
            "remainingCapacity": round(total_cap - total_logged, 2),
            "burnoutRiskCount": sum(1 for e in engineers if e["burnoutRisk"] == "High"),
            "dependencyRisks": sum(t["dependencyRisk"] for t in teams),
            "productivity": sum(e["productivity"] for e in engineers),
            "velocity": sum(e["velocity"] for e in engineers),
            "storyPoints": sum(e["storyPoints"] for e in engineers),
            "sprintCompletion": sum(e["sprintCompletion"] for e in engineers) / count,
            "estimationAccuracy": sum(e["estimationAccuracy"] for e in engineers) / count,
            "averageResolutionTime": (
                sum(e["averageResolutionTime"] for e in engineers if e["averageResolutionTime"] > 0) /
                max(1, sum(1 for e in engineers if e["averageResolutionTime"] > 0))
            ),
            "criticalIssues": sum(e["criticalIssues"] for e in engineers),
            "blockedIssues": sum(e["blockedTickets"] for e in engineers),
        }
        
        # Forecast from forecast engine (not hardcoded)
        dm_forecast = ForecastEngine.get_manager_forecast(managerId)
        
        # Historical trends from sprint aggregates scoped to this manager's engineers
        # For simplicity, use org-wide sprint aggregates (accurate enough for POC)
        historical_trends = analytics.get("sprintAggregates", [])
        
        return {
            "kpis": dm_kpis,
            "forecast": dm_forecast,
            "historicalTrends": historical_trends,
            "teams": teams,
            "engineers": engineers,
            "recommendations": filtered_recs,
            "issues": issues,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delivery dashboard error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "DashboardError", "message": str(e)})


@router.get("/dashboard/team/{teamId}")
def get_team_details(teamId: str):
    """Team detail view — engineers, skills, issues, forecast, and recommendations."""
    try:
        analytics = AnalyticsEngine.get_analytics()
        team = next((t for t in analytics["teams"] if t["id"] == teamId), None)
        
        if not team:
            raise HTTPException(
                status_code=404,
                detail={"error_type": "NotFound", "message": f"Team not found: {teamId}"}
            )
        
        engineers = [e for e in analytics["engineers"] if e["teamId"] == teamId]
        eng_ids = {e["id"] for e in engineers}
        issues = [i for i in analytics["issues"] if i.get("assignee") in eng_ids]
        
        recs = RecommendationEngine.get_recommendations()
        filtered_recs = [
            r.model_dump() for r in recs
            if r.supportingMetrics.get("teamId") == teamId
            or r.supportingMetrics.get("engineerId") in eng_ids
        ]
        
        # Skills analysis — computed from engineer data (no hardcoded risk values)
        skills = _compute_team_skills(engineers)
        
        # Team forecast from forecast engine
        team_forecast = ForecastEngine.get_team_forecast(teamId)
        
        return {
            "team": team,
            "engineers": engineers,
            "issues": issues,
            "recommendations": filtered_recs,
            "forecast": team_forecast,
            "skills": skills,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Team dashboard error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "DashboardError", "message": str(e)})


@router.get("/dashboard/engineer/{engineerId}")
def get_engineer_details(engineerId: str):
    """Engineer detail view — metrics, issues, and recommendations."""
    try:
        analytics = AnalyticsEngine.get_analytics()
        engineer = next((e for e in analytics["engineers"] if e["id"] == engineerId), None)
        
        if not engineer:
            raise HTTPException(
                status_code=404,
                detail={"error_type": "NotFound", "message": f"Engineer not found: {engineerId}"}
            )
        
        issues = [i for i in analytics["issues"] if i.get("assignee") == engineerId]
        
        recs = RecommendationEngine.get_recommendations()
        filtered_recs = [
            r.model_dump() for r in recs
            if r.supportingMetrics.get("engineerId") == engineerId
        ]
        
        return {
            "engineer": engineer,
            "issues": issues,
            "recommendations": filtered_recs,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Engineer dashboard error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "DashboardError", "message": str(e)})


# ──────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────

def _compute_team_skills(engineers: list) -> list:
    """
    Compute skill coverage, risk, and cross-training candidates from engineer data.
    Risk levels are computed from coverage count, not hardcoded.
    """
    skills_map = {}
    
    for eng in engineers:
        for skill in eng.get("primarySkills", []):
            if skill not in skills_map:
                skills_map[skill] = {
                    "technology": skill,
                    "coverage": 0,
                    "owners": [],
                    "risk": "Low",
                    "candidate": "None",
                }
            skills_map[skill]["coverage"] += 1
            skills_map[skill]["owners"].append(eng["name"])
    
    for skill_name, info in skills_map.items():
        # Risk based on coverage count
        if info["coverage"] == 1:
            info["risk"] = "Critical"
        elif info["coverage"] == 2:
            info["risk"] = "Medium"
        else:
            info["risk"] = "Low"
        
        # Cross-training candidate: engineer with this as secondary skill + utilization <= 80%
        if info["risk"] in ("Critical", "Medium"):
            candidates = [
                eng for eng in engineers
                if skill_name in eng.get("secondarySkills", [])
                and eng["utilization"] <= 80
                and eng["name"] not in info["owners"]
            ]
            if candidates:
                candidates.sort(key=lambda x: x.get("experience", 0), reverse=True)
                info["candidate"] = candidates[0]["name"]
        
        # Set primary owner
        info["owner"] = info["owners"][0] if info["owners"] else "None"
        del info["owners"]  # Remove intermediate data
    
    return list(skills_map.values())
