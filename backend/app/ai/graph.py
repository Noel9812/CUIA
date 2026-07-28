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

        # Step 2: Weighted keyword classification
        intent, score, needs_llm = classify_intent(question)

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
                    intent = intent if intent != "unknown" else "analytics"
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
                    intent = "analytics"

        elif intent == "unknown":
            # No LLM available and no keyword match
            intent = "analytics"
            logger.info("Intent defaulted to analytics (no LLM available).")

        logger.info(
            "Intent resolved: %s (score=%.1f, llm_used=%s, entities=%s)",
            intent, score, needs_llm and self.bedrock.is_available,
            bool(entities.has_any())
        )

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

        if state.get("intent") == "malicious":
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

    def chat(self, question: str, persona: str = "leadership") -> str:
        """
        Main chat entry point.

        Args:
            question: The user's natural language question.
            persona: "leadership" or a delivery manager ID (e.g., "dm-1").

        Returns:
            Natural language response from the AI.
        """
        if not self.bedrock.is_available:
            return "Error: AI service is not available. Check AWS Bedrock configuration."

        start = time.monotonic()
        initial_state = {"question": question, "persona": persona}

        try:
            result = self.app.invoke(initial_state)
            latency_ms = int((time.monotonic() - start) * 1000)

            logger.info(
                "Chat complete: persona=%s, intent=%s, latency=%dms",
                persona, result.get("intent", "unknown"), latency_ms
            )

            return result.get("response", "I was unable to generate a response.")

        except Exception as e:
            logger.error("Chat error: %s", str(e))
            return f"Error communicating with AI: {str(e)}"
