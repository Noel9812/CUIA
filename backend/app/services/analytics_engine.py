import pandas as pd
from app.services.dataset_loader import DatasetLoader
from typing import Dict, Any, List
from datetime import datetime

class AnalyticsEngine:
    _instance = None
    _analytics = None

    @classmethod
    def get_analytics(cls, force_refresh=False) -> Dict[str, Any]:
        if cls._analytics is None or force_refresh:
            dataset = DatasetLoader.get_dataset()
            cls._analytics = cls._calculate(dataset)
        return cls._analytics

    @classmethod
    def _calculate(cls, dataset) -> Dict[str, Any]:
        engineers_df = pd.DataFrame([e.model_dump() for e in dataset.engineers])
        teams_df = pd.DataFrame([t.model_dump() for t in dataset.teams])
        issues_df = pd.DataFrame([i.model_dump() for i in dataset.issues])
        
        # Time windows setup
        current_sprint = "Sprint 42"
        previous_sprint = "Sprint 41"
        historical_sprints = ["Sprint 39", "Sprint 40", "Sprint 41"]
        
        # Priority Weights
        priority_weights = {"Low": 1, "Medium": 3, "High": 5, "Critical": 8}
        issues_df['priorityWeight'] = issues_df['priority'].map(priority_weights).fillna(1)
        
        eng_metrics = []
        all_skills = []
        
        for eng in dataset.engineers:
            eng_issues = issues_df[issues_df['assignee'] == eng.id]
            current_sprint_issues = eng_issues[eng_issues['sprint'] == current_sprint]
            hist_issues = eng_issues[eng_issues['sprint'].isin(historical_sprints)]
            
            # Current Sprint Metrics
            active_issues_cs = current_sprint_issues[current_sprint_issues['status'].isin(['To Do', 'Selected for Development', 'In Progress', 'Code Review', 'Testing', 'Ready For QA', 'Blocked'])]
            resolved_issues_cs = current_sprint_issues[current_sprint_issues['status'].isin(['Done', 'Released'])]
            blocked_issues_cs = active_issues_cs[active_issues_cs['status'] == 'Blocked']
            
            logged_cs = current_sprint_issues['loggedHours'].sum()
            weekly_capacity = eng.effectiveCapacity
            sprint_capacity = weekly_capacity * 2
            
            utilization_cs = (logged_cs / sprint_capacity) * 100 if sprint_capacity > 0 else 0
            
            completed_sp_cs = resolved_issues_cs['storyPoints'].sum()
            productivity_score_cs = sum(row['storyPoints'] * row['priorityWeight'] for _, row in resolved_issues_cs.iterrows())
            
            critical_issues_cs = len(active_issues_cs[active_issues_cs['priority'] == 'Critical'])
            blocked_count_cs = len(blocked_issues_cs)
            
            # Historical Metrics
            logged_hist = hist_issues['loggedHours'].sum()
            hist_capacity = weekly_capacity * 6 # 3 sprints
            utilization_hist = (logged_hist / hist_capacity) * 100 if hist_capacity > 0 else 0
            
            resolved_issues_hist = hist_issues[hist_issues['status'].isin(['Done', 'Released'])]
            completed_sp_hist = resolved_issues_hist['storyPoints'].sum()
            
            # Health Score Calculation
            cap_balance = max(0, 100 - abs(100 - utilization_cs)) * 0.20
            util_score = min(100, utilization_cs) * 0.20
            prod_score = min(100, (productivity_score_cs / max(1, completed_sp_cs)) * 100) * 0.15
            vel_score = min(100, (completed_sp_cs / 20) * 100) * 0.15 # Assuming 20 SP is max
            est_acc = 100 - (abs(resolved_issues_cs['loggedHours'].sum() - resolved_issues_cs['originalEstimate'].sum()) / max(1, resolved_issues_cs['originalEstimate'].sum()) * 100)
            est_score = max(0, est_acc) * 0.10
            crit_score = max(0, 100 - (critical_issues_cs * 20)) * 0.05
            block_score = max(0, 100 - (blocked_count_cs * 20)) * 0.05
            
            health_score = cap_balance + util_score + prod_score + vel_score + est_score + crit_score + block_score + 10 # 10 for dep risk assumed 0
            
            # Burnout Risk
            burnout_risk = "Low"
            if utilization_cs > 110 or critical_issues_cs > 2:
                burnout_risk = "High"
            elif utilization_cs > 95:
                burnout_risk = "Medium"
                
            for s in eng.primarySkills:
                all_skills.append({"skill": s, "engineerId": eng.id, "teamId": eng.teamId})
                
            eng_metrics.append({
                "id": eng.id,
                "name": eng.name,
                "designation": eng.designation,
                "experience": eng.experience,
                "primarySkills": eng.primarySkills,
                "secondarySkills": eng.secondarySkills,
                "crossTrainingSkills": eng.crossTrainingCandidates,
                "teamId": eng.teamId,
                
                # Operational
                "utilization": float(utilization_cs),
                "productivity": float(productivity_score_cs),
                "activeTickets": int(len(active_issues_cs)),
                "criticalIssues": int(critical_issues_cs),
                "blockedTickets": int(blocked_count_cs),
                "storyPoints": int(completed_sp_cs),
                "velocity": int(completed_sp_cs),
                "estimationAccuracy": float(max(0, est_acc)),
                "loggedHours": float(logged_cs),
                "availableHours": float(weekly_capacity),
                "health": float(health_score),
                "averageResolutionTime": 24.5,
                "burnoutRisk": burnout_risk,
                
                # Historical Window
                "historicalUtilization": float(utilization_hist),
                "historicalVelocity": int(completed_sp_hist / 3)
            })
            
        skills_df = pd.DataFrame(all_skills)
        skill_counts = skills_df.groupby('skill').size().to_dict() if len(skills_df) > 0 else {}
        single_points_of_failure = [k for k, v in skill_counts.items() if v == 1]
            
        eng_df = pd.DataFrame(eng_metrics)
        
        team_metrics = []
        for team in dataset.teams:
            t_eng = eng_df[eng_df['teamId'] == team.id]
            t_skills = skills_df[skills_df['teamId'] == team.id] if len(skills_df) > 0 else pd.DataFrame()
            t_skill_counts = t_skills.groupby('skill').size().to_dict() if len(t_skills) > 0 else {}
            t_spof = len([k for k, v in t_skill_counts.items() if v == 1])
            
            team_metrics.append({
                "id": team.id,
                "name": team.name,
                "managerId": team.managerId,
                "utilization": float(t_eng['utilization'].mean()) if len(t_eng) > 0 else 0.0,
                "productivity": float(t_eng['productivity'].sum()) if len(t_eng) > 0 else 0.0,
                "healthScore": float(t_eng['health'].mean()) if len(t_eng) > 0 else 100.0,
                "estimationAccuracy": float(t_eng['estimationAccuracy'].mean()) if len(t_eng) > 0 else 100.0,
                "criticalIssues": int(t_eng['criticalIssues'].sum()),
                "burnoutRisk": int(len(t_eng[t_eng['burnoutRisk'] == "High"])),
                "dependencyRisk": t_spof,
                "openIssues": int(t_eng['activeTickets'].sum()),
                "members": int(len(t_eng)),
                "velocity": int(t_eng['velocity'].sum()),
                "averageResolutionTime": float(t_eng['averageResolutionTime'].mean()) if len(t_eng) > 0 else 0.0,
                "forecastStatus": "Balanced" if float(t_eng['utilization'].mean()) < 90 else "Risk"
            })
            
        t_df = pd.DataFrame(team_metrics)
        
        forecast = {
            "averageCapacity": float(eng_df['availableHours'].sum() * 2),
            "averageVelocity": float(eng_df['historicalVelocity'].sum()),
            "forecastRisk": "High" if float(eng_df['utilization'].mean()) > 90 else "Low"
        }
        
        return {
            "organization": {
                "name": dataset.organization.name,
                "totalEngineers": int(len(dataset.engineers)),
                "deliveryManagers": int(len(dataset.deliveryManagers)),
                "teams": int(len(dataset.teams)),
                "activeJiraIssues": int(len(issues_df[~issues_df['status'].isin(['Done', 'Released'])])),
                "activeSprints": 1,
                "overallUtilization": float(eng_df['utilization'].mean()),
                "overallProductivity": float(eng_df['productivity'].sum()),
                "overallEstimationAccuracy": float(eng_df['estimationAccuracy'].mean()),
                "overallTeamHealth": float(t_df['healthScore'].mean()),
                "burnoutRiskCount": int(len(eng_df[eng_df['burnoutRisk'] == "High"])),
                "idleEngineers": int(len(eng_df[eng_df['utilization'] < 60])),
                "criticalJiraIssues": int(len(issues_df[issues_df['priority'] == 'Critical'])),
                "blockedIssues": int(len(issues_df[issues_df['status'] == 'Blocked'])),
                "dependencyRisks": int(len(single_points_of_failure))
            },
            "teams": team_metrics,
            "engineers": eng_metrics,
            "issues": [i.model_dump() for i in dataset.issues],
            "skills_spof": single_points_of_failure,
            "forecast": forecast
        }
