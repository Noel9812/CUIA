import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.ai.graph import CopilotGraph

graph = CopilotGraph()

def run_chat(question, persona="leadership", context=None):
    response, new_ctx = graph.chat(question, persona=persona, conversation_context=context)
    return {"answer": response, "conversation_context": new_ctx}

class TestCopilotHarness:

    def test_basic_capability(self):
        # A: Basic capability
        res = run_chat("What can you help me with?")
        assert res["conversation_context"]["previous_intent"] == "capability"
        assert "utilization" in res["answer"].lower()

    def test_team_analytics(self):
        # B: Team Analytics
        res = run_chat("What is Team Alpha's utilization?")
        assert res["conversation_context"]["previous_intent"] == "analytics"
        assert "t-1" in res["conversation_context"]["previous_entities"]["team_ids"]

    def test_engineer_analytics(self):
        # C: Engineer Analytics
        res = run_chat("Show me the utilization for Charlie.")
        assert res["conversation_context"]["previous_intent"] == "analytics"
        assert "eng-1" in res["conversation_context"]["previous_entities"]["engineer_ids"]

    def test_comparisons(self):
        # D: Comparisons
        res = run_chat("Compare Team Alpha and Team Beta.")
        assert res["conversation_context"]["previous_intent"] == "analytics"
        entities = res["conversation_context"]["previous_entities"]["team_ids"]
        assert "t-1" in entities and "t-2" in entities

    def test_recommendations(self):
        # E: Recommendations
        res = run_chat("What do you recommend to fix utilization?")
        assert res["conversation_context"]["previous_intent"] == "recommendation"

    def test_what_if(self):
        # F: What-If
        res = run_chat("What happens if Charlie goes on leave?")
        assert res["conversation_context"]["previous_intent"] == "whatif"
        assert "eng-1" in res["conversation_context"]["previous_entities"]["engineer_ids"]

    def test_conversational_follow_up(self):
        # G: Follow-up
        res1 = run_chat("What is Team Alpha's utilization?")
        assert res1["conversation_context"]["previous_intent"] == "analytics"
        
        ctx = res1["conversation_context"]
        res2 = run_chat("Why?", context=ctx)
        # Should inherit intent and entities
        assert res2["conversation_context"]["previous_intent"] == "analytics"
        assert "t-1" in res2["conversation_context"]["previous_entities"]["team_ids"]

    def test_out_of_scope(self):
        # J: Out of scope
        res = run_chat("What's the weather?")
        # It should fallback to LLM and evaluate to out_of_scope
        assert res["conversation_context"]["previous_intent"] == "out_of_scope"
        assert "workforce" in res["answer"].lower() or "not with that request" in res["answer"].lower() or "error" in res["answer"].lower()

    def test_persona_isolation(self):
        # dm-2 shouldn't see Charlie (eng-1) from Team Alpha (t-1)
        res = run_chat("What is Charlie's utilization?", persona="dm-2")
        # Even if intent is analytics, the context builder should restrict data
        assert res["conversation_context"]["previous_intent"] == "analytics"

    def test_typo_tolerance(self):
        # I: Typo tolerance
        res = run_chat("What is Team Alpha's utiliztion?")
        assert res["conversation_context"]["previous_intent"] == "analytics"

