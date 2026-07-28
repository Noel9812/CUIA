"""
CUIA Dataset Generator — Realistic Jira-like Enterprise Data

Generates a deterministic, schema-compliant dataset.json that produces
meaningful analytics, forecasts, recommendations, and visualizations.

Key design decisions:
- 8 completed sprints + 1 active sprint = enough history for trend analysis
- Realistic issue lifecycle (created → started → resolved with time gaps)
- Varying workloads per sprint (not uniform)
- Engineers with different utilization patterns
- Blocked issues, cross-team dependencies, critical issues
- Engineers on leave, part-time, different experience levels
- Enough variation to trigger all recommendation rules
"""

import json
import os
import random
from datetime import datetime, timedelta, timezone

# Seed for reproducibility
random.seed(42)

# ─── Configuration ───

ORG_NAME = "Global Engineering Corp"

MANAGERS = [
    {"id": "dm-1", "name": "Alice Smith"},
    {"id": "dm-2", "name": "Bob Johnson"},
]

TEAMS = [
    {"id": "t-1", "name": "Team Alpha", "managerId": "dm-1"},
    {"id": "t-2", "name": "Team Beta", "managerId": "dm-1"},
    {"id": "t-3", "name": "Team Gamma", "managerId": "dm-2"},
    {"id": "t-4", "name": "Team Delta", "managerId": "dm-2"},
]

