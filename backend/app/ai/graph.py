"""
LangGraph AI Copilot — hardened, token-optimized, deterministic-first architecture.

Flow:
  Question → Entity Extraction → Weighted Intent Classification → Context Building → Bedrock → Response

Key design decisions:
- Weighted keyword scoring classifies intent without any model call (~90% of questions)
- Entity extraction narrows context to only relevant data (no LLM)
- Context builders create minimal, question-aware, persona-scoped DTOs
- Only 1-2 model calls max: intent fallback (if needed) + explanation
- AI never computes, forecasts, or recommends — only explains

Improvements over v1:
- Comprehensive intent taxonomy with hundreds of weighted keywords
- Deterministic entity extraction (teams, engineers, sprints, skills, issues)
- Question-aware context building (only send relevant fields)
- Strict persona data isolation (DM never sees other DMs' data)
- Structured logging with intent scores, context size, latency
"""

import logging
import os
import time
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END

from app.ai.prompts import INTENT_CLASSIFIER_PROMPT, LLM_EXPLAINER_PROMPT
from app.ai.context_builders import ContextBuilder
from app.ai.bedrock_client import BedrockClient
from app.ai.intent_classifier import classify_intent, VALID_INTENTS
from app.ai.entity_extractor import EntityExtractor, ExtractedEntities

logger = logging.getLogger("cuia.ai.graph")


# ──────────────────────────────────────────────
# State definition
# ──────────────────────────────────────────────

class AgentState(TypedDict):
    question: str
    persona: str
    intent: Optional[str]
    entities: Optional[dict]      # Serialized ExtractedEntities (for state transport)
    scoped_context: Optional[str]
    response: Optional[str]
    conversation_context: Optional[dict]


