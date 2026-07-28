"""
Deterministic Business Rules Engine — computes ambiguous concepts via config.

The LLM NEVER decides who is the "best performer", "most at risk", etc.
This engine computes those answers deterministically from configurable weights.

Concepts supported:
- Best/worst performer scoring
- Team status classification (Healthy / At Risk / Critical)
- Capacity risk assessment
- Replacement candidate scoring
- Priority attention ranking (who needs help first)
- Trend classification (improving / degrading / stable)
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from app.services.analytics_engine import AnalyticsEngine
from app.core.config_loader import ConfigLoader

logger = logging.getLogger("cuia.business_rules")


class BusinessRulesEngine:
    """
    Deterministic business rules engine.
    
    Every ambiguous concept (best performer, team health status, etc.)
    is computed here with configurable weights. AI only explains results.
    """

    @classmethod
    def _get_rules(cls) -> Dict[str, Any]:
        """Load business rules configuration."""
        return ConfigLoader._load_json("business_rules.json")

    # ──────────────────────────────────────────────
    # Performance scoring
    # ──────────────────────────────────────────────

    @classmethod
    def rank_engineers_by_performance(cls, engineers: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        """
        Rank engineers by deterministic weighted performance score.
        
        Returns list of {id, name, teamId, score, breakdown} sorted by score desc.
        """
        rules = cls._get_rules()
        perf = rules["performance_scoring"]
        weights = perf["weights"]
        norms = perf["normalization"]
        target_util = perf["utilization_balance_target"]

        if engineers is None:
            analytics = AnalyticsEngine.get_analytics()
            engineers = analytics["engineers"]

        scored = []
        for eng in engineers:
            # Velocity component (normalized to benchmark)
            vel_norm = min(100, (eng["velocity"] / max(1, norms["velocity_benchmark"])) * 100)
            vel_score = vel_norm * weights["velocity"]

            # Health component
            health_score = (eng["health"] / norms["health_max"]) * 100 * weights["health"]

            # Estimation accuracy component
            est_score = (eng["estimationAccuracy"] / norms["estimation_max"]) * 100 * weights["estimation_accuracy"]

            # Utilization balance (closer to target = better)
            util_diff = abs(eng["utilization"] - target_util)
            util_balance = max(0, 100 - util_diff)
            util_score = util_balance * weights["utilization_balance"]

            # Blocked penalty
            blocked_penalty = min(100, eng["blockedTickets"] * 25) * abs(weights["blocked_penalty"])

            total = vel_score + health_score + est_score + util_score - blocked_penalty

            scored.append({
                "id": eng["id"],
                "name": eng["name"],
                "teamId": eng["teamId"],
                "performanceScore": round(total, 2),
                "breakdown": {
                    "velocity": round(vel_score, 2),
                    "health": round(health_score, 2),
                    "estimation": round(est_score, 2),
                    "utilization_balance": round(util_score, 2),
                    "blocked_penalty": round(-blocked_penalty, 2),
                },
            })

        scored.sort(key=lambda x: x["performanceScore"], reverse=True)
        return scored

    # ──────────────────────────────────────────────
    # Team status classification
    # ──────────────────────────────────────────────

    @classmethod
    def classify_team_status(cls, team: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a team as Healthy / At Risk / Critical.
        
        Returns {status, label, reasons}.
        """
        rules = cls._get_rules()
        status_rules = rules["team_status_rules"]
        
        healthy = status_rules["healthy"]
        at_risk = status_rules["at_risk"]
        
        reasons = []
        
        health = team.get("healthScore", 100)
        burnout = team.get("burnoutRisk", 0)
        blocked = team.get("blockedIssues", 0)
        
        if (health >= healthy["min_health_score"] 
                and burnout <= healthy["max_burnout_count"]
                and blocked <= healthy["max_blocked_issues"]):
            return {"status": "healthy", "label": healthy["label"], "reasons": ["All metrics within healthy thresholds"]}
        
        if (health >= at_risk["min_health_score"]
                and burnout <= at_risk["max_burnout_count"]
                and blocked <= at_risk["max_blocked_issues"]):
            if health < healthy["min_health_score"]:
                reasons.append(f"Health score ({health:.1f}) below healthy threshold ({healthy['min_health_score']})")
            if burnout > healthy["max_burnout_count"]:
                reasons.append(f"{burnout} engineer(s) at high burnout risk")
            if blocked > healthy["max_blocked_issues"]:
                reasons.append(f"{blocked} blocked issues")
            return {"status": "at_risk", "label": at_risk["label"], "reasons": reasons}
        
        if health < at_risk["min_health_score"]:
            reasons.append(f"Health score critically low ({health:.1f})")
        if burnout > at_risk["max_burnout_count"]:
            reasons.append(f"{burnout} engineers at high burnout risk (exceeds threshold)")
        if blocked > at_risk["max_blocked_issues"]:
            reasons.append(f"{blocked} blocked issues (exceeds threshold)")
        
        return {"status": "critical", "label": status_rules["critical"]["label"], "reasons": reasons}

    # ──────────────────────────────────────────────
    # Capacity risk assessment
    # ──────────────────────────────────────────────

    @classmethod
    def assess_capacity_risk(cls, utilization: float) -> Dict[str, str]:
        """Classify capacity risk level from utilization percentage."""
        rules = cls._get_rules()
        cap = rules["capacity_risk_rules"]
        labels = cap["labels"]
        
        if utilization >= cap["high_risk_utilization"]:
            return {"level": "high", "label": labels["high"]}
        elif utilization >= cap["medium_risk_utilization"]:
            return {"level": "medium", "label": labels["medium"]}
        elif utilization >= cap["low_risk_utilization"]:
            return {"level": "balanced", "label": labels["balanced"]}
        elif utilization >= cap["overstaffed_threshold"]:
            return {"level": "low", "label": labels["low"]}
        else:
            return {"level": "overstaffed", "label": labels["overstaffed"]}

    # ──────────────────────────────────────────────
    # Priority attention ranking
    # ──────────────────────────────────────────────

    @classmethod
    def rank_by_attention_priority(cls, engineers: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
        """
        Rank engineers by who needs attention most urgently.
        
        Higher score = needs more immediate help.
        """
        rules = cls._get_rules()
        attn = rules["priority_attention"]
        
        if engineers is None:
            analytics = AnalyticsEngine.get_analytics()
            engineers = analytics["engineers"]
        
        scored = []
        for eng in engineers:
            burnout_score = (100 if eng["burnoutRisk"] == "High" else 50 if eng["burnoutRisk"] == "Medium" else 0)
            util_score = min(100, max(0, eng["utilization"] - 80) * 2)  # Ramps up above 80%
            blocked_score = min(100, eng["blockedTickets"] * 33)
            critical_score = min(100, eng["criticalIssues"] * 25)
            
            total = (
                burnout_score * attn["burnout_weight"] / 100
                + util_score * attn["utilization_weight"] / 100
                + blocked_score * attn["blocked_weight"] / 100
                + critical_score * attn["critical_issues_weight"] / 100
            )
            
            if total > 0:
                scored.append({
                    "id": eng["id"],
                    "name": eng["name"],
                    "teamId": eng["teamId"],
                    "attentionScore": round(total, 2),
                    "burnoutRisk": eng["burnoutRisk"],
                    "utilization": eng["utilization"],
                    "blockedTickets": eng["blockedTickets"],
                    "criticalIssues": eng["criticalIssues"],
                })
        
        scored.sort(key=lambda x: x["attentionScore"], reverse=True)
        return scored

    # ──────────────────────────────────────────────
    # Replacement candidate scoring
    # ──────────────────────────────────────────────

    @classmethod
    def find_replacement_candidates(cls, engineer_id: str) -> List[Dict[str, Any]]:
        """
        Find and rank replacement candidates for a given engineer.
        
        Considers skill overlap, available capacity, and experience.
        """
        rules = cls._get_rules()
        repl = rules["replacement_scoring"]
        
        analytics = AnalyticsEngine.get_analytics()
        engineers = analytics["engineers"]
        
        # Find target engineer
        target = None
        for eng in engineers:
            if eng["id"] == engineer_id:
                target = eng
                break
        
        if not target:
            return []
        
        target_skills = set(target.get("primarySkills", []) + target.get("secondarySkills", []))
        
        candidates = []
        for eng in engineers:
            if eng["id"] == engineer_id:
                continue
            
            eng_skills = set(eng.get("primarySkills", []) + eng.get("secondarySkills", []) + eng.get("crossTrainingSkills", []))
            
            # Skill overlap
            overlap = len(target_skills & eng_skills)
            skill_score = (overlap / max(1, len(target_skills))) * 100
            
            # Capacity (lower utilization = more available)
            capacity_score = max(0, 100 - eng["utilization"])
            
            # Experience (normalized to 15 years)
            exp_score = min(100, (eng.get("experience", 0) / 15) * 100)
            
            total = (
                skill_score * repl["skill_match_weight"]
                + capacity_score * repl["capacity_weight"]
                + exp_score * repl["experience_weight"]
            )
            
            if total > 10:  # Minimum viability threshold
                candidates.append({
                    "id": eng["id"],
                    "name": eng["name"],
                    "teamId": eng["teamId"],
                    "replacementScore": round(total, 2),
                    "skillOverlap": overlap,
                    "totalTargetSkills": len(target_skills),
                    "utilization": eng["utilization"],
                    "experience": eng.get("experience", 0),
                })
        
        candidates.sort(key=lambda x: x["replacementScore"], reverse=True)
        return candidates
