# 6. AI Copilot

The AI Copilot is the natural language interface for CUIA. It enables authorized users to query the analytics engine securely, without needing to learn complex dashboard filters or SQL.

## Purpose and Scope

- **Supported Queries:** Analytics ("What is Team Alpha's utilization?"), forecasting ("Will we have enough capacity next sprint?"), recommendations ("How can I reduce burnout?"), what-if scenarios ("What if Bob leaves?"), and reporting generation requests.
- **Unsupported Queries:** Out-of-domain knowledge ("What is the weather?"), raw data dumps ("Show me the raw JSON dataset"), or malicious prompt injections.

## The Deterministic AI Philosophy

In CUIA, **the LLM is an explainer, not a calculator.**

Large Language Models are prone to hallucination when performing math on tabular data. Therefore, the architecture strictly enforces:
1. **Deterministic Processing:** Intents and entities are identified using Python code (regex, keywords, string matching).
2. **Deterministic Context:** Python services calculate the requested analytics, forecasts, or simulations, and format them into a tiny JSON string.
3. **Restricted Generation:** The LLM is given a strict system prompt and the JSON string, and is instructed *only* to explain the provided data.

This architecture practically eliminates hallucination and guarantees that if the AI says a team's utilization is 85%, that number comes directly from the math engine.

## File-by-File Breakdown

The AI subsystem lives in `backend/app/ai/`.

| File | Responsibility |
|------|----------------|
| `graph.py` | The LangGraph state machine orchestrator. Wires nodes together. |
| `intent_classifier.py` | Deterministically classifies intents via weighted keywords. Rejects malicious queries. |
| `synonym_engine.py` | Normalizes user queries (e.g., mapping "overworked" to "overutilized") prior to classification. |
| `entity_extractor.py` | Deterministically extracts Teams, Engineers, Sprints, and business concepts (e.g., "busiest", "healthiest"). |
| `context_builders.py` | Dynamically builds the highly compressed JSON payload to inject into the LLM prompt based on the extracted entities and user persona. |
| `bedrock_client.py` | The AWS Bedrock wrapper. Handles the actual `invoke` call to the LLM. |
| `prompts.py` | Stores the system prompts used by the explainer and intent fallback nodes. |

## Conversationality and Follow-ups

The Copilot supports conversational memory. 
When a user asks, *"What is Team Alpha's utilization?"*, the system saves the `intent` ("analytics") and `entities` ("Team Alpha") into a `conversation_context` dict, which the frontend passes back on the next request.

If the user follows up with *"Why is it so low?"*, the system deterministically detects the explicit follow-up pattern (the word "why"), bypasses normal intent classification, inherits the "analytics" intent and "Team Alpha" entity from the context, and answers seamlessly.