# 16 engineers with realistic profiles
ENGINEER_PROFILES = [
    # Team Alpha (dm-1)
    {"id": "eng-1",  "name": "Charlie",  "designation": "Senior Engineer",    "experience": 6,  "teamId": "t-1", "managerId": "dm-1", "leaveHours": 0,  "primarySkills": ["Spring Boot", "Kafka"],       "secondarySkills": ["Docker", "PostgreSQL"],     "learningSkills": ["Kubernetes"],  "technologyOwnership": ["Billing Platform"], "crossTrainingCandidates": ["Eve"]},
    {"id": "eng-2",  "name": "Diana",    "designation": "Staff Engineer",     "experience": 9,  "teamId": "t-1", "managerId": "dm-1", "leaveHours": 0,  "primarySkills": ["AWS", "Go"],                  "secondarySkills": ["Python", "Terraform"],      "learningSkills": ["Kafka"],       "technologyOwnership": ["Auth Service"],     "crossTrainingCandidates": []},
    {"id": "eng-3",  "name": "Eve",      "designation": "Mid Engineer",       "experience": 3,  "teamId": "t-1", "managerId": "dm-1", "leaveHours": 0,  "primarySkills": ["React", "Node.js"],           "secondarySkills": ["Spring Boot", "Redis"],     "learningSkills": ["AWS"],         "technologyOwnership": [],                   "crossTrainingCandidates": []},
    {"id": "eng-4",  "name": "Frank",    "designation": "Junior Engineer",    "experience": 1,  "teamId": "t-1", "managerId": "dm-1", "leaveHours": 8,  "primarySkills": ["Python", "PostgreSQL"],       "secondarySkills": ["Docker", "Node.js"],        "learningSkills": ["Go"],          "technologyOwnership": [],                   "crossTrainingCandidates": []},
    # Team Beta (dm-1)
    {"id": "eng-5",  "name": "Grace",    "designation": "Principal Engineer", "experience": 12, "teamId": "t-2", "managerId": "dm-1", "leaveHours": 0,  "primarySkills": ["Kubernetes", "Terraform"],    "secondarySkills": ["AWS", "Go"],                "learningSkills": ["Azure"],       "technologyOwnership": ["Infra Platform"],   "crossTrainingCandidates": ["Ivan"]},
    {"id": "eng-6",  "name": "Heidi",    "designation": "Senior Engineer",    "experience": 5,  "teamId": "t-2", "managerId": "dm-1", "leaveHours": 16, "primarySkills": ["Node.js", "Redis"],           "secondarySkills": ["React", "Docker"],          "learningSkills": ["Kafka"],       "technologyOwnership": [],                   "crossTrainingCandidates": []},
    {"id": "eng-7",  "name": "Ivan",     "designation": "Mid Engineer",       "experience": 3,  "teamId": "t-2", "managerId": "dm-1", "leaveHours": 0,  "primarySkills": ["Spring Boot", "Docker"],      "secondarySkills": ["PostgreSQL", "AWS"],        "learningSkills": ["Kubernetes"],   "technologyOwnership": [],                   "crossTrainingCandidates": []},
    {"id": "eng-8",  "name": "Judy",     "designation": "Senior Engineer",    "experience": 7,  "teamId": "t-2", "managerId": "dm-1", "leaveHours": 0,  "primarySkills": ["Azure", "React"],             "secondarySkills": ["Node.js", "PostgreSQL"],    "learningSkills": ["Terraform"],   "technologyOwnership": [],                   "crossTrainingCandidates": []},
    # Team Gamma (dm-2)
    {"id": "eng-9",  "name": "Mallory",  "designation": "Senior Engineer",    "experience": 8,  "teamId": "t-3", "managerId": "dm-2", "leaveHours": 24, "primarySkills": ["AWS", "Go"],                  "secondarySkills": ["Kubernetes", "Python"],     "learningSkills": ["Spring Boot"], "technologyOwnership": [],                   "crossTrainingCandidates": []},
    {"id": "eng-10", "name": "Niaj",     "designation": "Staff Engineer",     "experience": 10, "teamId": "t-3", "managerId": "dm-2", "leaveHours": 0,  "primarySkills": ["Spring Boot", "Kafka"],       "secondarySkills": ["Docker", "PostgreSQL"],     "learningSkills": ["Azure"],       "technologyOwnership": ["Payment Gateway"],  "crossTrainingCandidates": []},
    {"id": "eng-11", "name": "Olivia",   "designation": "Mid Engineer",       "experience": 4,  "teamId": "t-3", "managerId": "dm-2", "leaveHours": 0,  "primarySkills": ["React", "Node.js"],           "secondarySkills": ["Terraform", "Redis"],       "learningSkills": ["Docker"],      "technologyOwnership": [],                   "crossTrainingCandidates": []},
    {"id": "eng-12", "name": "Peggy",    "designation": "Junior Engineer",    "experience": 1,  "teamId": "t-3", "managerId": "dm-2", "leaveHours": 0,  "primarySkills": ["Python", "Docker"],           "secondarySkills": ["PostgreSQL", "Redis"],      "learningSkills": ["AWS"],         "technologyOwnership": [],                   "crossTrainingCandidates": []},
    # Team Delta (dm-2)
    {"id": "eng-13", "name": "Sybil",    "designation": "Senior Engineer",    "experience": 7,  "teamId": "t-4", "managerId": "dm-2", "leaveHours": 0,  "primarySkills": ["AWS", "Terraform"],           "secondarySkills": ["Go", "Kubernetes"],         "learningSkills": ["Kafka"],       "technologyOwnership": ["Cloud Infra"],      "crossTrainingCandidates": []},
    {"id": "eng-14", "name": "Trent",    "designation": "Senior Engineer",    "experience": 6,  "teamId": "t-4", "managerId": "dm-2", "leaveHours": 0,  "primarySkills": ["React", "Node.js"],           "secondarySkills": ["Docker", "Spring Boot"],    "learningSkills": ["Azure"],       "technologyOwnership": [],                   "crossTrainingCandidates": []},
    {"id": "eng-15", "name": "Victor",   "designation": "Mid Engineer",       "experience": 3,  "teamId": "t-4", "managerId": "dm-2", "leaveHours": 8,  "primarySkills": ["PostgreSQL", "Go"],           "secondarySkills": ["Python", "Terraform"],      "learningSkills": ["Spring Boot"], "technologyOwnership": [],                   "crossTrainingCandidates": []},
    {"id": "eng-16", "name": "Walter",   "designation": "Staff Engineer",     "experience": 11, "teamId": "t-4", "managerId": "dm-2", "leaveHours": 0,  "primarySkills": ["Kafka", "Redis"],             "secondarySkills": ["Spring Boot", "AWS"],       "learningSkills": ["React"],       "technologyOwnership": ["Event Bus"],        "crossTrainingCandidates": ["Trent"]},
]

CURRENT_SPRINT = "Sprint 42"
SPRINT_DURATION_DAYS = 14
MEETING_HOURS = 3
TRAINING_HOURS = 2

# Sprint names: Sprint 34 through Sprint 42 (8 historical + 1 current)
ALL_SPRINTS = [f"Sprint {n}" for n in range(34, 43)]
HISTORICAL_SPRINTS = ALL_SPRINTS[:-1]  # Sprint 34-41

