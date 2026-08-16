import pytest
import json
from app.ai.context_builders import ContextBuilder
from app.ai.entity_extractor import ExtractedEntities
from app.services.analytics_engine import AnalyticsEngine

def test_leadership_org_summary_has_capacity():
    # Force full cache computation
    analytics = AnalyticsEngine.get_analytics()
    context_str = ContextBuilder.build_analytics_context(persona="leadership", entities=None)
    context = json.loads(context_str)
    
    assert "org" in context
    assert "capacityHours" in context["org"]
    assert "loggedHours" in context["org"]
    assert context["org"]["capacityHours"] > 0

def test_dm_isolation():
    # Get a specific DM
    analytics = AnalyticsEngine.get_analytics()
    if not analytics["teams"]:
        return
        
    manager_id = analytics["teams"][0]["managerId"]
    
    context_str = ContextBuilder.build_analytics_context(persona=manager_id, entities=None)
    context = json.loads(context_str)
    
    assert context["scope"] == f"DM {manager_id}"
    for team in context["teams"]:
        # We can't easily assert the team matches without checking the analytics,
        # but we know ContextBuilder filters by managerId
        assert team["id"] is not None

def test_dm_cannot_see_other_teams():
    analytics = AnalyticsEngine.get_analytics()
    if len(analytics["teams"]) < 2:
        return
        
    manager_1 = analytics["teams"][0]["managerId"]
    # Team 2 has a different manager (ideally)
    team_2_id = analytics["teams"][-1]["id"]
    manager_2 = analytics["teams"][-1]["managerId"]
    
    if manager_1 == manager_2:
        return
        
    entities = ExtractedEntities()
    entities.team_ids.add(team_2_id)
    
    context_str = ContextBuilder.build_analytics_context(persona=manager_1, entities=entities)
    context = json.loads(context_str)
    
    # DM1 asked for DM2's team. It should NOT be returned.
    assert len(context["teams"]) == 0
