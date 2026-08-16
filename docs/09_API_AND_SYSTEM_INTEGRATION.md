# 9. API and System Integration

The FastAPI backend exposes a set of RESTful endpoints to the React frontend.

## Dashboard APIs

### `GET /api/dashboard/leadership`
- **Purpose:** Retrieves organization-wide KPIs and aggregated data for all teams and engineers.
- **Request Parameters:** None
- **Response:** JSON object containing `organization`, `teams`, `engineers`, `skills_spof`, and `activeSprints`.

### `GET /api/dashboard/delivery?managerId={id}`
- **Purpose:** Retrieves dashboard data scoped exclusively to a specific delivery manager.
- **Request Parameters:** `managerId` (e.g., `dm-1`)
- **Response:** JSON object containing the manager's assigned `teams`, `engineers`, and aggregated metrics for that scope.

### `GET /api/dashboard/team/{team_id}`
- **Purpose:** Deep dive into a single team's metrics and composition.
- **Request Parameters:** Path parameter `team_id`
- **Response:** JSON object for the specific team and its array of engineers.

### `GET /api/dashboard/engineer/{engineer_id}`
- **Purpose:** Deep dive into an individual engineer's metrics, skills, and current/historical issues.
- **Request Parameters:** Path parameter `engineer_id`

## Copilot API

### `POST /api/copilot/chat`
- **Purpose:** Submits a natural language query to the LangGraph AI Copilot.
- **Request Body:**
```json
{
  "question": "What is the organization's utilization?",
  "persona": "leadership",
  "conversation_context": {
    "previous_intent": "analytics",
    "previous_entities": {}
  }
}
```
- **Response Body:**
```json
{
  "answer": "The organization's current utilization is 82.5%.",
  "conversation_context": {
    "persona": "leadership",
    "previous_intent": "analytics",
    "previous_entities": {}
  }
}
```

## System Integration (Error Handling)

The APIs are designed to fail gracefully. If the AI service (AWS Bedrock) is unavailable or rate-limited, the `/api/copilot/chat` endpoint intercepts the backend exception and returns standardized HTTP status codes (e.g., `503 Service Unavailable`, `429 Too Many Requests`). 

The frontend catches these codes via its Axios client and displays appropriate user-friendly toast notifications, ensuring the main dashboard remains fully functional even if the AI is down.