PRIORITIES = ["Critical", "High", "Medium", "Low"]
ISSUE_TYPES = ["Epic", "Story", "Task", "Bug", "Spike", "Sub-task"]
ACTIVE_STATUSES = ["To Do", "Selected for Development", "In Progress", "Code Review", "Testing", "Ready For QA", "Blocked"]
RESOLVED_STATUSES = ["Done", "Released"]
ALL_STATUSES = ACTIVE_STATUSES + RESOLVED_STATUSES

SUMMARIES = {
    "Epic":     ["Payment gateway integration", "User authentication overhaul", "Dashboard analytics engine", "API v2 migration", "Cloud infrastructure upgrade"],
    "Story":    ["Implement search filters", "Add export functionality", "Create admin panel", "Build notification system", "Implement caching layer", "Add audit logging"],
    "Task":     ["Update API documentation", "Configure CI/CD pipeline", "Set up monitoring alerts", "Database index optimization", "Update dependencies", "Code review cleanup"],
    "Bug":      ["Fix memory leak in worker", "Resolve race condition", "Fix pagination offset error", "Correct timezone handling", "Fix null pointer in reports", "Resolve CSS layout issue"],
    "Spike":    ["Evaluate message queue options", "Research GraphQL migration", "Benchmark database alternatives", "Prototype AI integration"],
    "Sub-task": ["Write unit tests", "Update schema migration", "Implement error handling", "Add validation rules", "Create integration tests"],
}


def compute_effective_capacity(leave_hours: float) -> float:
    """Compute weekly effective capacity after deductions."""
    return max(0.0, 45 - leave_hours - MEETING_HOURS - TRAINING_HOURS)


def generate_engineers():
    """Generate engineer records with computed effective capacity."""
    engineers = []
    for profile in ENGINEER_PROFILES:
        leave = profile["leaveHours"]
        effective = compute_effective_capacity(leave)
        eng = {
            "id": profile["id"],
            "name": profile["name"],
            "designation": profile["designation"],
            "experience": profile["experience"],
            "employmentType": "FTE",
            "managerId": profile["managerId"],
            "teamId": profile["teamId"],
            "workingHoursPerWeek": 45,
            "leaveHours": leave,
            "meetingHours": MEETING_HOURS,
            "trainingHours": TRAINING_HOURS,
            "effectiveCapacity": effective,
            "location": random.choice(["Remote", "Hybrid", "On-site"]),
            "availabilityStatus": "Active" if leave < 40 else "On Leave",
            "primarySkills": profile["primarySkills"],
            "secondarySkills": profile["secondarySkills"],
            "learningSkills": profile["learningSkills"],
            "technologyOwnership": profile["technologyOwnership"],
            "crossTrainingCandidates": profile["crossTrainingCandidates"],
            "certifications": [],
            "currentSprint": CURRENT_SPRINT,
            "roleLevel": profile["designation"],
        }
        engineers.append(eng)
    return engineers


