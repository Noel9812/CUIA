from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.ai.prompts import INTENT_CLASSIFIER_PROMPT, LLM_EXPLAINER_PROMPT, OUTPUT_VALIDATOR_PROMPT
from app.services.analytics_engine import AnalyticsEngine
from app.services.recommendation_engine import RecommendationEngine
import json
import os

class AgentState(TypedDict):
    question: str
    persona: str
    intent: Optional[str]
    raw_tool_data: Optional[dict]
    scoped_context: Optional[str]
    response: Optional[str]
    valid: Optional[bool]

class CopilotGraph:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, max_retries=0) if api_key else None
        
        # Build LangGraph
        workflow = StateGraph(AgentState)
        
        workflow.add_node("scope_resolver", self.scope_resolver)
        workflow.add_node("intent_classifier", self.intent_classifier)
        workflow.add_node("analytics_tool", self.analytics_tool)
        workflow.add_node("forecast_tool", self.forecast_tool)
        workflow.add_node("recommendation_tool", self.recommendation_tool)
        workflow.add_node("whatif_tool", self.whatif_tool)
        workflow.add_node("reporting_tool", self.reporting_tool)
        workflow.add_node("context_builder", self.context_builder)
        workflow.add_node("llm_explainer", self.llm_explainer)
        workflow.add_node("output_validator", self.output_validator)
        
        workflow.set_entry_point("scope_resolver")
        workflow.add_edge("scope_resolver", "intent_classifier")
        
        workflow.add_conditional_edges(
            "intent_classifier",
            self.tool_router,
            {
                "analytics": "analytics_tool",
                "forecast": "forecast_tool",
                "recommendation": "recommendation_tool",
                "whatif": "whatif_tool",
                "reporting": "reporting_tool",
                "malicious": END,
                "unknown": "analytics_tool" # fallback
            }
        )
        
        workflow.add_edge("analytics_tool", "context_builder")
        workflow.add_edge("forecast_tool", "context_builder")
        workflow.add_edge("recommendation_tool", "context_builder")
        workflow.add_edge("whatif_tool", "context_builder")
        workflow.add_edge("reporting_tool", "context_builder")
        
        workflow.add_edge("context_builder", "llm_explainer")
        workflow.add_edge("llm_explainer", "output_validator")
        
        workflow.add_conditional_edges(
            "output_validator",
            self.validation_router,
            {
                "VALID": END,
                "INVALID": "llm_explainer"
            }
        )
        
        self.app = workflow.compile()

    def scope_resolver(self, state: AgentState):
        return state # Persona is already in state, just pass through

    def extract_text(self, content):
        if isinstance(content, list):
            return " ".join([str(c.get("text", "")) for c in content if isinstance(c, dict) and "text" in c])
        return str(content)

    def intent_classifier(self, state: AgentState):
        if not self.llm: return {"intent": "analytics"}
        messages = [
            SystemMessage(content=INTENT_CLASSIFIER_PROMPT),
            HumanMessage(content=state["question"])
        ]
        raw_content = self.llm.invoke(messages).content
        response = self.extract_text(raw_content).strip().lower()
        if response not in ["analytics", "forecast", "recommendation", "whatif", "reporting", "malicious", "unknown"]:
            response = "analytics" # Default fallback
        if response == "malicious":
            return {"intent": "malicious", "response": "I cannot fulfill this request due to security constraints."}
        return {"intent": response}

    def tool_router(self, state: AgentState):
        return state["intent"]

    def analytics_tool(self, state: AgentState):
        return {"raw_tool_data": {"type": "analytics", "data": AnalyticsEngine.get_analytics()}}

    def forecast_tool(self, state: AgentState):
        # Forecast comes directly from deterministic engine
        return {"raw_tool_data": {"type": "forecast", "data": AnalyticsEngine.get_analytics()["forecast"]}}

    def recommendation_tool(self, state: AgentState):
        return {"raw_tool_data": {"type": "recommendation", "data": [r.model_dump() for r in RecommendationEngine.get_recommendations()]}}

    def whatif_tool(self, state: AgentState):
        # Deterministic What-if Engine does not exist yet. Document limitations.
        return {"raw_tool_data": {"type": "whatif", "data": "What-if simulation engine is currently unavailable in the Proof of Concept phase."}}

    def reporting_tool(self, state: AgentState):
        return {"raw_tool_data": {"type": "reporting", "data": "Reports can be downloaded from the Reports module (Daily, Weekly, Monthly)."}}

    def context_builder(self, state: AgentState):
        persona = state["persona"]
        raw_data = state["raw_tool_data"]
        
        if raw_data["type"] == "whatif" or raw_data["type"] == "reporting":
            return {"scoped_context": json.dumps(raw_data["data"])}

        # Apply Scope Isolation
        analytics = AnalyticsEngine.get_analytics()
        if raw_data["type"] == "recommendation":
            all_recs = raw_data["data"]
            if persona == "leadership":
                scoped = [r for r in all_recs if "teamId" in r["supportingMetrics"]]
            else:
                teams = [t for t in analytics["teams"] if t["managerId"] == persona]
                team_ids = [t["id"] for t in teams]
                engineers = [e for e in analytics["engineers"] if e["teamId"] in team_ids]
                scoped = [r for r in all_recs if r["supportingMetrics"].get("teamId") in team_ids or r["supportingMetrics"].get("engineerId") in [e["id"] for e in engineers]]
            return {"scoped_context": json.dumps({"scoped_recommendations": scoped}, indent=2)}
            
        elif raw_data["type"] == "forecast":
            # Forecast is org-wide or team-specific based on scope.
            # But the analytics engine forecast object is currently org-wide only.
            # For POC, if DM, restrict to their teams.
            if persona != "leadership":
                teams = [t for t in analytics["teams"] if t["managerId"] == persona]
                team_ids = [t["id"] for t in teams]
                engineers = [e for e in analytics["engineers"] if e["teamId"] in team_ids]
                fc_cap = sum(e["availableHours"] * 2 for e in engineers)
                fc_dem = sum(e.get("historicalVelocity", e.get("velocity", 0)) for e in engineers)
                scoped = {"forecast": {"averageCapacity": fc_cap, "averageVelocity": fc_dem, "forecastRisk": "High" if (sum(e["utilization"] for e in engineers)/max(1, len(engineers)) > 90) else "Low"}}
            else:
                scoped = raw_data["data"]
            return {"scoped_context": json.dumps(scoped, indent=2)}
            
        else: # analytics
            # Token Optimization: Strip unnecessary arrays from engineers
            def optimize_engineer(e):
                return {
                    "id": e["id"],
                    "name": e["name"],
                    "teamId": e["teamId"],
                    "role": e["role"],
                    "utilization": e["utilization"],
                    "productivity": e["productivity"],
                    "healthScore": e.get("healthScore"),
                    "burnoutRisk": e.get("burnoutRisk"),
                    "criticalIssues": e.get("criticalIssues"),
                    "blockedTickets": e.get("blockedTickets"),
                    "velocity": e.get("velocity")
                }
                
            if persona == "leadership":
                context_org = analytics['organization']
                context_teams = analytics['teams']
                context_engineers = [optimize_engineer(e) for e in analytics['engineers']]
            else:
                context_teams = [t for t in analytics["teams"] if t["managerId"] == persona]
                team_ids = [t["id"] for t in context_teams]
                context_engineers = [optimize_engineer(e) for e in analytics["engineers"] if e["teamId"] in team_ids]
                context_org = {"error": "Not available in Delivery Manager scope."}
                
            return {"scoped_context": json.dumps({
                "organization": context_org,
                "teams": context_teams,
                "engineers": context_engineers
            })}

    def llm_explainer(self, state: AgentState):
        if not self.llm: return {"response": "Error: GEMINI_API_KEY is not configured."}
        if state.get("intent") == "malicious": return state
        
        messages = [
            SystemMessage(content=LLM_EXPLAINER_PROMPT + "\n\n" + state["scoped_context"]),
            HumanMessage(content=state["question"])
        ]
        raw_content = self.llm.invoke(messages).content
        response = self.extract_text(raw_content)
        return {"response": response}

    def output_validator(self, state: AgentState):
        if not self.llm or state.get("intent") == "malicious": return {"valid": True} # skip validation if malicious or no LLM
        
        validation_prompt = f"{OUTPUT_VALIDATOR_PROMPT}\n\nUser Question: {state['question']}\nContext: {state['scoped_context']}\nAssistant Response: {state['response']}"
        raw_content = self.llm.invoke([HumanMessage(content=validation_prompt)]).content
        response = self.extract_text(raw_content).strip().upper()
        
        # If it hallucinates twice in a row, we just return a safe canned response.
        if "INVALID" in response and getattr(self, '_retry', False):
             return {"valid": True, "response": "I do not have sufficient data within your current scope to answer that securely."}
        
        if "INVALID" in response:
             self._retry = True
             return {"valid": False}
             
        self._retry = False
        return {"valid": True}
        
    def validation_router(self, state: AgentState):
        return "VALID" if state["valid"] else "INVALID"

    def chat(self, question: str, persona: str = "leadership") -> str:
        if not self.llm:
            return "Error: GEMINI_API_KEY is not configured."
            
        initial_state = {"question": question, "persona": persona}
        try:
            result = self.app.invoke(initial_state)
            return result["response"]
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"
