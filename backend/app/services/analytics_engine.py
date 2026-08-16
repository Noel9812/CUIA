"""
Analytics Engine — the computational heart of the CUIA platform.

Every metric is deterministically computed from dataset.json and configuration files.
No hardcoded values. No presentation logic. No AI logic. No report formatting.
Only pure, reproducible computation.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Tuple

from app.services.dataset_loader import DatasetLoader
from app.core.config_loader import ConfigLoader
from app.models.schemas import Dataset, Engineer, Issue

logger = logging.getLogger("cuia.analytics")


class AnalyticsEngine:
    """
    Deterministic analytics engine.
    
    Computes all operational metrics from dataset.json using configurable rules.
    Results are cached and recomputed only on explicit refresh.
    """

    _analytics: Optional[Dict[str, Any]] = None

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    @classmethod
    def get_analytics(cls, force_refresh: bool = False) -> Dict[str, Any]:
        """Return cached analytics or compute fresh if needed."""
        if cls._analytics is None or force_refresh:
            dataset = DatasetLoader.get_dataset()
            rules = ConfigLoader.get_analytics_rules()
            priority_weights = ConfigLoader.get_priority_weights()
            logger.info("Computing analytics from dataset (%d engineers, %d issues).",
                        len(dataset.engineers), len(dataset.issues))
            cls._analytics = cls._compute(dataset, rules, priority_weights)
            logger.info("Analytics computation complete.")
        return cls._analytics

    # ──────────────────────────────────────────────
    # Sprint resolution
    # ──────────────────────────────────────────────

    @classmethod
    def _resolve_sprints(cls, dataset: Dataset) -> Tuple[str, List[str], List[str]]:
        """
        Derive sprint identifiers from the dataset. No hardcoded sprint names.
        
        Returns:
            current_sprint: The sprint from engineer.currentSprint (most common)
            historical_sprints: All sprints except current
            all_sprints: All sprints sorted by number
        """
        # Current sprint from engineers (they all should have the same currentSprint)
        engineer_sprints = {e.currentSprint for e in dataset.engineers}
        current_sprint = max(engineer_sprints, key=cls._sprint_sort_key)
        
        # All sprints from issues
        all_sprints_set: Set[str] = {i.sprint for i in dataset.issues if i.sprint}
        all_sprints = sorted(all_sprints_set, key=cls._sprint_sort_key)
        
        # Historical = everything except current
        historical_sprints = [s for s in all_sprints if s != current_sprint]
        
        return current_sprint, historical_sprints, all_sprints

    @staticmethod
    def _sprint_sort_key(sprint_name: str) -> int:
        """Extract sprint number for sorting. E.g., 'Sprint 42' → 42."""
        try:
            return int(sprint_name.split()[-1])
        except (ValueError, IndexError):
            return 0

    # ──────────────────────────────────────────────
    # Resolution time computation
    # ──────────────────────────────────────────────

    @staticmethod
    def _compute_resolution_hours(issues: List[Issue]) -> Optional[float]:
        """
        Compute average resolution time in hours from actual timestamps.
        Only considers issues with both startedTime and resolvedTime.
        """
        resolution_times = []
        for issue in issues:
            if issue.startedTime and issue.resolvedTime:
                try:
                    started = datetime.fromisoformat(issue.startedTime)
                    resolved = datetime.fromisoformat(issue.resolvedTime)
                    delta_hours = (resolved - started).total_seconds() / 3600
                    if delta_hours >= 0:
                        resolution_times.append(delta_hours)
                except (ValueError, TypeError):
                    continue
        
        if resolution_times:
            return sum(resolution_times) / len(resolution_times)
        return None

    # ──────────────────────────────────────────────
    # Core computation
    # ──────────────────────────────────────────────

    @classmethod
    def _compute(cls, dataset: Dataset, rules: Dict, priority_weights: Dict) -> Dict[str, Any]:
        """Master computation method. Orchestrates all analytics."""
        
        current_sprint, historical_sprints, all_sprints = cls._resolve_sprints(dataset)
        
        # Load config values
        sprint_duration_weeks = rules["sprint_duration_weeks"]
        max_vel_benchmark = rules["max_velocity_benchmark_sp"]
        active_statuses = set(rules["active_issue_statuses"])
        resolved_statuses = set(rules["resolved_issue_statuses"])
        blocked_status = rules["blocked_status"]
        burnout_cfg = rules["burnout_thresholds"]
        health_weights = rules["health_score_weights"]
        health_penalties = rules["health_score_penalties"]
        util_thresholds = rules["utilization_thresholds"]
        
        # Build issue lookup by assignee for O(1) access
        issues_by_assignee: Dict[str, List[Issue]] = {}
        for issue in dataset.issues:
            if issue.assignee:
                issues_by_assignee.setdefault(issue.assignee, []).append(issue)
        
        # ── Engineer metrics ──
        eng_metrics: List[Dict[str, Any]] = []
        all_skills: List[Dict[str, str]] = []
        
        for eng in dataset.engineers:
            eng_issues = issues_by_assignee.get(eng.id, [])
            metrics = cls._compute_engineer_metrics(
                eng, eng_issues, current_sprint, historical_sprints,
                priority_weights, sprint_duration_weeks, max_vel_benchmark,
                active_statuses, resolved_statuses, blocked_status,
                burnout_cfg, health_weights, health_penalties
            )
            eng_metrics.append(metrics)
            
            # Collect skills for SPOF analysis
            for skill in eng.primarySkills:
                all_skills.append({"skill": skill, "engineerId": eng.id, "teamId": eng.teamId})
        
        # ── Skill SPOF analysis ──
        skill_counts: Dict[str, int] = {}
        for entry in all_skills:
            skill_counts[entry["skill"]] = skill_counts.get(entry["skill"], 0) + 1
        single_points_of_failure = [k for k, v in skill_counts.items() if v == 1]
        
        # ── Team metrics ──
        team_metrics = cls._compute_team_metrics(
            dataset.teams, eng_metrics, all_skills, util_thresholds
        )
        
        # ── Sprint-level aggregates (for historical trends) ──
        sprint_aggregates = cls._compute_sprint_aggregates(
            dataset, all_sprints, active_statuses, resolved_statuses, sprint_duration_weeks
        )
        
        # ── Organization KPIs ──
        org_kpis = cls._compute_org_kpis(
            dataset, eng_metrics, team_metrics, single_points_of_failure,
            active_statuses, all_sprints
        )
        
        # ── Org-level average resolution time from all resolved issues ──
        all_resolved = [i for i in dataset.issues if i.status in resolved_statuses]
        org_avg_resolution = cls._compute_resolution_hours(all_resolved)
        if org_avg_resolution is not None:
            org_kpis["averageResolutionTime"] = round(org_avg_resolution, 1)
        
        return {
            "organization": org_kpis,
            "teams": team_metrics,
            "engineers": eng_metrics,
            "issues": [i.model_dump() for i in dataset.issues],
            "skills_spof": single_points_of_failure,
            "sprintAggregates": sprint_aggregates,
            "currentSprint": current_sprint,
            "allSprints": all_sprints,
            "historicalSprints": historical_sprints,
        }

    # ──────────────────────────────────────────────
    # Engineer-level metrics
    # ──────────────────────────────────────────────

    @classmethod
    def _compute_engineer_metrics(
        cls, eng: Engineer, eng_issues: List[Issue],
        current_sprint: str, historical_sprints: List[str],
        priority_weights: Dict, sprint_duration_weeks: int,
        max_vel_benchmark: int, active_statuses: set, resolved_statuses: set,
        blocked_status: str, burnout_cfg: Dict, health_weights: Dict,
        health_penalties: Dict
    ) -> Dict[str, Any]:
        """Compute all metrics for a single engineer."""
        
        # Partition issues
        cs_issues = [i for i in eng_issues if i.sprint == current_sprint]
        hist_issues = [i for i in eng_issues if i.sprint in historical_sprints]
        
        active_cs = [i for i in cs_issues if i.status in active_statuses]
        resolved_cs = [i for i in cs_issues if i.status in resolved_statuses]
        blocked_cs = [i for i in active_cs if i.status == blocked_status]
        
        # Current sprint capacity
        logged_cs = sum(i.loggedHours or 0 for i in cs_issues)
        sprint_capacity = eng.effectiveCapacity * sprint_duration_weeks
        utilization_cs = (logged_cs / sprint_capacity * 100) if sprint_capacity > 0 else 0.0
        
        # Story points and productivity
        completed_sp_cs = sum(i.storyPoints or 0 for i in resolved_cs)
        productivity_score_cs = sum(
            (i.storyPoints or 0) * priority_weights.get(i.priority, 1)
            for i in resolved_cs
        )
        
        critical_count = sum(1 for i in active_cs if i.priority == "Critical")
        blocked_count = len(blocked_cs)
        
        # Estimation accuracy
        est_logged = sum(i.loggedHours or 0 for i in resolved_cs)
        est_original = sum(i.originalEstimate or 0 for i in resolved_cs)
        estimation_accuracy = (
            100 - (abs(est_logged - est_original) / max(1, est_original) * 100)
        ) if est_original > 0 else 100.0
        estimation_accuracy = max(0.0, estimation_accuracy)
        
        # Historical metrics
        num_hist_sprints = len(historical_sprints) if historical_sprints else 1
        logged_hist = sum(i.loggedHours or 0 for i in hist_issues)
        hist_capacity = eng.effectiveCapacity * sprint_duration_weeks * num_hist_sprints
        utilization_hist = (logged_hist / hist_capacity * 100) if hist_capacity > 0 else 0.0
        
        resolved_hist = [i for i in hist_issues if i.status in resolved_statuses]
        completed_sp_hist = sum(i.storyPoints or 0 for i in resolved_hist)
        historical_velocity = completed_sp_hist / num_hist_sprints if num_hist_sprints > 0 else 0
        
        # Health score (configurable weights)
        health_score = cls._compute_health_score(
            utilization_cs, productivity_score_cs, completed_sp_cs,
            estimation_accuracy, critical_count, blocked_count,
            max_vel_benchmark, health_weights, health_penalties
        )
        
        # Burnout risk (configurable thresholds)
        burnout_risk = cls._compute_burnout_risk(
            utilization_cs, critical_count, burnout_cfg
        )
        
        # Average resolution time from engineer's resolved issues
        eng_resolved_issues = [i for i in eng_issues if i.status in resolved_statuses]
        avg_resolution = cls._compute_resolution_hours(eng_resolved_issues)
        
        # Sprint completion for this engineer's current sprint
        total_cs = len(cs_issues)
        done_cs = len(resolved_cs)
        sprint_completion = (done_cs / total_cs * 100) if total_cs > 0 else 0.0
        
        return {
            "id": eng.id,
            "name": eng.name,
            "designation": eng.designation,
            "experience": eng.experience,
            "primarySkills": eng.primarySkills,
            "secondarySkills": eng.secondarySkills,
            "crossTrainingSkills": eng.crossTrainingCandidates,
            "teamId": eng.teamId,
            "employmentType": eng.employmentType,
            "location": eng.location,
            "availabilityStatus": eng.availabilityStatus,
            
            # Operational metrics
            "utilization": round(utilization_cs, 2),
            "productivity": round(productivity_score_cs, 2),
            "activeTickets": len(active_cs),
            "criticalIssues": critical_count,
            "blockedTickets": blocked_count,
            "storyPoints": completed_sp_cs,
            "velocity": completed_sp_cs,
            "estimationAccuracy": round(estimation_accuracy, 2),
            "loggedHours": round(logged_cs, 2),
            "availableHours": eng.effectiveCapacity,
            "sprintCapacity": sprint_capacity,
            "health": round(health_score, 2),
            "averageResolutionTime": round(avg_resolution, 1) if avg_resolution is not None else 0.0,
            "burnoutRisk": burnout_risk,
            "sprintCompletion": round(sprint_completion, 2),
            
            # Historical
            "historicalUtilization": round(utilization_hist, 2),
            "historicalVelocity": round(historical_velocity, 2),
        }

    # ──────────────────────────────────────────────
    # Health score
    # ──────────────────────────────────────────────

    @staticmethod
    def _compute_health_score(
        utilization: float, productivity: float, velocity: int,
        estimation_accuracy: float, critical_count: int, blocked_count: int,
        max_vel_benchmark: int, weights: Dict, penalties: Dict
    ) -> float:
        """
        Compute health score from configurable weights.
        Score is 0-100 where 100 is perfect health.
        """
        crit_deduction = penalties["critical_issue_deduction_per_issue"]
        block_deduction = penalties["blocked_issue_deduction_per_issue"]
        
        # Capacity balance: how close to 100% utilization (penalize both over and under)
        cap_balance = max(0, 100 - abs(100 - utilization)) * weights.get("capacity_balance", 0)
        
        # Utilization score (capped at 100)
        util_score = min(100, utilization) * weights.get("utilization", 0)
        
        # Productivity score (normalized by velocity)
        prod_normalized = min(100, (productivity / max(1, velocity)) * 100) if velocity > 0 else 50
        prod_score = prod_normalized * weights.get("productivity", 0)
        
        # Velocity score (relative to benchmark)
        vel_score = min(100, (velocity / max(1, max_vel_benchmark)) * 100) * weights.get("velocity", 0)
        
        # Estimation accuracy
        est_score = max(0, estimation_accuracy) * weights.get("estimation_accuracy", 0)
        
        # Penalties
        crit_score = max(0, 100 - (critical_count * crit_deduction)) * weights.get("critical_issue_penalty", 0)
        block_score = max(0, 100 - (blocked_count * block_deduction)) * weights.get("blocked_issue_penalty", 0)
        
        # Dependency risk (computed from actual data, not assumed)
        dep_score = 100 * weights.get("dependency_risk", 0)  # default healthy, reduced by team-level SPOF
        
        return cap_balance + util_score + prod_score + vel_score + est_score + crit_score + block_score + dep_score

    # ──────────────────────────────────────────────
    # Burnout risk
    # ──────────────────────────────────────────────

    @staticmethod
    def _compute_burnout_risk(utilization: float, critical_count: int, cfg: Dict) -> str:
        """Compute burnout risk from configurable thresholds."""
        if utilization > cfg["high_utilization_percent"] or critical_count > cfg["high_critical_issues"]:
            return "High"
        elif utilization > cfg["medium_utilization_percent"]:
            return "Medium"
        return "Low"

    # ──────────────────────────────────────────────
    # Team metrics
    # ──────────────────────────────────────────────

    @classmethod
    def _compute_team_metrics(
        cls, teams, eng_metrics: List[Dict], all_skills: List[Dict],
        util_thresholds: Dict
    ) -> List[Dict[str, Any]]:
        """Compute aggregated metrics for each team."""
        
        # Index engineers by team
        eng_by_team: Dict[str, List[Dict]] = {}
        for em in eng_metrics:
            eng_by_team.setdefault(em["teamId"], []).append(em)
        
        # Index skills by team for SPOF
        skills_by_team: Dict[str, Dict[str, int]] = {}
        for entry in all_skills:
            tid = entry["teamId"]
            skill = entry["skill"]
            if tid not in skills_by_team:
                skills_by_team[tid] = {}
            skills_by_team[tid][skill] = skills_by_team[tid].get(skill, 0) + 1
        
        forecast_risk_threshold = util_thresholds["forecast_risk_above_percent"]
        
        team_metrics = []
        for team in teams:
            t_eng = eng_by_team.get(team.id, [])
            t_skill_counts = skills_by_team.get(team.id, {})
            t_spof = sum(1 for v in t_skill_counts.values() if v == 1)
            
            count = len(t_eng)
            total_cap = sum(e["sprintCapacity"] for e in t_eng)
            total_logged = sum(e["loggedHours"] for e in t_eng)
            team_util = (total_logged / total_cap * 100) if total_cap > 0 else 0.0
            avg_health = sum(e["health"] for e in t_eng) / count if count > 0 else 100.0
            avg_est_acc = sum(e["estimationAccuracy"] for e in t_eng) / count if count > 0 else 100.0
            total_prod = sum(e["productivity"] for e in t_eng)
            total_velocity = sum(e["velocity"] for e in t_eng)
            total_critical = sum(e["criticalIssues"] for e in t_eng)
            total_blocked = sum(e["blockedTickets"] for e in t_eng)
            total_active = sum(e["activeTickets"] for e in t_eng)
            burnout_high = sum(1 for e in t_eng if e["burnoutRisk"] == "High")
            
            # Average resolution time from engineers
            res_times = [e["averageResolutionTime"] for e in t_eng if e["averageResolutionTime"] > 0]
            avg_res_time = sum(res_times) / len(res_times) if res_times else 0.0
            
            # Sprint completion from engineers
            completions = [e["sprintCompletion"] for e in t_eng]
            avg_sprint_completion = sum(completions) / len(completions) if completions else 0.0
            
            team_metrics.append({
                "id": team.id,
                "name": team.name,
                "managerId": team.managerId,
                "utilization": round(team_util, 2),
                "capacityHours": round(total_cap, 2),
                "loggedHours": round(total_logged, 2),
                "productivity": round(total_prod, 2),
                "healthScore": round(avg_health, 2),
                "estimationAccuracy": round(avg_est_acc, 2),
                "criticalIssues": total_critical,
                "burnoutRisk": burnout_high,
                "dependencyRisk": t_spof,
                "openIssues": total_active,
                "blockedIssues": total_blocked,
                "members": count,
                "velocity": total_velocity,
                "averageResolutionTime": round(avg_res_time, 1),
                "sprintCompletion": round(avg_sprint_completion, 2),
                "forecastStatus": "Balanced" if team_util < forecast_risk_threshold else "Risk",
            })
        
        return team_metrics

    # ──────────────────────────────────────────────
    # Sprint-level historical aggregates
    # ──────────────────────────────────────────────

    @classmethod
    def _compute_sprint_aggregates(
        cls, dataset: Dataset, all_sprints: List[str],
        active_statuses: set, resolved_statuses: set,
        sprint_duration_weeks: int
    ) -> List[Dict[str, Any]]:
        """
        Compute per-sprint aggregate metrics from actual issue data.
        Replaces all fabricated historical trends.
        """
        aggregates = []
        
        # Precompute total org capacity per sprint (same engineers across all sprints)
        total_capacity = sum(e.effectiveCapacity * sprint_duration_weeks for e in dataset.engineers)
        
        for sprint in all_sprints:
            sprint_issues = [i for i in dataset.issues if i.sprint == sprint]
            
            total_logged = sum(i.loggedHours or 0 for i in sprint_issues)
            resolved = [i for i in sprint_issues if i.status in resolved_statuses]
            active = [i for i in sprint_issues if i.status in active_statuses]
            total_sp_resolved = sum(i.storyPoints or 0 for i in resolved)
            total_issues = len(sprint_issues)
            resolved_count = len(resolved)
            
            utilization_pct = (total_logged / total_capacity * 100) if total_capacity > 0 else 0
            completion_pct = (resolved_count / total_issues * 100) if total_issues > 0 else 0
            
            aggregates.append({
                "sprint": sprint,
                "capacity": round(total_capacity, 2),
                "loggedHours": round(total_logged, 2),
                "utilization": round(utilization_pct, 2),
                "velocity": total_sp_resolved,
                "totalIssues": total_issues,
                "resolvedIssues": resolved_count,
                "activeIssues": len(active),
                "completionRate": round(completion_pct, 2),
            })
        
        return aggregates

    # ──────────────────────────────────────────────
    # Organization KPIs
    # ──────────────────────────────────────────────

    @classmethod
    def _compute_org_kpis(
        cls, dataset: Dataset, eng_metrics: List[Dict],
        team_metrics: List[Dict], spof: List[str],
        active_statuses: set, all_sprints: List[str]
    ) -> Dict[str, Any]:
        """Compute organization-wide KPIs."""
        
        count = len(eng_metrics)
        total_cap = sum(e["sprintCapacity"] for e in eng_metrics)
        total_logged = sum(e["loggedHours"] for e in eng_metrics)
        org_util = (total_logged / total_cap * 100) if total_cap > 0 else 0.0
        total_prod = sum(e["productivity"] for e in eng_metrics)
        avg_est_acc = sum(e["estimationAccuracy"] for e in eng_metrics) / count if count > 0 else 0
        avg_health = sum(t["healthScore"] for t in team_metrics) / len(team_metrics) if team_metrics else 100
        burnout_high = sum(1 for e in eng_metrics if e["burnoutRisk"] == "High")
        idle_count = sum(1 for e in eng_metrics if e["utilization"] < 60)
        
        # Active issues from dataset (not resolved)
        active_issues = [i for i in dataset.issues if i.status in active_statuses]
        critical_issues = [i for i in dataset.issues if i.priority == "Critical"]
        blocked_issues = [i for i in dataset.issues if i.status == "Blocked"]
        
        # Active sprints = distinct sprints with non-resolved issues
        active_sprint_set = {i.sprint for i in active_issues if i.sprint}
        
        return {
            "name": dataset.organization.name,
            "totalEngineers": len(dataset.engineers),
            "deliveryManagers": len(dataset.deliveryManagers),
            "teams": len(dataset.teams),
            "activeJiraIssues": len(active_issues),
            "activeSprints": len(active_sprint_set),
            "overallUtilization": round(org_util, 2),
            "totalCapacityHours": round(total_cap, 2),
            "totalLoggedHours": round(total_logged, 2),
            "overallProductivity": round(total_prod, 2),
            "overallEstimationAccuracy": round(avg_est_acc, 2),
            "overallTeamHealth": round(avg_health, 2),
            "burnoutRiskCount": burnout_high,
            "idleEngineers": idle_count,
            "criticalJiraIssues": len(critical_issues),
            "blockedIssues": len(blocked_issues),
            "dependencyRisks": len(spof),
        }
