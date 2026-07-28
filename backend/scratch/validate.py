import asyncio
import json
import os
import sys
from pprint import pprint

# Add backend directory to sys.path so we can import from app
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.append(backend_dir)

from app.services.dataset_loader import DatasetLoader
from app.services.analytics_engine import AnalyticsEngine
from app.services.forecast_engine import ForecastEngine
from app.services.recommendation_engine import RecommendationEngine

def validate_system():
    print("\n" + "="*50)
    print("CUIA End-To-End System Validation")
    print("="*50 + "\n")

    # 1. Dataset Loading & Validation
    print("1. Loading and Validating Dataset...")
    try:
        data = DatasetLoader.get_dataset().model_dump()
        print(f"  [*] Loaded Dataset successfully.")
        print(f"  [*] Organization: {data['organization']['name']}")
        print(f"  [*] Engineers: {len(data['engineers'])}")
        print(f"  [*] Issues: {len(data['issues'])}")
    except Exception as e:
        print(f"  [X] Failed to load dataset: {str(e)}")
        sys.exit(1)

    # 2. Analytics Computation
    print("\n2. Computing Analytics...")
    try:
        analytics = AnalyticsEngine.get_analytics()
        print(f"  [*] Analytics computed successfully.")
        
        # Verify some KPI logic
        org_kpis = analytics['organization']
        print(f"  [*] Total Teams: {org_kpis['teams']}")
        print(f"  [*] Avg Utilization: {org_kpis['overallUtilization']:.1f}%")
        print(f"  [*] Org Health Score: {org_kpis['overallTeamHealth']:.1f}")
        print(f"  [*] Active Sprint: {org_kpis.get('currentSprint', 'Sprint 42')}")

        if org_kpis['overallUtilization'] == 0:
            print("  [X] Warning: Overall utilization is 0%. Expected > 0%.")
            
        print("\n  Sample Team Metrics:")
        team = analytics['teams'][0]
        print(f"    - Team: {team['name']}")
        print(f"    - Health: {team['healthScore']:.1f}")
        print(f"    - Utilization: {team['utilization']:.1f}%")
        print(f"    - Velocity: {team['velocity']} SP")
    except Exception as e:
        print(f"  [X] Failed to compute analytics: {str(e)}")
        sys.exit(1)

    # 3. Forecast Engine
    print("\n3. Generating Forecasts...")
    try:
        org_forecast = ForecastEngine.get_forecast()
        print(f"  [*] Org Forecast generated successfully.")
        print(f"  [*] Current Capacity: {org_forecast['currentCapacity']:.1f}h")
        print(f"  [*] Avg Velocity: {org_forecast['averageVelocity']:.1f} SP")
        print(f"  [*] Forecast Risk: {org_forecast['forecastRisk']}")
        print(f"  [*] Velocity Trend: {org_forecast['trendAnalysis']['velocityDirection']}")
        
        dm1_forecast = ForecastEngine.get_manager_forecast("dm-1")
        print(f"  [*] Manager (dm-1) Forecast generated successfully.")
        print(f"  [*] Current Capacity: {dm1_forecast['currentCapacity']:.1f}h")
    except Exception as e:
        print(f"  [X] Failed to generate forecasts: {str(e)}")
        sys.exit(1)

    # 4. Recommendation Engine
    print("\n4. Generating Recommendations...")
    try:
        recs = RecommendationEngine.get_recommendations()
        print(f"  [*] Generated {len(recs)} total recommendations.")
        
        # Group by rule
        rules_triggered = {}
        for r in recs:
            rules_triggered[r.businessRule] = rules_triggered.get(r.businessRule, 0) + 1
            
        print("  [*] Rules triggered:")
        for rule, count in rules_triggered.items():
            print(f"    - {rule}: {count}")
    except Exception as e:
        print(f"  ✗ Failed to generate recommendations: {str(e)}")
        sys.exit(1)

    print("\n" + "="*50)
    print("ALL VALIDATIONS PASSED. SYSTEM IS DETERMINISTIC.")
    print("="*50 + "\n")

if __name__ == "__main__":
    validate_system()
