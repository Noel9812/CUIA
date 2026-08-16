import json
import os
import sys

def run_audit():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(base_dir)
    
    # Load raw dataset
    with open(os.path.join(base_dir, 'sample_data', 'dataset.json'), 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
    # Get config rules for dependencies
    with open(os.path.join(base_dir, 'app', 'config', 'analytics_rules.json'), 'r', encoding='utf-8') as f:
        rules = json.load(f)
        
    sprint_duration_weeks = rules["sprint_duration_weeks"]
    resolved_statuses = set(rules["resolved_issue_statuses"])
    active_statuses = set(rules["active_issue_statuses"])

    engineers = dataset['engineers']
    issues = dataset['issues']
    teams = dataset['teams']

    # Current sprint from max engineer.currentSprint
    current_sprint = max({e["currentSprint"] for e in engineers}, key=lambda s: int(s.split()[-1]))
    
    # INDEPENDENT CALCULATION
    
    # Engineeer metrics
    eng_expected = {}
    for eng in engineers:
        sprint_cap = eng['effectiveCapacity'] * sprint_duration_weeks
        eng_issues = [i for i in issues if i.get('assignee') == eng['id'] and i.get('sprint') == current_sprint]
        
        logged = sum(i.get('loggedHours', 0) or 0 for i in eng_issues)
        utilization = (logged / sprint_cap * 100) if sprint_cap > 0 else 0.0
        
        resolved = [i for i in eng_issues if i.get('status') in resolved_statuses]
        velocity = sum(i.get('storyPoints', 0) or 0 for i in resolved)
        
        eng_expected[eng['id']] = {
            'utilization': round(utilization, 2),
            'sprintCapacity': sprint_cap,
            'loggedHours': round(logged, 2),
            'velocity': velocity,
            'teamId': eng['teamId']
        }
        
    # Team metrics
    team_expected = {}
    for team in teams:
        team_engs = [e for e in eng_expected.values() if e['teamId'] == team['id']]
        cap = sum(e['sprintCapacity'] for e in team_engs)
        logged = sum(e['loggedHours'] for e in team_engs)
        util = (logged / cap * 100) if cap > 0 else 0.0
        vel = sum(e['velocity'] for e in team_engs)
        
        team_expected[team['id']] = {
            'capacityHours': round(cap, 2),
            'loggedHours': round(logged, 2),
            'utilization': round(util, 2),
            'velocity': vel
        }
        
    # COMPARE WITH APPLICATION
    from app.services.analytics_engine import AnalyticsEngine
    app_data = AnalyticsEngine.get_analytics(force_refresh=True)
    
    print("=== ENGINEER VALIDATION ===")
    eng_errors = 0
    for app_eng in app_data['engineers']:
        exp = eng_expected[app_eng['id']]
        for k in ['utilization', 'sprintCapacity', 'loggedHours', 'velocity']:
            # Handle float rounding differences
            if abs(app_eng[k] - exp[k]) > 0.01:
                print(f"Mismatch for engineer {app_eng['id']} metric {k}: Expected {exp[k]}, Actual {app_eng[k]}")
                eng_errors += 1
                
    if eng_errors == 0:
        print("All engineer metrics match.")
        
    print("\n=== TEAM VALIDATION ===")
    team_errors = 0
    for app_team in app_data['teams']:
        exp = team_expected[app_team['id']]
        for k in ['capacityHours', 'loggedHours', 'utilization', 'velocity']:
            if abs(app_team[k] - exp[k]) > 0.01:
                print(f"Mismatch for team {app_team['id']} metric {k}: Expected {exp[k]}, Actual {app_team[k]}")
                team_errors += 1
                
    if team_errors == 0:
        print("All team metrics match.")
        
    if eng_errors > 0 or team_errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_audit()
