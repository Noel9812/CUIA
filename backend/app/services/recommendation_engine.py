"""
Recommendation Engine — deterministic, config-driven recommendations.

All recommendations originate from business rules defined in
config/recommendation_rules.json. AI never generates recommendations.
Recommendations include reason, business impact, supporting metrics,
confidence, recommended action, expected outcome, priority, and severity.
"""

import logging
from typing import List, Dict, Any

from app.services.analytics_engine import AnalyticsEngine
from app.core.config_loader import ConfigLoader
from app.models.schemas import Recommendation

logger = logging.getLogger("cuia.recommendations")


class RecommendationEngine:
    """
    Deterministic recommendation engine.
    
    Evaluates business rules from configuration against computed analytics.
    No hardcoded thresholds, no hardcoded recommendation text.
    All templates are configurable.
    """

    @classmethod
    def get_recommendations(cls) -> List[Recommendation]:
        """Generate all recommendations from analytics + config rules."""
        analytics = AnalyticsEngine.get_analytics()
        rule_config = ConfigLoader.get_recommendation_rules()
        rules = rule_config.get("rules", [])
        
        recs: List[Recommendation] = []
        
        for rule in rules:
            scope = rule.get("scope", "")
            
            if scope == "engineer":
                recs.extend(cls._evaluate_engineer_rule(rule, analytics))
            elif scope == "engineer_skill":
                recs.extend(cls._evaluate_skill_rule(rule, analytics))
            elif scope == "team":
                recs.extend(cls._evaluate_team_rule(rule, analytics))
            elif scope == "organization":
                recs.extend(cls._evaluate_org_rule(rule, analytics))
        
        logger.info("Generated %d recommendations from %d rules.", len(recs), len(rules))
        return recs

    # ──────────────────────────────────────────────
    # Rule evaluation by scope
    # ──────────────────────────────────────────────

    @classmethod
    def _evaluate_engineer_rule(cls, rule: Dict, analytics: Dict) -> List[Recommendation]:
        """Evaluate a rule against each engineer's metrics."""
        recs = []
        field = rule["condition_field"]
        operator = rule["condition_operator"]
        threshold = rule["condition_value"]
        
        for eng in analytics.get("engineers", []):
            value = eng.get(field)
            if value is None:
                continue
            
            if cls._check_condition(value, operator, threshold):
                rec = cls._build_recommendation(rule, eng, threshold)
                recs.append(rec)
        
        return recs

    @classmethod
    def _evaluate_skill_rule(cls, rule: Dict, analytics: Dict) -> List[Recommendation]:
        """Evaluate skill-based rules (SPOF detection)."""
        recs = []
        spof_skills = set(analytics.get("skills_spof", []))
        
        for eng in analytics.get("engineers", []):
            for skill in eng.get("primarySkills", []):
                if skill in spof_skills:
                    context = {**eng, "skill": skill, "coverage": 1}
                    rec = cls._build_recommendation(rule, context, rule["condition_value"])
                    recs.append(rec)
        
        return recs

    @classmethod
    def _evaluate_team_rule(cls, rule: Dict, analytics: Dict) -> List[Recommendation]:
        """Evaluate a rule against each team's metrics."""
        recs = []
        field = rule["condition_field"]
        operator = rule["condition_operator"]
        threshold = rule["condition_value"]
        
        for team in analytics.get("teams", []):
            value = team.get(field)
            if value is None:
                continue
            
            if cls._check_condition(value, operator, threshold):
                rec = cls._build_recommendation(rule, team, threshold)
                recs.append(rec)
        
        return recs

    @classmethod
    def _evaluate_org_rule(cls, rule: Dict, analytics: Dict) -> List[Recommendation]:
        """Evaluate organization-level rules."""
        recs = []
        # Organization rules can use forecast data or org KPIs
        org = analytics.get("organization", {})
        field = rule["condition_field"]
        operator = rule["condition_operator"]
        threshold = rule["condition_value"]
        
        value = org.get(field)
        if value is not None and cls._check_condition(value, operator, threshold):
            rec = cls._build_recommendation(rule, org, threshold)
            recs.append(rec)
        
        return recs

    # ──────────────────────────────────────────────
    # Condition checking
    # ──────────────────────────────────────────────

    @staticmethod
    def _check_condition(value: Any, operator: str, threshold: Any) -> bool:
        """Evaluate a condition: value <operator> threshold."""
        try:
            if operator == ">":
                return value > threshold
            elif operator == "<":
                return value < threshold
            elif operator == ">=":
                return value >= threshold
            elif operator == "<=":
                return value <= threshold
            elif operator == "==":
                return value == threshold
            elif operator == "!=":
                return value != threshold
        except TypeError:
            return False
        return False

    # ──────────────────────────────────────────────
    # Recommendation building from templates
    # ──────────────────────────────────────────────

    @classmethod
    def _build_recommendation(cls, rule: Dict, context: Dict, threshold: Any) -> Recommendation:
        """
        Build a Recommendation from a rule template and context data.
        Template variables like {name}, {utilization}, {threshold} are resolved.
        """
        # Merge threshold into context for template rendering
        # Also create snake_case aliases so templates like {logged_hours} resolve from {loggedHours}
        template_vars = {**context, "threshold": threshold}
        for key, val in context.items():
            # Convert camelCase to snake_case: loggedHours -> logged_hours
            snake = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            if snake not in template_vars:
                template_vars[snake] = val
            # Also keep original camelCase
            template_vars[key] = val
        
        def render(template: str) -> str:
            """Render a template string with context variables."""
            try:
                return template.format(**template_vars)
            except (KeyError, IndexError, ValueError):
                # Fallback: return template with unresolved vars
                return template
        
        # Build supporting metrics from context (only include relevant fields)
        supporting = {}
        if "id" in context:
            key = "teamId" if rule.get("scope") == "team" else "engineerId"
            supporting[key] = context["id"]
        
        field = rule.get("condition_field", "")
        if field in context:
            supporting[field] = context[field]
        
        if "skill" in context:
            supporting["skill"] = context["skill"]
            supporting["coverage"] = context.get("coverage", 1)
        
        return Recommendation(
            severity=rule.get("severity", "Medium"),
            businessRule=render(rule.get("business_rule", "")),
            reason=render(rule.get("reason_template", "")),
            businessImpact=render(rule.get("impact_template", "")),
            supportingMetrics=supporting,
            suggestedAction=render(rule.get("action_template", "")),
            expectedOutcome=render(rule.get("outcome_template", "")),
            confidence=rule.get("confidence", "Medium"),
            sourceAnalytics=rule.get("source_analytics", ""),
        )
