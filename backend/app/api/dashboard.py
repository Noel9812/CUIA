from fastapi import APIRouter
from app.services.analytics_engine import AnalyticsEngine
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()

@router.get("/dashboard/leadership")
def get_leadership_dashboard():
    analytics = AnalyticsEngine.get_analytics()
    recs = RecommendationEngine.get_recommendations()
    
    # Calculate Org-wide historical trends
    engineers = analytics["engineers"]
    total_avg_cap = sum(e["availableHours"] * 2 for e in engineers)
    total_logged = sum(e["loggedHours"] for e in engineers)
    total_historical_vel = sum(e.get("historicalVelocity", e.get("velocity", 0)) for e in engineers)
    
    historical_trends = [
        {"sprint": "Sprint 37", "capacity": total_avg_cap * 1.05, "utilization": total_avg_cap * 0.95, "productivity": 85},
        {"sprint": "Sprint 38", "capacity": total_avg_cap * 1.02, "utilization": total_avg_cap * 0.90, "productivity": 88},
        {"sprint": "Sprint 39", "capacity": total_avg_cap * 0.98, "utilization": total_avg_cap * 0.96, "productivity": 92},
        {"sprint": "Sprint 40", "capacity": total_avg_cap, "utilization": total_avg_cap * 0.98, "productivity": 90},
        {"sprint": "Sprint 41", "capacity": total_avg_cap * 1.01, "utilization": total_avg_cap * 0.94, "productivity": 87},
        {"sprint": "Sprint 42", "capacity": total_avg_cap, "utilization": total_logged, "productivity": analytics["organization"]["overallProductivity"]}
    ]
    
    return {
        "kpis": analytics["organization"],
        "historicalTrends": historical_trends,
        "teams": analytics["teams"],
        "recommendations": [r.model_dump() for r in recs if "teamId" in r.supportingMetrics]
    }

@router.get("/dashboard/delivery")
def get_delivery_dashboard(managerId: str):
    analytics = AnalyticsEngine.get_analytics()
    teams = [t for t in analytics["teams"] if t["managerId"] == managerId]
    team_ids = [t["id"] for t in teams]
    engineers = [e for e in analytics["engineers"] if e["teamId"] in team_ids]
    issues = [i for i in analytics["issues"] if i["assignee"] in [e["id"] for e in engineers]]
    
    recs = RecommendationEngine.get_recommendations()
    filtered_recs = [r.model_dump() for r in recs if r.supportingMetrics.get("teamId") in team_ids or r.supportingMetrics.get("engineerId") in [e["id"] for e in engineers]]
    
    # Calculate delivery manager specific KPIs
    total_sp = sum(e["storyPoints"] for e in engineers)
    total_velocity = sum(e["velocity"] for e in engineers)
    total_historical_velocity = sum(e.get("historicalVelocity", e["velocity"]) for e in engineers)
    
    dm_kpis = {
        "healthScore": sum(t["healthScore"] for t in teams) / max(1, len(teams)),
        "utilization": sum(e["utilization"] for e in engineers) / max(1, len(engineers)),
        "remainingCapacity": sum(e["availableHours"] * 2 for e in engineers) - sum(e["loggedHours"] for e in engineers),
        "forecastCapacityGap": sum(e["availableHours"] * 2 for e in engineers) - total_historical_velocity, 
        "burnoutRiskCount": sum(1 for e in engineers if e["burnoutRisk"] == "High"),
        "dependencyRisks": sum(t["dependencyRisk"] for t in teams),
        "productivity": sum(e["productivity"] for e in engineers),
        "velocity": total_velocity,
        "storyPoints": total_sp,
        "sprintCompletion": 85, # Mock percentage
        "estimationAccuracy": sum(e["estimationAccuracy"] for e in engineers) / max(1, len(engineers)),
        "averageResolutionTime": sum(e["averageResolutionTime"] for e in engineers) / max(1, len([e for e in engineers if e["averageResolutionTime"] > 0])),
        "criticalIssues": sum(e["criticalIssues"] for e in engineers),
        "blockedIssues": sum(e["blockedTickets"] for e in engineers)
    }
    
    # Forecast aligned with TDD
    dm_forecast = {
        "averageCapacity": sum(e["availableHours"] * 2 for e in engineers),
        "averageVelocity": total_historical_velocity,
        "forecastDemand": total_historical_velocity,
        "forecastRisk": "High" if dm_kpis["utilization"] > 90 else "Balanced"
    }
    
    # Mock historical trends for the last 6 sprints for the Capacity vs Utilization line graph
    historical_trends = [
        {"sprint": "Sprint 37", "capacity": dm_forecast["averageCapacity"] * 1.05, "utilization": dm_forecast["averageCapacity"] * 0.95},
        {"sprint": "Sprint 38", "capacity": dm_forecast["averageCapacity"] * 1.02, "utilization": dm_forecast["averageCapacity"] * 0.90},
        {"sprint": "Sprint 39", "capacity": dm_forecast["averageCapacity"] * 0.98, "utilization": dm_forecast["averageCapacity"] * 0.96},
        {"sprint": "Sprint 40", "capacity": dm_forecast["averageCapacity"], "utilization": dm_forecast["averageCapacity"] * 0.98},
        {"sprint": "Sprint 41", "capacity": dm_forecast["averageCapacity"] * 1.01, "utilization": dm_forecast["averageCapacity"] * 0.94},
        {"sprint": "Sprint 42", "capacity": dm_forecast["averageCapacity"], "utilization": sum(e["loggedHours"] for e in engineers)}
    ]
    
    return {
        "kpis": dm_kpis,
        "forecast": dm_forecast,
        "historicalTrends": historical_trends,
        "teams": teams,
        "engineers": engineers,
        "recommendations": filtered_recs,
        "issues": issues
    }

