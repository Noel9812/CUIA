"""
Forecast Engine — deterministic forecasting for the CUIA platform.

Uses historical sprint data to project future utilization, capacity,
velocity, delivery risk, and resource demand. All computations are
deterministic — no AI, no ML, just trend analysis and extrapolation.
"""

import logging
from typing import Dict, Any, List, Optional

from app.services.analytics_engine import AnalyticsEngine
from app.core.config_loader import ConfigLoader

logger = logging.getLogger("cuia.forecast")


class ForecastEngine:
    """
    Deterministic forecast engine.
    
    Computes forward-looking projections from historical sprint aggregates.
    AI only explains results — it never generates forecasts.
    """

    _forecast: Optional[Dict[str, Any]] = None

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    @classmethod
    def get_forecast(cls, force_refresh: bool = False) -> Dict[str, Any]:
        """Return org-wide forecast."""
        if cls._forecast is None or force_refresh:
            analytics = AnalyticsEngine.get_analytics()
            rules = ConfigLoader.get_forecast_rules()
            logger.info("Computing forecast.")
            cls._forecast = cls._compute_org_forecast(analytics, rules)
            logger.info("Forecast computation complete.")
        return cls._forecast

    @classmethod
    def get_team_forecast(cls, team_id: str) -> Dict[str, Any]:
        """Return forecast scoped to a specific team."""
        analytics = AnalyticsEngine.get_analytics()
        rules = ConfigLoader.get_forecast_rules()
        return cls._compute_team_forecast(analytics, rules, team_id)

    @classmethod
    def get_manager_forecast(cls, manager_id: str) -> Dict[str, Any]:
        """Return forecast scoped to a delivery manager's teams."""
        analytics = AnalyticsEngine.get_analytics()
        rules = ConfigLoader.get_forecast_rules()
        return cls._compute_manager_forecast(analytics, rules, manager_id)

    # ──────────────────────────────────────────────
    # Organization forecast
    # ──────────────────────────────────────────────

    @classmethod
    def _compute_org_forecast(cls, analytics: Dict, rules: Dict) -> Dict[str, Any]:
        """Compute organization-wide forecast from sprint aggregates."""
        sprint_aggs = analytics.get("sprintAggregates", [])
        engineers = analytics.get("engineers", [])
        analytics_rules = ConfigLoader.get_analytics_rules()
        sprint_duration = analytics_rules["sprint_duration_weeks"]
        risk_cfg = rules["risk_thresholds"]
        horizon = rules["forecast_horizon_sprints"]
        
        # Current capacity
        current_capacity = sum(e["availableHours"] * sprint_duration for e in engineers)
        
        # Historical velocity trend
        velocities = [s["velocity"] for s in sprint_aggs]
        utilizations = [s["utilization"] for s in sprint_aggs]
        logged_hours = [s["loggedHours"] for s in sprint_aggs]
        
        avg_velocity = cls._moving_average(velocities, rules)
        avg_utilization = cls._moving_average(utilizations, rules)
        avg_logged = cls._moving_average(logged_hours, rules)
        
        # Velocity trend (positive = accelerating, negative = decelerating)
        velocity_trend = cls._compute_trend(velocities)
        utilization_trend = cls._compute_trend(utilizations)
        
        # Projected velocity for next N sprints
        projected_velocities = cls._project_values(velocities, horizon)
        projected_utilizations = cls._project_values(utilizations, horizon)
        
        # Capacity gap
        capacity_gap = current_capacity - avg_logged if avg_logged else current_capacity
        
        # Risk assessment
        risk_level = cls._assess_risk(
            avg_utilization, velocity_trend, capacity_gap,
            current_capacity, risk_cfg
        )
        
        # Future sprint predictions
        current_sprint = analytics.get("currentSprint", "")
        current_num = AnalyticsEngine._sprint_sort_key(current_sprint)
        future_sprints = []
        for i in range(1, horizon + 1):
            sprint_name = f"Sprint {current_num + i}"
            proj_vel = projected_velocities[i - 1] if i <= len(projected_velocities) else avg_velocity
            proj_util = projected_utilizations[i - 1] if i <= len(projected_utilizations) else avg_utilization
            future_sprints.append({
                "sprint": sprint_name,
                "projectedVelocity": round(proj_vel, 1),
                "projectedUtilization": round(proj_util, 1),
                "projectedCapacity": round(current_capacity, 1),
                "risk": "High" if proj_util > risk_cfg["utilization_risk_percent"] else "Low",
            })
        
        return {
            "currentCapacity": round(current_capacity, 1),
            "averageVelocity": round(avg_velocity, 1),
            "averageUtilization": round(avg_utilization, 1),
            "velocityTrend": round(velocity_trend, 2),
            "utilizationTrend": round(utilization_trend, 2),
            "capacityGap": round(capacity_gap, 1),
            "forecastRisk": risk_level,
            "futureSprints": future_sprints,
            "trendAnalysis": {
                "velocityDirection": "increasing" if velocity_trend > 0 else ("decreasing" if velocity_trend < 0 else "stable"),
                "utilizationDirection": "increasing" if utilization_trend > 0 else ("decreasing" if utilization_trend < 0 else "stable"),
                "sprintsAnalyzed": len(sprint_aggs),
            },
        }

    # ──────────────────────────────────────────────
    # Team forecast
    # ──────────────────────────────────────────────

    @classmethod
    def _compute_team_forecast(cls, analytics: Dict, rules: Dict, team_id: str) -> Dict[str, Any]:
        """Compute forecast for a specific team."""
        engineers = [e for e in analytics.get("engineers", []) if e["teamId"] == team_id]
        if not engineers:
            return {"error": f"No engineers found for team {team_id}"}
        
        analytics_rules = ConfigLoader.get_analytics_rules()
        sprint_duration = analytics_rules["sprint_duration_weeks"]
        risk_cfg = rules["risk_thresholds"]
        
        team_capacity = sum(e["availableHours"] * sprint_duration for e in engineers)
        team_velocity = sum(e["historicalVelocity"] for e in engineers)
        team_utilization = sum(e["utilization"] for e in engineers) / len(engineers)
        team_logged = sum(e["loggedHours"] for e in engineers)
        capacity_gap = team_capacity - team_logged
        
        risk = "High" if team_utilization > risk_cfg["utilization_risk_percent"] else "Low"
        
        return {
            "teamId": team_id,
            "currentCapacity": round(team_capacity, 1),
            "averageVelocity": round(team_velocity, 1),
            "averageUtilization": round(team_utilization, 1),
            "capacityGap": round(capacity_gap, 1),
            "forecastRisk": risk,
            "forecastDemand": round(team_velocity, 1),
        }

    # ──────────────────────────────────────────────
    # Manager forecast
    # ──────────────────────────────────────────────

    @classmethod
    def _compute_manager_forecast(cls, analytics: Dict, rules: Dict, manager_id: str) -> Dict[str, Any]:
        """Compute forecast for all teams under a delivery manager."""
        teams = [t for t in analytics.get("teams", []) if t["managerId"] == manager_id]
        team_ids = {t["id"] for t in teams}
        engineers = [e for e in analytics.get("engineers", []) if e["teamId"] in team_ids]
        
        if not engineers:
            return {"error": f"No engineers found for manager {manager_id}"}
        
        analytics_rules = ConfigLoader.get_analytics_rules()
        sprint_duration = analytics_rules["sprint_duration_weeks"]
        risk_cfg = rules["risk_thresholds"]
        
        total_capacity = sum(e["availableHours"] * sprint_duration for e in engineers)
        total_velocity = sum(e["historicalVelocity"] for e in engineers)
        avg_utilization = sum(e["utilization"] for e in engineers) / len(engineers)
        total_logged = sum(e["loggedHours"] for e in engineers)
        capacity_gap = total_capacity - total_logged
        
        risk = "High" if avg_utilization > risk_cfg["utilization_risk_percent"] else "Balanced"
        
        return {
            "managerId": manager_id,
            "currentCapacity": round(total_capacity, 1),
            "averageVelocity": round(total_velocity, 1),
            "averageUtilization": round(avg_utilization, 1),
            "forecastDemand": round(total_velocity, 1),
            "capacityGap": round(capacity_gap, 1),
            "forecastRisk": risk,
        }

    # ──────────────────────────────────────────────
    # Trend analysis utilities
    # ──────────────────────────────────────────────

    @classmethod
    def _moving_average(cls, values: List[float], rules: Dict) -> float:
        """Compute simple moving average over the configured window."""
        if not values:
            return 0.0
        window = min(rules.get("smoothing", {}).get("window_size", 3), len(values))
        recent = values[-window:]
        return sum(recent) / len(recent)

    @staticmethod
    def _compute_trend(values: List[float]) -> float:
        """
        Compute linear trend (slope) using least squares.
        Positive = increasing, negative = decreasing, 0 = stable.
        """
        n = len(values)
        if n < 2:
            return 0.0
        
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0.0

    @classmethod
    def _project_values(cls, historical: List[float], horizon: int) -> List[float]:
        """Project future values using linear extrapolation from historical data."""
        if not historical:
            return [0.0] * horizon
        
        trend = cls._compute_trend(historical)
        last_value = historical[-1]
        
        return [max(0, last_value + trend * (i + 1)) for i in range(horizon)]

    @staticmethod
    def _assess_risk(
        avg_util: float, velocity_trend: float, capacity_gap: float,
        total_capacity: float, risk_cfg: Dict
    ) -> str:
        """Assess overall forecast risk level."""
        risk_factors = 0
        
        if avg_util > risk_cfg["utilization_risk_percent"]:
            risk_factors += 2
        
        if velocity_trend < 0:
            decline_pct = abs(velocity_trend)
            if decline_pct > risk_cfg.get("velocity_decline_risk_percent", 10):
                risk_factors += 1
        
        if total_capacity > 0:
            gap_pct = abs(capacity_gap) / total_capacity * 100
            if gap_pct > risk_cfg.get("capacity_gap_risk_percent", 15):
                risk_factors += 1
        
        if risk_factors >= 3:
            return "Critical"
        elif risk_factors >= 2:
            return "High"
        elif risk_factors >= 1:
            return "Medium"
        return "Low"
