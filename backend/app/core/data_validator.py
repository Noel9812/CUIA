"""
Data validation for the CUIA platform.

Validates the dataset.json structure and relationships before analytics
can be computed. Catches missing values, orphan references, duplicate IDs,
invalid assignments, and structural issues.
"""

import logging
from typing import List, Dict, Any
from app.models.schemas import Dataset

logger = logging.getLogger("cuia.validation")


class ValidationError:
    """Represents a single validation issue."""
    
    def __init__(self, severity: str, field: str, message: str, record_id: str = None):
        self.severity = severity  # "error" | "warning"
        self.field = field
        self.message = message
        self.record_id = record_id
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"severity": self.severity, "field": self.field, "message": self.message}
        if self.record_id:
            result["record_id"] = self.record_id
        return result


class DataValidator:
    """Validates dataset integrity before analytics computation."""
    
    @classmethod
    def validate(cls, dataset: Dataset) -> List[ValidationError]:
        """
        Run all validation checks against the dataset.
        Returns a list of ValidationError objects. Empty list = valid.
        """
        errors: List[ValidationError] = []
        
        errors.extend(cls._validate_organization(dataset))
        errors.extend(cls._validate_no_duplicate_ids(dataset))
        errors.extend(cls._validate_team_manager_references(dataset))
        errors.extend(cls._validate_engineer_references(dataset))
        errors.extend(cls._validate_issue_references(dataset))
        errors.extend(cls._validate_issue_data_quality(dataset))
        errors.extend(cls._validate_sprint_consistency(dataset))
        
        if errors:
            error_count = sum(1 for e in errors if e.severity == "error")
            warn_count = sum(1 for e in errors if e.severity == "warning")
            logger.warning(
                "Dataset validation: %d error(s), %d warning(s)",
                error_count, warn_count
            )
        else:
            logger.info("Dataset validation passed with no issues.")
        
        return errors
    
    @classmethod
    def _validate_organization(cls, dataset: Dataset) -> List[ValidationError]:
        errors = []
        if not dataset.organization or not dataset.organization.name:
            errors.append(ValidationError("error", "organization.name", "Organization name is missing."))
        return errors
    
    @classmethod
    def _validate_no_duplicate_ids(cls, dataset: Dataset) -> List[ValidationError]:
        errors = []
        
        # Check engineer IDs
        eng_ids = [e.id for e in dataset.engineers]
        seen = set()
        for eid in eng_ids:
            if eid in seen:
                errors.append(ValidationError("error", "engineers.id", f"Duplicate engineer ID: {eid}", eid))
            seen.add(eid)
        
        # Check team IDs
        team_ids = [t.id for t in dataset.teams]
        seen = set()
        for tid in team_ids:
            if tid in seen:
                errors.append(ValidationError("error", "teams.id", f"Duplicate team ID: {tid}", tid))
            seen.add(tid)
        
        # Check issue keys
        issue_keys = [i.issueKey for i in dataset.issues]
        seen = set()
        for ik in issue_keys:
            if ik in seen:
                errors.append(ValidationError("error", "issues.issueKey", f"Duplicate issue key: {ik}", ik))
            seen.add(ik)
        
        # Check delivery manager IDs
        dm_ids = [dm.id for dm in dataset.deliveryManagers]
        seen = set()
        for dmid in dm_ids:
            if dmid in seen:
                errors.append(ValidationError("error", "deliveryManagers.id", f"Duplicate DM ID: {dmid}", dmid))
            seen.add(dmid)
        
        return errors
    
    @classmethod
    def _validate_team_manager_references(cls, dataset: Dataset) -> List[ValidationError]:
        errors = []
        dm_ids = {dm.id for dm in dataset.deliveryManagers}
        
        for team in dataset.teams:
            if team.managerId not in dm_ids:
                errors.append(ValidationError(
                    "error", "teams.managerId",
                    f"Team '{team.name}' references non-existent manager: {team.managerId}",
                    team.id
                ))
        return errors
    
    @classmethod
    def _validate_engineer_references(cls, dataset: Dataset) -> List[ValidationError]:
        errors = []
        team_ids = {t.id for t in dataset.teams}
        dm_ids = {dm.id for dm in dataset.deliveryManagers}
        
        for eng in dataset.engineers:
            if eng.teamId not in team_ids:
                errors.append(ValidationError(
                    "error", "engineers.teamId",
                    f"Engineer '{eng.name}' references non-existent team: {eng.teamId}",
                    eng.id
                ))
            if eng.managerId not in dm_ids:
                errors.append(ValidationError(
                    "error", "engineers.managerId",
                    f"Engineer '{eng.name}' references non-existent manager: {eng.managerId}",
                    eng.id
                ))
            if eng.effectiveCapacity <= 0:
                errors.append(ValidationError(
                    "warning", "engineers.effectiveCapacity",
                    f"Engineer '{eng.name}' has zero or negative effective capacity: {eng.effectiveCapacity}",
                    eng.id
                ))
        return errors
    
    @classmethod
    def _validate_issue_references(cls, dataset: Dataset) -> List[ValidationError]:
        errors = []
        eng_ids = {e.id for e in dataset.engineers}
        
        for issue in dataset.issues:
            if issue.assignee and issue.assignee not in eng_ids:
                errors.append(ValidationError(
                    "error", "issues.assignee",
                    f"Issue '{issue.issueKey}' assigned to non-existent engineer: {issue.assignee}",
                    issue.issueKey
                ))
        return errors
    
    @classmethod
    def _validate_issue_data_quality(cls, dataset: Dataset) -> List[ValidationError]:
        errors = []
        
        for issue in dataset.issues:
            if issue.loggedHours < 0:
                errors.append(ValidationError(
                    "error", "issues.loggedHours",
                    f"Issue '{issue.issueKey}' has negative logged hours: {issue.loggedHours}",
                    issue.issueKey
                ))
            if issue.storyPoints is not None and issue.storyPoints < 0:
                errors.append(ValidationError(
                    "error", "issues.storyPoints",
                    f"Issue '{issue.issueKey}' has negative story points: {issue.storyPoints}",
                    issue.issueKey
                ))
            if issue.originalEstimate is not None and issue.originalEstimate < 0:
                errors.append(ValidationError(
                    "error", "issues.originalEstimate",
                    f"Issue '{issue.issueKey}' has negative original estimate: {issue.originalEstimate}",
                    issue.issueKey
                ))
            # Warn if Done/Released but no resolvedTime
            if issue.status in ("Done", "Released") and not issue.resolvedTime:
                errors.append(ValidationError(
                    "warning", "issues.resolvedTime",
                    f"Issue '{issue.issueKey}' is {issue.status} but has no resolvedTime.",
                    issue.issueKey
                ))
        return errors
    
    @classmethod
    def _validate_sprint_consistency(cls, dataset: Dataset) -> List[ValidationError]:
        errors = []
        
        # Check that engineers' currentSprint appears in issues
        engineer_sprints = {e.currentSprint for e in dataset.engineers}
        issue_sprints = {i.sprint for i in dataset.issues if i.sprint}
        
        for sprint in engineer_sprints:
            if sprint not in issue_sprints:
                errors.append(ValidationError(
                    "warning", "engineers.currentSprint",
                    f"Engineer currentSprint '{sprint}' has no matching issues."
                ))
        
        if not issue_sprints:
            errors.append(ValidationError(
                "error", "issues.sprint",
                "No sprint data found in any issues."
            ))
        
        return errors
