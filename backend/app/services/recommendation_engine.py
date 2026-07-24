from app.services.analytics_engine import AnalyticsEngine
from app.models.schemas import Recommendation
from typing import List

class RecommendationEngine:
    
    @classmethod
    def get_recommendations(cls) -> List[Recommendation]:
        analytics = AnalyticsEngine.get_analytics()
        recs = []
        
        for eng in analytics.get("engineers", []):
            if eng.get("utilization", 0) > 100:
                recs.append(Recommendation(
                    severity="Critical",
                    businessRule="Utilization > 100%",
                    reason=f"{eng['name']} has logged {eng['loggedHours']} hours against {eng['availableHours']} available effective hours.",
                    businessImpact="High risk of burnout and delayed delivery.",
                    supportingMetrics={"engineerId": eng['id'], "utilization": eng['utilization'], "criticalIssues": eng['criticalIssues']},
                    suggestedAction=f"Redistribute high priority issues from {eng['name']} to engineers with lower utilization.",
                    expectedOutcome=f"Utilization reduces to below 100%, mitigating burnout risk.",
                    confidence="High",
                    sourceAnalytics="Module 1 - Utilization Analysis"
                ))
            elif eng.get("utilization", 0) < 60:
                recs.append(Recommendation(
                    severity="Low",
                    businessRule="Utilization < 60%",
                    reason=f"{eng['name']} has low utilization.",
                    businessImpact="Wasted capacity and lower team throughput.",
                    supportingMetrics={"engineerId": eng['id'], "utilization": eng['utilization']},
                    suggestedAction=f"Assign additional tasks to {eng['name']}.",
                    expectedOutcome="Improve team velocity and throughput.",
                    confidence="Medium",
                    sourceAnalytics="Module 1 - Utilization Analysis"
                ))
                
            if eng.get("estimationAccuracy", 100) < 70:
                recs.append(Recommendation(
                    severity="Medium",
                    businessRule="Estimation Accuracy < 70%",
                    reason=f"{eng['name']} has chronic under/over estimation.",
                    businessImpact="Reduces predictability of sprint completion.",
                    supportingMetrics={"engineerId": eng['id'], "accuracy": eng['estimationAccuracy']},
                    suggestedAction="Conduct estimation review session.",
                    expectedOutcome="Improve sprint planning reliability.",
                    confidence="High",
                    sourceAnalytics="Module 4 - Estimation Accuracy Analysis"
                ))
                
            for skill in eng.get("primarySkills", []):
                if skill in analytics.get("skills_spof", []):
                    recs.append(Recommendation(
                        severity="High",
                        businessRule="Single Point of Failure (Skill)",
                        reason=f"{eng['name']} is the only engineer with skill: {skill}.",
                        businessImpact="If this engineer takes leave, work requiring this skill will be completely blocked.",
                        supportingMetrics={"engineerId": eng['id'], "skill": skill, "coverage": 1},
                        suggestedAction=f"Cross-train another engineer on {skill}.",
                        expectedOutcome="Reduce dependency risk from High to Moderate.",
                        confidence="High",
                        sourceAnalytics="Module 6 - Skill Risk Analysis"
                    ))
                
        for team in analytics.get("teams", []):
            if team.get("healthScore", 100) < 70:
                recs.append(Recommendation(
                    severity="High",
                    businessRule="Team Health < 70%",
                    reason=f"Team {team['name']} is unhealthy due to high critical bugs or overload.",
                    businessImpact="Severe risk to sprint delivery and morale.",
                    supportingMetrics={"teamId": team['id'], "health": team['healthScore']},
                    suggestedAction=f"Manager intervention for Team {team['name']}.",
                    expectedOutcome="Prevent attrition and stabilize delivery.",
                    confidence="Medium",
                    sourceAnalytics="Module 2 - Workload Analysis"
                ))
                
        return recs