def generate_issues(engineers):
    """
    Generate realistic Jira issues across all sprints.

    Historical sprints: mostly resolved (85-95% Done/Released)
    Current sprint: mix of active, in-progress, and some resolved
    """
    issues = []
    now = datetime.now(timezone.utc)
    issue_counter = 1

    for sprint_idx, sprint_name in enumerate(ALL_SPRINTS):
        is_current = (sprint_name == CURRENT_SPRINT)
        sprint_start = now - timedelta(days=(len(ALL_SPRINTS) - sprint_idx) * SPRINT_DURATION_DAYS)
        sprint_end = sprint_start + timedelta(days=SPRINT_DURATION_DAYS)

        for eng in engineers:
            # Vary issue count per engineer per sprint based on seniority
            base_issues = 3 if eng["designation"] in ("Junior Engineer", "Mid Engineer") else 4
            num_issues = random.randint(base_issues, base_issues + 3)

            for j in range(num_issues):
                issue_type = random.choices(
                    ISSUE_TYPES,
                    weights=[1, 4, 3, 3, 1, 2],
                    k=1
                )[0]

                priority = random.choices(
                    PRIORITIES,
                    weights=[1, 3, 5, 3],
                    k=1
                )[0]

                sp = random.choices([1, 2, 3, 5, 8, 13], weights=[3, 4, 5, 4, 2, 1], k=1)[0]
                original_estimate = sp * random.uniform(3.5, 5.0)

                # Determine status based on sprint phase
                if is_current:
                    # Current sprint: realistic mix
                    status = random.choices(
                        ALL_STATUSES,
                        weights=[2, 1, 4, 2, 1, 1, 1, 5, 1],  # Weighted toward In Progress and Done
                        k=1
                    )[0]
                else:
                    # Historical sprints: mostly resolved
                    resolved_pct = 0.80 + (sprint_idx * 0.02)  # Older sprints slightly less resolved
                    if random.random() < resolved_pct:
                        status = random.choice(RESOLVED_STATUSES)
                    else:
                        status = random.choice(ACTIVE_STATUSES)

                # Compute logged hours based on status
                if status in RESOLVED_STATUSES:
                    # Realistic estimation variance: ±30%
                    variance = random.uniform(0.6, 1.4)
                    logged = round(original_estimate * variance, 1)
                    remaining = 0.0
                elif status in ("In Progress", "Code Review", "Testing", "Ready For QA"):
                    progress = random.uniform(0.3, 0.9)
                    logged = round(original_estimate * progress, 1)
                    remaining = round(max(0, original_estimate - logged), 1)
                elif status == "Blocked":
                    progress = random.uniform(0.1, 0.5)
                    logged = round(original_estimate * progress, 1)
                    remaining = round(max(0, original_estimate - logged), 1)
                else:  # To Do, Selected for Development
                    logged = 0.0
                    remaining = round(original_estimate, 1)

                # Timestamps
                created_offset = random.randint(0, SPRINT_DURATION_DAYS - 1)
                created = sprint_start + timedelta(days=created_offset, hours=random.randint(8, 17))

                started = None
                resolved = None
                if status not in ("To Do", "Selected for Development"):
                    started = created + timedelta(hours=random.randint(1, 24))
                    if status in RESOLVED_STATUSES:
                        work_hours = max(1, logged)
                        resolved = started + timedelta(hours=work_hours + random.randint(0, 16))

                # Build summary
                summary_pool = SUMMARIES.get(issue_type, ["Implement feature"])
                summary = random.choice(summary_pool)

                # Dependencies (10% chance of cross-team dependency)
                deps = []
                if random.random() < 0.10 and issues:
                    dep_issue = random.choice(issues[-20:] if len(issues) > 20 else issues)
                    deps.append(dep_issue["issueKey"])

                issue = {
                    "issueKey": f"PROJ-{issue_counter:04d}",
                    "summary": summary,
                    "description": f"Implementation details for {summary.lower()}.",
                    "issueType": issue_type,
                    "priority": priority,
                    "storyPoints": sp,
                    "originalEstimate": round(original_estimate, 1),
                    "remainingEstimate": remaining,
                    "loggedHours": logged,
                    "status": status,
                    "reporter": "admin",
                    "assignee": eng["id"],
                    "sprint": sprint_name,
                    "createdTime": created.isoformat(),
                    "startedTime": started.isoformat() if started else None,
                    "resolvedTime": resolved.isoformat() if resolved else None,
                    "labels": random.choice([["backend", "api"], ["frontend", "ui"], ["infra"], ["data"], []]),
                    "blocked": status == "Blocked",
                    "dependencies": deps,
                    "parentEpic": None,
                }
                issues.append(issue)
                issue_counter += 1

    return issues


def generate_dataset():
    """Generate the complete CUIA dataset."""
    engineers = generate_engineers()
    issues = generate_issues(engineers)

    dataset = {
        "organization": {"name": ORG_NAME},
        "deliveryManagers": MANAGERS,
        "teams": TEAMS,
        "engineers": engineers,
        "issues": issues,
    }

    # Determine output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "dataset.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    # Print summary
    sprint_counts = {}
    for issue in issues:
        sprint_counts[issue["sprint"]] = sprint_counts.get(issue["sprint"], 0) + 1

    print(f"[*] Generated dataset: {len(engineers)} engineers, {len(issues)} issues")
    print(f"  Output: {output_path}")
    print(f"  Sprints: {len(ALL_SPRINTS)} ({len(HISTORICAL_SPRINTS)} historical + 1 current)")
    for sprint in ALL_SPRINTS:
        count = sprint_counts.get(sprint, 0)
        marker = " <-- current" if sprint == CURRENT_SPRINT else ""
        print(f"    {sprint}: {count} issues{marker}")


if __name__ == "__main__":
    generate_dataset()
