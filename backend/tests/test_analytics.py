import pytest
import json
from app.services.analytics_engine import AnalyticsEngine
from app.models.schemas import Engineer, Issue


# ── Unit: engineer utilization formula ────────────────────────────────

def test_utilization_formula():
    eng = Engineer(
        id="e1", name="Test Eng", designation="Dev", experience=5, employmentType="FTE",
        managerId="dm1", teamId="t1", workingHoursPerWeek=40, leaveHours=0, meetingHours=0,
        trainingHours=0, effectiveCapacity=40, location="Remote", availabilityStatus="Available",
        primarySkills=[], secondarySkills=[], learningSkills=[], technologyOwnership=[],
        crossTrainingCandidates=[], certifications=[], currentSprint="Sprint 1", roleLevel="Mid"
    )
    issues = [
        Issue(
            issueKey="1", summary="test", description="test", issueType="Task", priority="High",
            storyPoints=5, originalEstimate=10, remainingEstimate=0, loggedHours=20, status="Resolved",
            reporter="r", assignee="e1", sprint="Sprint 1", createdTime="2024-01-01", labels=[], blocked=False,
            dependencies=[]
        )
    ]
    # Capacity = 40 (effective) * 2 (sprint weeks) = 80
    # Logged = 20
    # Util = 20 / 80 * 100 = 25.0
    metrics = AnalyticsEngine._compute_engineer_metrics(
        eng, issues, "Sprint 1", [], {}, 2, 10, {"In Progress"}, {"Resolved"}, "Blocked",
        {"high_utilization_percent": 90, "high_critical_issues": 3, "medium_utilization_percent": 70},
        {"capacity_balance": 0.2, "utilization": 0.2, "productivity": 0.2, "velocity": 0.2, "estimation_accuracy": 0.2},
        {"critical_issue_deduction_per_issue": 5, "blocked_issue_deduction_per_issue": 5}
    )
    assert metrics["utilization"] == 25.0
    assert metrics["sprintCapacity"] == 80
    assert metrics["loggedHours"] == 20


# ── Unit: zero-capacity edge case ─────────────────────────────────────

def test_zero_capacity_utilization():
    eng = Engineer(
        id="e2", name="Test Eng2", designation="Dev", experience=5, employmentType="FTE",
        managerId="dm1", teamId="t1", workingHoursPerWeek=0, leaveHours=0, meetingHours=0,
        trainingHours=0, effectiveCapacity=0, location="Remote", availabilityStatus="Available",
        primarySkills=[], secondarySkills=[], learningSkills=[], technologyOwnership=[],
        crossTrainingCandidates=[], certifications=[], currentSprint="Sprint 1", roleLevel="Mid"
    )
    metrics = AnalyticsEngine._compute_engineer_metrics(
        eng, [], "Sprint 1", [], {}, 2, 10, {"In Progress"}, {"Resolved"}, "Blocked",
        {"high_utilization_percent": 90, "high_critical_issues": 3, "medium_utilization_percent": 70},
        {"capacity_balance": 0.2, "utilization": 0.2, "productivity": 0.2, "velocity": 0.2, "estimation_accuracy": 0.2},
        {"critical_issue_deduction_per_issue": 5, "blocked_issue_deduction_per_issue": 5}
    )
    assert metrics["utilization"] == 0.0


# ── Integration: org-level utilization consistency ────────────────────

def test_org_utilization_is_not_average_of_averages():
    """
    Org utilization must equal totalLoggedHours / totalCapacityHours * 100.
    This validates the corrected aggregation (sum/sum) not the old average-of-averages.
    """
    analytics = AnalyticsEngine.get_analytics()
    org = analytics["organization"]

    expected_util = (org["totalLoggedHours"] / org["totalCapacityHours"] * 100) if org["totalCapacityHours"] > 0 else 0
    assert abs(org["overallUtilization"] - round(expected_util, 2)) < 0.01, (
        f"Org utilization mismatch: got {org['overallUtilization']}, expected {round(expected_util, 2)}"
    )


