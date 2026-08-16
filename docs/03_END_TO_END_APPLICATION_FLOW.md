# 3. End-to-End Application Flow

This document traces how data flows through CUIA, detailing the journey of a natural language query through the Copilot and a standard Dashboard request.

## Flow 1: AI Copilot Request

**Example User Query:** _"Why is Team Alpha's health score so low?"_ (Logged in as `leadership`)

### 1. Frontend Request
The user types the question into the Copilot chat.
The React app sends a POST request to `/api/copilot/chat`:
```json
{
  "question": "Why is Team Alpha's health score so low?",
  "persona": "leadership",
  "conversation_context": {}
}
```

### 2. FastAPI Entry
The `copilot.py` router receives the request, verifies the AI service health, and invokes the `CopilotGraph` orchestrator (`graph.chat()`).

### 3. LangGraph Orchestration: Intent & Entities
The `AgentState` is initialized.
The graph's first node, `intent_classifier`, runs:
- **Entity Extraction:** `EntityExtractor.extract()` analyzes the string and identifies `team_ids = {"team-alpha"}` using string matching against the dataset. (No LLM).
- **Intent Classification:** The keyword "health score" hits the `ANALYTICS_KEYWORDS` list with a strong weight. The intent is deterministically classified as `analytics`. (No LLM).

### 4. LangGraph Orchestration: Context Building
The graph routes the state to the `analytics_tool` node.
- The `ContextBuilder.build_analytics_context()` is called.
- It sees the persona is `leadership` (full access) and the entity is `team-alpha`.
- It fetches the pre-computed analytics from the `AnalyticsEngine`.
- It filters the data to **only include Team Alpha's details**, heavily compressing the JSON to save tokens.

### 5. LLM Explanation
The graph routes to the `llm_explainer` node.
- It combines the `LLM_EXPLAINER_PROMPT`, the minimized JSON context for Team Alpha, and the user's original question.
- It sends this single prompt to AWS Bedrock via `BedrockClient`.

### 6. Response Construction
- Bedrock returns a natural language explanation (e.g., "Team Alpha's health score is low primarily because they have 3 critical issues and a burnout risk for two engineers...").
- The graph returns the response and the updated `conversation_context` (saving the intent and entities for follow-ups).
- FastAPI returns the JSON to the React frontend, which renders it in the chat window.

## Flow 2: Dashboard API Request

**Example Action:** Delivery Manager `dm-1` loads their dashboard.

### 1. Frontend Request
The React app mounts the `DeliveryDashboard` component and calls `GET /api/dashboard/delivery?managerId=dm-1`.

### 2. FastAPI & Analytics Engine
The `dashboard.py` router receives the request.
- It calls `AnalyticsEngine.get_analytics()`. (This engine caches computations on startup).
- The router explicitly filters the returned analytics, selecting only teams where `managerId == "dm-1"`.
- It also filters engineers to only those belonging to `dm-1`'s teams.

### 3. Response
The highly structured, deterministic JSON is returned to the frontend. No AI is involved. The frontend renders the utilization gauges, health charts, and critical issue lists.

## Conversational Context Inheritance (Follow-up)

**Query 1:** _"What is Team Alpha's utilization?"_
- Intent: `analytics`
- Entity: `team-alpha`
- Context saved: `{previous_intent: "analytics", previous_entities: {team_ids: ["team-alpha"]}}`

**Query 2:** _"Why is it so low?"_
- Frontend sends Query 2 + previous context.
- `intent_classifier` sees "why" and detects an explicit conversational follow-up.
- It automatically inherits `intent="analytics"` and `team-alpha` from the previous context.
- Flow continues exactly as above, providing a seamless conversational experience without losing context or requiring the LLM to manage conversational memory natively.
