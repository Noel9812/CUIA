"""
What-If Simulation Engine — deterministic scenario analysis for CUIA.

Supports scenarios such as engineer leave/join/departure, capacity changes,
work redistribution, issue additions/removals, and team restructuring.

The simulator clones the current analytics state, applies changes,
recomputes analytics, and returns a before/after comparison.
No simulation permanently modifies the original dataset.
"""

import copy
import logging
from typing import Dict, Any, List, Optional

from app.services.analytics_engine import AnalyticsEngine
from app.services.dataset_loader import DatasetLoader
from app.core.config_loader import ConfigLoader
from app.models.schemas import Dataset, Engineer, Issue

logger = logging.getLogger("cuia.simulation")


class SimulationEngine:
    """
    Deterministic what-if simulation engine.
    
    Each simulation:
    1. Deep-clones the current dataset
    2. Applies the requested scenario changes
    3. Recomputes analytics on the modified dataset
    4. Returns before/after comparison with delta metrics
    """

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    @classmethod
    def simulate(cls, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a what-if simulation.
        
        Args:
            scenario: Dict with 'type' and type-specific parameters.
            
        Supported types:
            - engineer_leave: {"type": "engineer_leave", "engineerId": "eng-1", "leaveHours": 40}
            - team_leave: {"type": "team_leave", "teamId": "t-1", "leaveHours": 40}
            - engineer_join: {"type": "engineer_join", "engineer": {...}}
            - engineer_depart: {"type": "engineer_depart", "engineerId": "eng-1"}
            - capacity_change: {"type": "capacity_change", "engineerId": "eng-1", "newCapacity": 30}
            - add_issues: {"type": "add_issues", "issues": [...]}
            - remove_issues: {"type": "remove_issues", "issueKeys": [...]}
            - redistribute_work: {"type": "redistribute_work", "fromEngineerId": "eng-1", "toEngineerId": "eng-2"}
            - team_restructure: {"type": "team_restructure", "engineerId": "eng-1", "newTeamId": "t-2"}
            - skill_gain: {"type": "skill_gain", "engineerId": "eng-1", "skill": "React"}
            - skill_loss: {"type": "skill_loss", "engineerId": "eng-1", "skill": "React"}
            - team_merge: {"type": "team_merge", "fromTeamId": "t-1", "toTeamId": "t-2"}
            - team_split: {"type": "team_split", "teamId": "t-1", "newTeamId": "t-new", "newTeamName": "New Team"}
            - sprint_delay: {"type": "sprint_delay", "days": 7}
            
        Returns:
            Dict with "before", "after", and "delta" analytics.
        """
        scenario_type = scenario.get("type")
        if not scenario_type:
            return {"error": "Missing scenario type."}
        
        logger.info("Running simulation: %s", scenario_type)
        
        # Capture 'before' state
        before_analytics = AnalyticsEngine.get_analytics()
        
        # Clone dataset
        original_dataset = DatasetLoader.get_dataset()
        cloned_dataset = cls._clone_dataset(original_dataset)
        
        # Apply scenario
        handler = cls._get_handler(scenario_type)
        if handler is None:
            return {"error": f"Unknown scenario type: {scenario_type}"}
        
        try:
            modified_dataset = handler(cloned_dataset, scenario)
        except Exception as e:
            logger.error("Simulation failed: %s", str(e))
            return {"error": f"Simulation failed: {str(e)}"}
        
        # Recompute analytics on modified dataset
        rules = ConfigLoader.get_analytics_rules()
        priority_weights = ConfigLoader.get_priority_weights()
        after_analytics = AnalyticsEngine._compute(modified_dataset, rules, priority_weights)
        
        # Compute deltas
        delta = cls._compute_delta(before_analytics, after_analytics)
        
        logger.info("Simulation complete: %s", scenario_type)
        
        return {
            "scenarioType": scenario_type,
            "scenarioParams": {k: v for k, v in scenario.items() if k != "type"},
            "before": cls._extract_summary(before_analytics),
            "after": cls._extract_summary(after_analytics),
            "delta": delta,
        }

    # ──────────────────────────────────────────────
    # Dataset cloning
    # ──────────────────────────────────────────────

    @staticmethod
    def _clone_dataset(dataset: Dataset) -> Dataset:
        """Create a deep copy of the dataset to prevent mutation."""
        return Dataset(**copy.deepcopy(dataset.model_dump()))

    # ──────────────────────────────────────────────
    # Scenario handlers
    # ──────────────────────────────────────────────

    @classmethod
    def _get_handler(cls, scenario_type: str):
        """Map scenario type to handler method."""
        handlers = {
            "engineer_leave": cls._handle_engineer_leave,
            "team_leave": cls._handle_team_leave,
            "engineer_join": cls._handle_engineer_join,
            "engineer_depart": cls._handle_engineer_depart,
            "capacity_change": cls._handle_capacity_change,
            "add_issues": cls._handle_add_issues,
            "remove_issues": cls._handle_remove_issues,
            "redistribute_work": cls._handle_redistribute_work,
            "team_restructure": cls._handle_team_restructure,
            "skill_gain": cls._handle_skill_gain,
            "skill_loss": cls._handle_skill_loss,
            "team_merge": cls._handle_team_merge,
            "team_split": cls._handle_team_split,
            "sprint_delay": cls._handle_sprint_delay,
        }
        return handlers.get(scenario_type)

    @staticmethod
    def _handle_engineer_leave(dataset: Dataset, scenario: Dict) -> Dataset:
        """Simulate an engineer going on leave (reduced capacity)."""
        eng_id = scenario.get("engineerId")
        leave_hours = scenario.get("leaveHours", 40)
        
        for eng in dataset.engineers:
            if eng.id == eng_id:
                eng.leaveHours += leave_hours
                eng.effectiveCapacity = max(0, eng.workingHoursPerWeek - eng.leaveHours - eng.meetingHours - eng.trainingHours)
                break
        
        return dataset

    @staticmethod
    def _handle_engineer_join(dataset: Dataset, scenario: Dict) -> Dataset:
        """Simulate a new engineer joining a team."""
        eng_data = scenario.get("engineer", {})
        if not eng_data:
            raise ValueError("Missing engineer data for join scenario.")
        
        new_eng = Engineer(**eng_data)
        dataset.engineers.append(new_eng)
        return dataset

    @staticmethod
    def _handle_engineer_depart(dataset: Dataset, scenario: Dict) -> Dataset:
        """Simulate an engineer leaving the organization."""
        eng_id = scenario.get("engineerId")
        
        # Remove engineer
        dataset.engineers = [e for e in dataset.engineers if e.id != eng_id]
        
        # Unassign their issues (set to None)
        for issue in dataset.issues:
            if issue.assignee == eng_id:
                issue.assignee = None
        
        return dataset

    @staticmethod
    def _handle_capacity_change(dataset: Dataset, scenario: Dict) -> Dataset:
        """Simulate a change in an engineer's effective capacity."""
        eng_id = scenario.get("engineerId")
        new_capacity = scenario.get("newCapacity")
        
        for eng in dataset.engineers:
            if eng.id == eng_id:
                eng.effectiveCapacity = new_capacity
                break
        
        return dataset

    @staticmethod
    def _handle_add_issues(dataset: Dataset, scenario: Dict) -> Dataset:
        """Simulate adding new issues to the current sprint."""
        new_issues = scenario.get("issues", [])
        for issue_data in new_issues:
            dataset.issues.append(Issue(**issue_data))
        return dataset

    @staticmethod
    def _handle_remove_issues(dataset: Dataset, scenario: Dict) -> Dataset:
        """Simulate removing issues from the sprint."""
        keys_to_remove = set(scenario.get("issueKeys", []))
        dataset.issues = [i for i in dataset.issues if i.issueKey not in keys_to_remove]
        return dataset

    @staticmethod
    def _handle_redistribute_work(dataset: Dataset, scenario: Dict) -> Dataset:
        """Simulate redistributing all issues from one engineer to another."""
        from_id = scenario.get("fromEngineerId")
        to_id = scenario.get("toEngineerId")
        
        for issue in dataset.issues:
            if issue.assignee == from_id:
                issue.assignee = to_id
        
        return dataset

    @staticmethod
    def _handle_team_restructure(dataset: Dataset, scenario: Dict) -> Dataset:
        """Simulate moving an engineer to a different team."""
        eng_id = scenario.get("engineerId")
        new_team_id = scenario.get("newTeamId")
        
        for eng in dataset.engineers:
            if eng.id == eng_id:
                eng.teamId = new_team_id
                # Update managerId based on new team
                for team in dataset.teams:
                    if team.id == new_team_id:
                        eng.managerId = team.managerId
                        break
                break
        
        return dataset

    @staticmethod
    def _handle_skill_gain(dataset: Dataset, scenario: Dict) -> Dataset:
        eng_id = scenario.get("engineerId")
        skill = scenario.get("skill")
        for eng in dataset.engineers:
            if eng.id == eng_id:
                if skill not in eng.primarySkills and skill not in eng.secondarySkills:
                    eng.secondarySkills.append(skill)
                break
        return dataset

    @staticmethod
    def _handle_skill_loss(dataset: Dataset, scenario: Dict) -> Dataset:
        eng_id = scenario.get("engineerId")
        skill = scenario.get("skill")
        for eng in dataset.engineers:
            if eng.id == eng_id:
                eng.primarySkills = [s for s in eng.primarySkills if s != skill]
                eng.secondarySkills = [s for s in eng.secondarySkills if s != skill]
                eng.learningSkills = [s for s in eng.learningSkills if s != skill]
                break
        return dataset

    @staticmethod
    def _handle_team_merge(dataset: Dataset, scenario: Dict) -> Dataset:
        from_team_id = scenario.get("fromTeamId")
        to_team_id = scenario.get("toTeamId")
        to_team = next((t for t in dataset.teams if t.id == to_team_id), None)
        if to_team:
            for eng in dataset.engineers:
                if eng.teamId == from_team_id:
                    eng.teamId = to_team_id
                    eng.managerId = to_team.managerId
            dataset.teams = [t for t in dataset.teams if t.id != from_team_id]
        return dataset

    @staticmethod
    def _handle_team_split(dataset: Dataset, scenario: Dict) -> Dataset:
        from_team_id = scenario.get("teamId")
        new_team_id = scenario.get("newTeamId")
        new_team_name = scenario.get("newTeamName", "New Split Team")
        
        from_team = next((t for t in dataset.teams if t.id == from_team_id), None)
        if from_team:
            from app.models.schemas import Team
            new_team = Team(id=new_team_id, name=new_team_name, managerId=from_team.managerId)
            dataset.teams.append(new_team)
            
            engs_in_team = [e for e in dataset.engineers if e.teamId == from_team_id]
            # Move half
            for i, eng in enumerate(engs_in_team):
                if i % 2 == 1:
                    eng.teamId = new_team_id
        return dataset

    @staticmethod
    def _handle_sprint_delay(dataset: Dataset, scenario: Dict) -> Dataset:
        """Simulate sprint delay by reducing effective capacity to simulate lost time."""
        days = scenario.get("days", 7)
        hours_lost = (days / 5) * 40 # Rough translation to work hours
        for eng in dataset.engineers:
            eng.leaveHours += hours_lost
            eng.effectiveCapacity = max(0, eng.workingHoursPerWeek - eng.leaveHours - eng.meetingHours - eng.trainingHours)
        return dataset

    # ──────────────────────────────────────────────
    # Delta computation
    # ──────────────────────────────────────────────

    @classmethod
    def _extract_summary(cls, analytics: Dict) -> Dict[str, Any]:
        """Extract key metrics for comparison."""
        org = analytics.get("organization", {})
        teams = analytics.get("teams", [])
        engineers = analytics.get("engineers", [])
        
        return {
            "organization": {
                "totalEngineers": org.get("totalEngineers", 0),
                "overallUtilization": org.get("overallUtilization", 0),
                "overallProductivity": org.get("overallProductivity", 0),
                "overallTeamHealth": org.get("overallTeamHealth", 0),
                "burnoutRiskCount": org.get("burnoutRiskCount", 0),
                "idleEngineers": org.get("idleEngineers", 0),
                "criticalJiraIssues": org.get("criticalJiraIssues", 0),
                "blockedIssues": org.get("blockedIssues", 0),
                "dependencyRisks": org.get("dependencyRisks", 0),
            },
            "teams": [{
                "id": t["id"],
                "name": t["name"],
                "utilization": t["utilization"],
                "healthScore": t["healthScore"],
                "members": t["members"],
                "velocity": t["velocity"],
            } for t in teams],
            "engineerCount": len(engineers),
        }

    @classmethod
    def _compute_delta(cls, before: Dict, after: Dict) -> Dict[str, Any]:
        """Compute the difference between before and after states."""
        before_org = before.get("organization", {})
        after_org = after.get("organization", {})
        
        delta_fields = [
            "totalEngineers", "overallUtilization", "overallProductivity",
            "overallTeamHealth", "burnoutRiskCount", "idleEngineers",
            "criticalJiraIssues", "blockedIssues", "dependencyRisks"
        ]
        
        org_delta = {}
        for field in delta_fields:
            b = before_org.get(field, 0)
            a = after_org.get(field, 0)
            if isinstance(b, (int, float)) and isinstance(a, (int, float)):
                org_delta[field] = round(a - b, 2)
        
        return {"organization": org_delta}
