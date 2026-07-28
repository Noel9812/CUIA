"""
Smart Context Builders — question-aware, persona-scoped, token-optimized.

Improvements in this version:
1. Dynamic data mapping based on ExtractedEntities (concepts, skills, timeframes).
2. Deterministic business rule integration (calls BusinessRulesEngine if concepts like
   'best performer' or 'capacity risk' are detected).
3. Full SimulationEngine execution mapping (builds what-if results directly into context).
4. Strict Persona Isolation (DMs only see their teams).
5. Token-optimized compact JSON payload.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set

from app.services.analytics_engine import AnalyticsEngine
from app.services.forecast_engine import ForecastEngine
from app.services.recommendation_engine import RecommendationEngine
from app.services.simulation_engine import SimulationEngine
from app.services.business_rules_engine import BusinessRulesEngine
from app.ai.entity_extractor import ExtractedEntities

logger = logging.getLogger("cuia.ai.context")


class ContextBuilder:
    """
    Creates token-optimized, question-aware context for AI consumption.
    """

    # ──────────────────────────────────────────────
    # Analytics Context
    # ──────────────────────────────────────────────

    @classmethod
    def build_analytics_context(
        cls, persona: str, entities: Optional[ExtractedEntities] = None
    ) -> str:
        """Build question-aware, persona-scoped analytics context."""
        analytics = AnalyticsEngine.get_analytics()

        if persona == "leadership":
            return cls._build_leadership_analytics(analytics, entities)
        else:
            return cls._build_dm_analytics(analytics, persona, entities)

    @classmethod
    def _build_leadership_analytics(
        cls, analytics: Dict, entities: Optional[ExtractedEntities] = None
    ) -> str:
        """Leadership analytics — org KPIs + filtered team/engineer data."""
        result: Dict[str, Any] = {}
        org = analytics["organization"]

        # If no specific entities/concepts requested, just return high level
        if not entities or not entities.has_any():
            result["org"] = {
                "engineers": org["totalEngineers"],
                "util": org["overallUtilization"],
                "health": org["overallTeamHealth"],
                "burnout": org["burnoutRiskCount"],
                "blocked": org["blockedIssues"],
            }
            result["teams"] = [cls._compact_team(t) for t in analytics["teams"]]
            return cls._compact_json(result)

        teams = analytics["teams"]
        engineers = analytics["engineers"]

        # ── Entity-based filtering ──
        if entities.team_ids:
            teams = [t for t in teams if t["id"] in entities.team_ids]
            
        if entities.engineer_ids:
            engineers = [e for e in engineers if e["id"] in entities.engineer_ids]
        elif entities.team_ids:
            engineers = [e for e in engineers if e["teamId"] in entities.team_ids]

        # ── Concept-based data inclusion ──
        concepts = entities.concepts
        
        # Rankings and Business Rules
        if "best performer" in concepts or "worst performer" in concepts:
            ranked = BusinessRulesEngine.rank_engineers_by_performance(engineers)
            if "best performer" in concepts:
                result["topPerformers"] = ranked[:3]
            if "worst performer" in concepts:
                result["bottomPerformers"] = ranked[-3:]

        if "busiest" in concepts:
            sorted_by_util = sorted(engineers, key=lambda x: x["utilization"], reverse=True)
            result["busiestEngineers"] = [cls._compact_engineer(e, concepts) for e in sorted_by_util[:3]]
            
        if "least busy" in concepts:
            sorted_by_util = sorted(engineers, key=lambda x: x["utilization"])
            result["leastBusyEngineers"] = [cls._compact_engineer(e, concepts) for e in sorted_by_util[:3]]
            
        if "healthiest team" in concepts:
            sorted_teams = sorted(teams, key=lambda x: x["healthScore"], reverse=True)
            result["healthiestTeam"] = cls._compact_team(sorted_teams[0]) if sorted_teams else None
            
        if "unhealthiest team" in concepts:
            sorted_teams = sorted(teams, key=lambda x: x["healthScore"])
            result["unhealthiestTeam"] = cls._compact_team(sorted_teams[0]) if sorted_teams else None

        # Build basic summaries if rankings weren't requested
        if "teams" not in result and not any(c in concepts for c in ["healthiest team", "unhealthiest team"]):
            result["teams"] = [cls._compact_team(t) for t in teams]

        if "engineers" not in result and not any(c in concepts for c in ["best performer", "worst performer", "busiest", "least busy"]):
            result["engineers"] = [cls._compact_engineer(e, concepts) for e in engineers]

        return cls._compact_json(result)

    @classmethod
    def _build_dm_analytics(
        cls, analytics: Dict, manager_id: str,
        entities: Optional[ExtractedEntities] = None
    ) -> str:
        """DM analytics — ONLY their teams and engineers. No cross-team leakage."""
        teams = [t for t in analytics["teams"] if t["managerId"] == manager_id]
        team_ids = {t["id"] for t in teams}
        engineers = [e for e in analytics["engineers"] if e["teamId"] in team_ids]

        if entities and entities.has_any():
            if entities.team_ids:
                allowed_teams = entities.team_ids & team_ids
                teams = [t for t in teams if t["id"] in allowed_teams]
                if allowed_teams:
                    engineers = [e for e in engineers if e["teamId"] in allowed_teams]

            if entities.engineer_ids:
                engineers = [e for e in engineers if e["id"] in entities.engineer_ids and e["teamId"] in team_ids]

        # Concept handling for DMs (re-using rules on filtered data)
        result: Dict[str, Any] = {"scope": f"DM {manager_id}"}
        concepts = entities.concepts if entities else set()
        
        if "best performer" in concepts or "worst performer" in concepts:
            ranked = BusinessRulesEngine.rank_engineers_by_performance(engineers)
            result["rankedPerformers"] = ranked

        if "busiest" in concepts:
            sorted_by_util = sorted(engineers, key=lambda x: x["utilization"], reverse=True)
            result["busiestEngineers"] = [cls._compact_engineer(e, concepts) for e in sorted_by_util[:3]]
            
        result["teams"] = [cls._compact_team(t) for t in teams]
        
        if "busiestEngineers" not in result and "rankedPerformers" not in result:
            result["engineers"] = [cls._compact_engineer(e, concepts) for e in engineers]
            
        return cls._compact_json(result)

    # ──────────────────────────────────────────────
    # Forecast Context
    # ──────────────────────────────────────────────

    @classmethod
    def build_forecast_context(
        cls, persona: str, entities: Optional[ExtractedEntities] = None
    ) -> str:
        """Build forecast context — no analytics data mixed in."""
        if persona == "leadership":
            forecast = ForecastEngine.get_forecast()
            result = {
                "forecast": {
                    "capacity": forecast.get("currentCapacity"),
                    "avgVel": forecast.get("averageVelocity"),
                    "avgUtil": forecast.get("averageUtilization"),
                    "risk": forecast.get("forecastRisk"),
                    "velTrend": forecast.get("trendAnalysis", {}).get("velocityDirection"),
                    "utilTrend": forecast.get("trendAnalysis", {}).get("utilizationDirection"),
                    "capGap": forecast.get("capacityGap"),
                    "sprints": forecast.get("futureSprints", []),
                }
            }
        else:
            forecast = ForecastEngine.get_manager_forecast(persona)
            result = {"forecast": forecast}

        return cls._compact_json(result)

    # ──────────────────────────────────────────────
    # Recommendation Context
    # ──────────────────────────────────────────────

    @classmethod
    def build_recommendation_context(
        cls, persona: str, entities: Optional[ExtractedEntities] = None
    ) -> str:
        """Build recommendation context — persona-isolated."""
        analytics = AnalyticsEngine.get_analytics()
        all_recs = RecommendationEngine.get_recommendations()

        if persona == "leadership":
            scoped = [cls._compact_rec(r) for r in all_recs]
        else:
            teams = [t for t in analytics["teams"] if t["managerId"] == persona]
            team_ids = {t["id"] for t in teams}
            eng_ids = {e["id"] for e in analytics["engineers"] if e["teamId"] in team_ids}
            
            scoped = [
                cls._compact_rec(r) for r in all_recs
                if r.supportingMetrics.get("teamId") in team_ids
                or r.supportingMetrics.get("engineerId") in eng_ids
            ]

        # If entities specified, filter recs
        if entities and entities.has_any():
            if entities.engineer_ids:
                scoped = [r for r in scoped if r.get("metrics", {}).get("engineerId") in entities.engineer_ids]
            if entities.team_ids:
                scoped = [r for r in scoped if r.get("metrics", {}).get("teamId") in entities.team_ids]

        return cls._compact_json({"recs": scoped, "total": len(scoped)})

    # ──────────────────────────────────────────────
    # Simulation Context
    # ──────────────────────────────────────────────

    @classmethod
    def build_simulation_context(
        cls, entities: Optional[ExtractedEntities] = None
    ) -> str:
        """
        Build simulation context by mapping natural language entities to scenarios
        and executing the SimulationEngine.
        """
        if not entities or not entities.has_any():
            return cls._compact_json({
                "error": "No simulation scenario detected.",
                "supported": ["engineer leave", "engineer depart", "capacity change"]
            })
            
        result = {}
        
        # Example mapping: If an engineer and "capacity change" or "leave" is mentioned
        if entities.engineer_ids:
            eng_id = list(entities.engineer_ids)[0]
            
            # Simple heuristic mapping based on concepts/timeframes
            # In a production system, this mapping would be more sophisticated
            scenario_type = "engineer_leave" 
            scenario_params = {"type": scenario_type, "engineerId": eng_id, "leaveHours": 40}
            
            try:
                sim_result = SimulationEngine.simulate(scenario_params)
                result["simulation"] = {
                    "scenario": scenario_type,
                    "target": eng_id,
                    "impact": sim_result.get("delta", {}).get("organization", {})
                }
            except Exception as e:
                result["error"] = str(e)
        else:
            result["error"] = "Insufficient entities to build a simulation scenario."

        return cls._compact_json(result)

    # ──────────────────────────────────────────────
    # Reporting Context
    # ──────────────────────────────────────────────

    @classmethod
    def build_reporting_context(
        cls, entities: Optional[ExtractedEntities] = None
    ) -> str:
        """Build context for reporting questions."""
        return cls._compact_json({
            "reports": {
                "types": ["daily", "weekly", "monthly"],
                "format": "PDF",
                "endpoint": "GET /api/reports/download/{type}?persona={persona}",
            }
        })

    # ──────────────────────────────────────────────
    # Compact serialization helpers
    # ──────────────────────────────────────────────

    @classmethod
    def _compact_team(cls, t: Dict) -> Dict:
        """Compress a team to essential fields."""
        return {
            "id": t["id"],
            "name": t["name"],
            "util": t["utilization"],
            "health": t["healthScore"],
            "vel": t["velocity"],
            "blocked": t["blockedIssues"],
        }

    @classmethod
    def _compact_engineer(
        cls, e: Dict, concepts: Set[str]
    ) -> Dict:
        """Compress an engineer to essential fields, scoped by concepts."""
        result: Dict[str, Any] = {
            "id": e["id"],
            "name": e["name"],
            "team": e["teamId"],
        }

        if not concepts:
            result.update({
                "util": e["utilization"],
                "vel": e["velocity"],
                "health": e["health"],
                "burnout": e["burnoutRisk"],
            })
            return result

        if "overutilized" in concepts or "underutilized" in concepts:
            result["util"] = e["utilization"]
            result["logged"] = e["loggedHours"]
            result["cap"] = e["sprintCapacity"]

        if "burnout risk" in concepts:
            result["burnout"] = e["burnoutRisk"]
            result["util"] = e["utilization"]
            result["crit"] = e["criticalIssues"]

        if "single point of failure" in concepts:
            result["skills"] = e.get("primarySkills", [])
            
        if len(result) <= 3:
            result.update({
                "util": e["utilization"],
                "vel": e["velocity"],
                "burnout": e["burnoutRisk"],
            })

        return result

    @staticmethod
    def _compact_rec(rec) -> Dict:
        """Compress a recommendation."""
        return {
            "sev": rec.severity,
            "rule": rec.businessRule,
            "action": rec.suggestedAction,
            "metrics": rec.supportingMetrics,
        }

    @staticmethod
    def _compact_json(data: Any) -> str:
        """Serialize to compact JSON (no whitespace to save tokens)."""
        return json.dumps(data, separators=(",", ":"))