@router.get("/dashboard/team/{teamId}")
def get_team_details(teamId: str):
    analytics = AnalyticsEngine.get_analytics()
    team = next((t for t in analytics["teams"] if t["id"] == teamId), None)
    engineers = [e for e in analytics["engineers"] if e["teamId"] == teamId]
    issues = [i for i in analytics["issues"] if i["assignee"] in [e["id"] for e in engineers]]
    recs = RecommendationEngine.get_recommendations()
    filtered_recs = [r.model_dump() for r in recs if r.supportingMetrics.get("teamId") == teamId or r.supportingMetrics.get("engineerId") in [e["id"] for e in engineers]]
    
    # Calculate skills list from engineers
    skills_map = {}
    for e in engineers:
        for s in e["primarySkills"]:
            if s not in skills_map:
                skills_map[s] = {"technology": s, "coverage": 0, "owner": e["name"], "risk": "Low", "candidate": "None"}
            skills_map[s]["coverage"] += 1
            
    for k, v in skills_map.items():
        if v["coverage"] == 1:
            v["risk"] = "Critical"
            
            # Deterministic Algorithm for Cross-Training
            # Query engineers on the team with the bottlenecked skill as a secondarySkill
            # Filter out engineers with Current Sprint Utilization > 80%
            candidates = [
                cand for cand in engineers
                if k in cand["secondarySkills"] and cand["utilization"] <= 80
            ]
            
            if candidates:
                # Rank by experience (as a proxy for Skill Level since we don't have explicit skill levels in dataset)
                candidates.sort(key=lambda x: x["experience"], reverse=True)
                # Output top candidate
                v["candidate"] = candidates[0]["name"]
                
    skills = list(skills_map.values())
    
    total_historical_velocity = sum(e.get("historicalVelocity", e["velocity"]) for e in engineers)
    team_forecast = {
        "averageCapacity": sum(e["availableHours"] * 2 for e in engineers),
        "averageVelocity": total_historical_velocity,
        "forecastDemand": total_historical_velocity,
        "forecastRisk": "High" if team and team["utilization"] > 90 else "Balanced"
    }
    
    return {
        "team": team,
        "engineers": engineers,
        "issues": issues,
        "recommendations": filtered_recs,
        "forecast": team_forecast,
        "skills": skills
    }

@router.get("/dashboard/engineer/{engineerId}")
def get_engineer_details(engineerId: str):
    analytics = AnalyticsEngine.get_analytics()
    engineer = next((e for e in analytics["engineers"] if e["id"] == engineerId), None)
    issues = [i for i in analytics["issues"] if i["assignee"] == engineerId]
    recs = RecommendationEngine.get_recommendations()
    filtered_recs = [r.model_dump() for r in recs if r.supportingMetrics.get("engineerId") == engineerId]
    
    return {
        "engineer": engineer,
        "issues": issues,
        "recommendations": filtered_recs
    }
