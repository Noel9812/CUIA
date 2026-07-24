import json
import random
import uuid
from datetime import datetime, timedelta, timezone

def generate_complex_dataset():
    managers = [
        {"id": "dm-1", "name": "Alice Smith"},
        {"id": "dm-2", "name": "Bob Johnson"}
    ]

    teams = [
        {"id": "t-1", "name": "Team Alpha", "managerId": "dm-1"},
        {"id": "t-2", "name": "Team Beta", "managerId": "dm-1"},
        {"id": "t-3", "name": "Team Gamma", "managerId": "dm-2"},
        {"id": "t-4", "name": "Team Delta", "managerId": "dm-2"}
    ]

    engineers = []
    names = ["Charlie", "Diana", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Niaj", "Olivia", "Peggy", "Sybil", "Trent", "Victor", "Walter"]
    designations = ["Junior Engineer", "Mid Engineer", "Senior Engineer", "Staff Engineer", "Principal Engineer"]
    skills_pool = ["Spring Boot", "Kafka", "PostgreSQL", "React", "Node.js", "Docker", "Kubernetes", "Redis", "AWS", "Go", "Python", "Terraform", "Azure"]
    
    for i in range(16):
        name = names[i]
        team_id = f"t-{(i // 4) + 1}"
        manager_id = "dm-1" if i < 8 else "dm-2"
        role = random.choice(designations)
        exp = 1 if role == "Junior Engineer" else (3 if role == "Mid Engineer" else 7)
        
        primary = random.sample(skills_pool, k=2)
        secondary = random.sample(list(set(skills_pool) - set(primary)), k=2)
        learning = random.sample(list(set(skills_pool) - set(primary) - set(secondary)), k=1)
        
        leave_hours = random.choice([0, 0, 4, 8, 16, 24])
        meeting_hours = 3
        training_hours = 2
        effective = 45 - leave_hours - meeting_hours - training_hours
        
        eng = {
            "id": f"eng-{i+1}",
            "name": name,
            "designation": role,
            "experience": exp,
            "employmentType": "FTE",
            "managerId": manager_id,
            "teamId": team_id,
            "workingHoursPerWeek": 45,
            "leaveHours": leave_hours,
            "meetingHours": meeting_hours,
            "trainingHours": training_hours,
            "effectiveCapacity": effective,
            "location": "Remote",
            "availabilityStatus": "Active",
            "primarySkills": primary,
            "secondarySkills": secondary,
            "learningSkills": learning,
            "technologyOwnership": ["Billing Platform"] if i == 0 else [],
            "crossTrainingCandidates": ["Eve"] if i == 0 else [],
            "certifications": [],
            "currentSprint": "Sprint 42",
            "roleLevel": role
        }
        engineers.append(eng)

    issues = []
    sprints = ["Sprint 39", "Sprint 40", "Sprint 41", "Sprint 42"]
    priorities = ["Critical", "High", "Medium", "Low"]
    issue_types = ["Epic", "Story", "Task", "Bug", "Spike", "Sub-task"]
    statuses = ["To Do", "Selected for Development", "In Progress", "Code Review", "Testing", "Ready For QA", "Blocked", "Done", "Released"]
    
    for eng in engineers:
        # Generate 5-10 issues per engineer over the 4 sprints
        num_issues = random.randint(5, 12)
        for j in range(num_issues):
            sprint_idx = random.randint(0, 3)
            sprint = sprints[sprint_idx]
            
            prio = random.choices(priorities, weights=[1, 3, 5, 2])[0]
            itype = random.choice(issue_types)
            status = random.choices(statuses, weights=[1, 1, 2, 1, 1, 1, 1, 8, 2])[0]
            
            sp = random.choice([1, 2, 3, 5, 8, 13])
            
            orig_est = sp * 4
            
            # Data quality degradation: randomly missing some
            if random.random() < 0.05:
                orig_est = 0
                sp = 0
                
            logged = random.uniform(orig_est * 0.5, orig_est * 1.5) if status in ["Done", "Released", "In Progress", "Code Review"] else 0
            rem = max(0, orig_est - logged) if status not in ["Done", "Released"] else 0
            
            created_days = (4 - sprint_idx) * 14 + random.randint(0, 10)
            created = datetime.now(timezone.utc) - timedelta(days=created_days)
            
            started = created + timedelta(hours=random.randint(1, 48)) if status not in ["To Do", "Selected for Development"] else None
            resolved = started + timedelta(hours=logged) if status in ["Done", "Released"] and started else None
            
            issue = {
                "issueKey": f"PROJ-{str(uuid.uuid4())[:6].upper()}",
                "summary": f"Task summary {j}",
                "description": "Details...",
                "issueType": itype,
                "priority": prio,
                "storyPoints": sp,
                "originalEstimate": round(orig_est, 1),
                "remainingEstimate": round(rem, 1),
                "loggedHours": round(logged, 1),
                "status": status,
                "reporter": "admin",
                "assignee": eng["id"],
                "sprint": sprint,
                "createdTime": created.isoformat(),
                "startedTime": started.isoformat() if started else None,
                "resolvedTime": resolved.isoformat() if resolved else None,
                "labels": ["backend", "api"] if random.random() > 0.5 else [],
                "blocked": status == "Blocked",
                "dependencies": [],
                "parentEpic": None
            }
            issues.append(issue)
            
    dataset = {
        "organization": {"name": "Global Engineering Corp"},
        "deliveryManagers": managers,
        "teams": teams,
        "engineers": engineers,
        "issues": issues
    }

    with open("/app/sample_data/dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"Generated realistic dataset with {len(engineers)} engineers and {len(issues)} issues.")

if __name__ == "__main__":
    generate_complex_dataset()
