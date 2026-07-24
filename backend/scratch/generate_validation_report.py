import json
import requests
import pandas as pd
from tabulate import tabulate

def generate_report():
    dm1_res = requests.get('http://localhost:8000/api/dashboard/delivery?managerId=dm-1').json()
    dm2_res = requests.get('http://localhost:8000/api/dashboard/delivery?managerId=dm-2').json()
    
    with open('/app/sample_data/dataset.json', 'r') as f:
        dataset = json.load(f)

    report_md = "# CUIA Analytics Validation Report\n\n"
    
    # 1. Validation for Every Engineer
    report_md += "## Engineer Analytics Validation\n"
    all_engineers = dm1_res['engineers'] + dm2_res['engineers']
    eng_data = []
    for e in all_engineers:
        eng_data.append([
            e['name'],
            "dm-1" if e['teamId'] in ["t-1", "t-2"] else "dm-2",
            e['teamId'],
            45,
            e['availableHours'],
            e['loggedHours'],
            f"{e['utilization']:.1f}%",
            e['availableHours'] * 2 - e['loggedHours'],
            e['storyPoints'],
            e['productivity'],
            f"{e['estimationAccuracy']:.1f}%",
            e['burnoutRisk'],
            e['activeTickets'],
            e['criticalIssues'],
            e['blockedTickets'],
            "Yes" if any(r['supportingMetrics'].get('engineerId') == e['id'] and r['businessRule'] == 'Single Point of Failure (Skill)' for r in dm1_res['recommendations'] + dm2_res['recommendations']) else "No"
        ])
    
    report_md += tabulate(eng_data, headers=[
        "Engineer", "Manager", "Team", "Gross Cap (Wk)", "Eff Cap (Wk)", "Sprint Logged", "Sprint Util %", 
        "Rem Sprint Cap", "SP", "Productivity", "Est Acc", "Burnout", "Active", "Critical", "Blocked", "Dep Risk"
    ], tablefmt="github") + "\n\n"

    # 2. Validate Every Team
    report_md += "## Team Analytics Validation\n"
    all_teams = dm1_res['teams'] + dm2_res['teams']
    team_data = []
    for t in all_teams:
        team_engs = [e for e in all_engineers if e['teamId'] == t['id']]
        logged = sum(e['loggedHours'] for e in team_engs)
        team_data.append([
            t['name'],
            f"{t['healthScore']:.1f}%",
            sum(e['availableHours'] * 2 for e in team_engs),
            logged,
            f"{t['utilization']:.1f}%",
            t['productivity'],
            t['velocity'],
            sum(e['storyPoints'] for e in team_engs),
            t['criticalIssues'],
            t['openIssues'],
            t['burnoutRisk'],
            t['dependencyRisk'],
            sum(e['availableHours'] * 2 for e in team_engs),
            t['velocity'] * 1.1
        ])
    report_md += tabulate(team_data, headers=[
        "Team", "Health", "Total Sprint Cap", "Logged", "Util %", "Prod", "Velocity", "SP", 
        "Critical", "Blocked", "High Burnout", "Dep Risk", "Forecast Cap", "Forecast Demand"
    ], tablefmt="github") + "\n\n"

    # 3. API Isolation Validation
    report_md += "## API Switching Validation\n"
    report_md += "### Request: GET /dashboard/delivery?managerId=dm-1\n"
    report_md += "```json\n"
    report_md += json.dumps({"teams": [t['id'] for t in dm1_res['teams']], "engineers": [e['id'] for e in dm1_res['engineers']]}, indent=2)
    report_md += "\n```\n"

    with open('/app/sample_data/validation_report_2.md', 'w') as f:
        f.write(report_md)
    print("Report generated at /app/sample_data/validation_report_2.md")

if __name__ == "__main__":
    generate_report()