class CopilotGraph:
    """
    Token-optimized, hardened LangGraph Copilot.

    Architecture:
    - Deterministic weighted intent classification (0 model calls for ~90% of questions)
    - Deterministic entity extraction (0 model calls)
    - Question-aware context building (0 model calls)
    - Single Bedrock call for explanation (1 model call)
    - Total: 1 model call typical, 2 max (intent fallback + explanation)
    """

    def __init__(self):
        self.bedrock = BedrockClient()
        self.llm = self.bedrock  # Alias for compatibility

        # Build LangGraph workflow
        workflow = StateGraph(AgentState)

        workflow.add_node("intent_classifier", self.intent_classifier)
        workflow.add_node("analytics_tool", self.analytics_tool)
        workflow.add_node("forecast_tool", self.forecast_tool)
        workflow.add_node("recommendation_tool", self.recommendation_tool)
        workflow.add_node("whatif_tool", self.whatif_tool)
        workflow.add_node("reporting_tool", self.reporting_tool)
        workflow.add_node("llm_explainer", self.llm_explainer)

        workflow.set_entry_point("intent_classifier")

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
                "greeting": END,
                "identity": END,
                "capability": END,
                "out_of_scope": END,
                "unknown": END,
            }
        )

        workflow.add_edge("analytics_tool", "llm_explainer")
        workflow.add_edge("forecast_tool", "llm_explainer")
        workflow.add_edge("recommendation_tool", "llm_explainer")
        workflow.add_edge("whatif_tool", "llm_explainer")
        workflow.add_edge("reporting_tool", "llm_explainer")
        workflow.add_edge("llm_explainer", END)

        self.app = workflow.compile()
        logger.info("CopilotGraph initialized with %d tool nodes.", 5)

    # ──────────────────────────────────────────────
    # Intent classification (weighted keyword scoring + LLM fallback)
    # ──────────────────────────────────────────────

    def intent_classifier(self, state: AgentState):
        """
        Classify intent using weighted keyword scoring first.
        Falls back to Bedrock model only when scores are ambiguous.
        Also performs entity extraction for context narrowing.
        """
        question = state["question"]

        # Step 1: Extract entities (always, no LLM)
        entities = EntityExtractor.extract(question)
        
        # Step 1.5: Conversational Follow-up Handling
        conversation_context = state.get("conversation_context") or {}
        previous_intent = conversation_context.get("previous_intent")
        previous_entities = conversation_context.get("previous_entities", {})
        
        # Merge previous entities if not explicitly overridden in current question
        if previous_entities:
            if not entities.team_ids and previous_entities.get("team_ids"):
                entities.team_ids = set(previous_entities["team_ids"])
            if not entities.engineer_ids and previous_entities.get("engineer_ids"):
                entities.engineer_ids = set(previous_entities["engineer_ids"])
            if not entities.sprints and previous_entities.get("sprints"):
                entities.sprints = set(previous_entities["sprints"])
            if not entities.skills and previous_entities.get("skills"):
                entities.skills = set(previous_entities["skills"])

        # Check for explicit 'why' follow-up
        q_clean = question.lower().strip().strip('?!. ')
        if q_clean in ('why', 'why is that', 'explain', 'tell me why', 'how come', 'how') and previous_intent:
            intent = previous_intent
            score = 10.0
            needs_llm = False
            logger.info("Explicit conversational follow-up detected. Inheriting intent: %s", intent)
        else:
            # Step 2: Weighted keyword classification
            intent, score, needs_llm = classify_intent(question)
            
            # Inherit previous intent if current query is ambiguous but introduces new entities (e.g. "What about Team Alpha?")
            if intent == "unknown" and previous_intent and (entities.team_ids or entities.engineer_ids):
                intent = previous_intent
                needs_llm = False
                logger.info("Conversational context inheritance (new entity). Inheriting intent: %s", intent)

        # Handle malicious immediately
        if intent == "malicious":
            logger.warning("Malicious intent blocked (score=%.1f): %s", score, question[:50])
            return {
                "intent": "malicious",
                "entities": entities.to_dict(),
                "response": "I cannot fulfill this request due to security constraints.",
            }

        # Step 3: LLM fallback only when needed
        if needs_llm and self.bedrock.is_available:
            try:
                llm_response = self.bedrock.invoke(
                    INTENT_CLASSIFIER_PROMPT,
                    question,
                    max_tokens=10,
                    temperature=0.0,
                ).strip().lower()

                if llm_response in VALID_INTENTS:
                    intent = llm_response
                    logger.info("Intent classified (LLM fallback): %s", intent)
                else:
                    # LLM returned garbage, use keyword result or default
                    intent = intent if intent != "unknown" else "out_of_scope"
                    logger.warning(
                        "LLM returned invalid intent '%s', using: %s",
                        llm_response, intent
                    )

                if intent == "malicious":
                    return {
                        "intent": "malicious",
                        "entities": entities.to_dict(),
                        "response": "I cannot fulfill this request due to security constraints.",
                    }

            except Exception as e:
                logger.warning(
                    "LLM intent fallback failed: %s. Using keyword result: %s",
                    str(e), intent
                )
                if intent == "unknown":
                    intent = "out_of_scope"

        elif intent == "unknown":
            # No LLM available and no keyword match
            intent = "out_of_scope"
            logger.info("Intent defaulted to out_of_scope (no LLM available).")

        logger.info(
            "Intent resolved: %s (score=%.1f, llm_used=%s, entities=%s)",
            intent, score, needs_llm and self.bedrock.is_available,
            bool(entities.has_any())
        )

        if intent == "greeting":
            return {
                "intent": "greeting",
                "entities": entities.to_dict(),
                "response": "Hello! What would you like to analyze?",
            }
            
        if intent == "identity":
            return {
                "intent": "identity",
                "entities": entities.to_dict(),
                "response": "I'm the CUIA workforce analytics Copilot. I help authorized managers and leadership understand team capacity, utilization, workload, health, performance, and related workforce insights."
            }
            
        if intent == "capability":
            return {
                "intent": "capability",
                "entities": entities.to_dict(),
                "response": "I can help you analyze:\n- utilization and capacity\n- workload and velocity\n- team health and burnout risk\n- blocked work\n- engineer/team performance\n- workforce trends and recommendations\n\nAsk me a question about your authorized workforce data."
            }
            
        if intent == "out_of_scope" or intent == "unknown":
            return {
                "intent": "out_of_scope",
                "entities": entities.to_dict(),
                "response": "I can help with CUIA workforce analytics, but not with that request.",
            }

        return {
            "intent": intent,
            "entities": entities.to_dict(),
        }

    def tool_router(self, state: AgentState):
        """Route to the appropriate tool based on classified intent."""
        return state["intent"]

    # ──────────────────────────────────────────────
    # Tool nodes (context building, no analytics computation)
    # ──────────────────────────────────────────────

    def _restore_entities(self, state: AgentState) -> Optional[ExtractedEntities]:
        """Restore ExtractedEntities from state dict."""
        entities_dict = state.get("entities")
        if not entities_dict:
            return None

        # Re-extract for full object (state only carries the dict summary)
        return EntityExtractor.extract(state["question"])

    def analytics_tool(self, state: AgentState):
        """Build compressed, question-aware analytics context."""
        entities = self._restore_entities(state)
        context = ContextBuilder.build_analytics_context(state["persona"], entities)
        logger.info("Analytics context built: %d chars", len(context))
        return {"scoped_context": context}

    def forecast_tool(self, state: AgentState):
        """Build compressed forecast context."""
        entities = self._restore_entities(state)
        context = ContextBuilder.build_forecast_context(state["persona"], entities)
        logger.info("Forecast context built: %d chars", len(context))
        return {"scoped_context": context}

    def recommendation_tool(self, state: AgentState):
        """Build compressed recommendation context."""
        entities = self._restore_entities(state)
        context = ContextBuilder.build_recommendation_context(state["persona"], entities)
        logger.info("Recommendation context built: %d chars", len(context))
        return {"scoped_context": context}

    def whatif_tool(self, state: AgentState):
        """Build simulation context."""
        entities = self._restore_entities(state)
        context = ContextBuilder.build_simulation_context(entities)
        logger.info("Simulation context built: %d chars", len(context))
        return {"scoped_context": context}

    def reporting_tool(self, state: AgentState):
        """Build reporting context."""
        entities = self._restore_entities(state)
        context = ContextBuilder.build_reporting_context(entities)
        logger.info("Reporting context built: %d chars", len(context))
        return {"scoped_context": context}

    # ──────────────────────────────────────────────
    # LLM explainer (single model call)
    # ──────────────────────────────────────────────

    def llm_explainer(self, state: AgentState):
        """Use Bedrock to explain the deterministic context in natural language."""
        if not self.bedrock.is_available:
            return {
                "response": "Error: AI service is not available. Check AWS Bedrock configuration."
            }

        if state.get("intent") in ("malicious", "greeting", "identity", "capability", "out_of_scope", "unknown"):
            return state

        scoped_context = state.get("scoped_context", "{}")
        system_prompt = LLM_EXPLAINER_PROMPT + "\n\nContext:\n" + scoped_context

        prompt_size = len(system_prompt) + len(state["question"])

        try:
            start = time.monotonic()
            response = self.bedrock.invoke(
                system_prompt,
                state["question"],
            )
            latency_ms = int((time.monotonic() - start) * 1000)

            logger.info(
                "LLM explainer: intent=%s, promptSize=%d, responseSize=%d, latency=%dms",
                state.get("intent", "unknown"), prompt_size,
                len(response), latency_ms
            )
            return {"response": response}

        except Exception as e:
            logger.error("LLM explainer failed: %s", str(e))
            return {
                "response": f"I encountered an error generating the response: {str(e)}"
            }

    # ──────────────────────────────────────────────
    # Public chat interface
    # ──────────────────────────────────────────────

    def chat(self, question: str, persona: str = "leadership", conversation_context: Optional[dict] = None) -> tuple[str, dict]:
        """
        Main chat entry point.

        Args:
            question: The user's natural language question.
            persona: "leadership" or a delivery manager ID (e.g., "dm-1").
            conversation_context: Context from the previous turns.

        Returns:
            Tuple of (response, updated_conversation_context).
        """
        if not self.bedrock.is_available:
            return "Error: AI service is not available. Check AWS Bedrock configuration.", {}

        start = time.monotonic()
        initial_state = {
            "question": question, 
            "persona": persona,
            "conversation_context": conversation_context or {}
        }

        try:
            result = self.app.invoke(initial_state)
            latency_ms = int((time.monotonic() - start) * 1000)

            logger.info(
                "Chat complete: persona=%s, intent=%s, latency=%dms",
                persona, result.get("intent", "unknown"), latency_ms
            )

            # Build new conversation context
            new_ctx = {
                "persona": persona,
                "previous_intent": result.get("intent"),
                "previous_entities": result.get("entities", {})
            }

            return result.get("response", "I was unable to generate a response."), new_ctx

        except Exception as e:
            logger.error("Chat error: %s", str(e))
            return f"Error communicating with AI: {str(e)}", {}
