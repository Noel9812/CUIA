# CUIA: Complete System Analysis & Demo Guide

## 01. Executive Summary

CUIA (Capacity & Utilization Intelligence Agent) is a deterministic workforce analytics platform built as a Proof of Concept (POC). It provides organizational leaders and Delivery Managers with deep insights into engineering team performance, capacity, utilization, and skill risks.

Crucially, CUIA enforces **architectural determinism**. The AI Copilot does *not* calculate metrics, make predictions, or guess at team health. Instead, a strict Python-based Analytics Engine and Business Rules Engine compute all metrics deterministically from a JSON dataset. The AI (via LangGraph and AWS Bedrock) is used exclusively as a natural language interface to explain these pre-computed, deterministic insights.

---

## 02. Repository Structure

The repository is structured as a modern full-stack web application:

```text
CUIA
│
├── frontend/               # React + Vite + Tailwind CSS frontend
│   ├── src/
│   │   ├── components/     # UI building blocks (Navbar, Sidebar, Chat)
│   │   ├── pages/          # Views (Dashboard, Reports, Copilot, Team/Engineer details)
│   │   ├── hooks/          # React hooks
│   │   ├── services/       # API clients
│   │   └── types/          # TypeScript definitions
│   ├── package.json        # Frontend dependencies
│   └── vite.config.ts      # Vite configuration
│
├── backend/                # FastAPI + LangGraph Python backend
│   ├── app/
│   │   ├── ai/             # LangGraph, Prompts, Intent Classifier, Bedrock client
│   │   ├── api/            # API Routers (analytics, dashboard, copilot, etc.)
│   │   ├── core/           # Config loader, logger, data validator
│   │   ├── models/         # Pydantic schemas for the data model
│   │   └── services/       # Deterministic engines (Analytics, Business Rules, Forecast)
│   ├── sample_data/
│   │   └── dataset.json    # The "Database" (Mock simulated Jira data)
│   └── requirements.txt    # Python dependencies
│
├── docker-compose.yml      # Container orchestration
└── Caddyfile               # Reverse proxy configuration
```

---

## 03. Complete Architecture

**Implementation vs Documentation**: The system is fully containerized. However, it does **not** use a traditional SQL database (like PostgreSQL). Instead, the data layer is an in-memory representation of `dataset.json`.

```text
User
  |
  v
Caddy (Reverse Proxy - Port 80)
  |
  +---> React Frontend (Vite)
  |
  +---> FastAPI Backend (Port 8000 internally)
          |
          +---> API Routers (Dashboard, Analytics, Copilot)
          |
          +---> Services Layer (AnalyticsEngine, BusinessRulesEngine)
          |       |
          |       v
          |     DatasetLoader (Reads sample_data/dataset.json into memory)
          |
          +---> AI Layer (LangGraph CopilotGraph)
                  |
                  v
                AWS Bedrock (LLM Provider)
```

---

## 04. Frontend Architecture

- **Framework**: React 18, Vite, TypeScript.
- **Styling**: Tailwind CSS, Lucide React (icons).
- **Routing**: `react-router-dom` (Pages: `/`, `/reports`, `/copilot`, `/team/:id`, `/engineer/:id`).
- **State Management**: Simple React State (`useState`, `useEffect`). No Redux/Zustand is used.
- **Authentication**: **Mocked**. The user's role ("Persona") is selected via a dropdown in the `Navbar` and stored in `localStorage` under `cuia_persona`.

---

## 05. Backend Architecture

- **Framework**: FastAPI.
- **API Routing**: Modular routers located in `backend/app/api/` (`analytics.py`, `copilot.py`, `dashboard.py`).
- **Services Layer**: Strict separation of concerns. `AnalyticsEngine` computes metrics. `BusinessRulesEngine` computes subjective rankings (e.g., best performer).
- **AI Layer**: LangGraph workflow (`backend/app/ai/graph.py`) with a highly optimized intent classifier that bypasses LLMs for 90% of requests.

---

## 06. Database Architecture

**No PostgreSQL is implemented.**
- The "Database" is a 17,000+ line JSON file (`backend/sample_data/dataset.json`).
- It is loaded into memory on startup by `DatasetLoader` (`backend/app/services/dataset_loader.py`).
- **Schemas**: Defined in `backend/app/models/schemas.py` using Pydantic (Entities: `Issue`, `Engineer`, `Team`, `DeliveryManager`, `Organization`).

---

## 07. Authentication & RBAC

**Implementation**: Mocked for POC.
- **Frontend**: The `Navbar.tsx` allows the user to switch between `leadership` (Admin), `dm-1` (Alice Smith), and `dm-2` (Bob Johnson).
- **Backend API**: The frontend passes the persona directly in API calls (e.g., `/api/dashboard/delivery?managerId=dm-1`). The backend filters the JSON data based on this parameter to ensure Alice only sees Alice's teams.
- **Security Check**: There are no JWTs or actual OAuth flows.

---

## 08. Data Ingestion

- **Implementation**: There is no live CSV upload or Jira webhook in the active execution path.
- **Flow**: When the FastAPI server starts (see `@asynccontextmanager async def lifespan` in `main.py`), it calls `DatasetLoader.get_dataset()`. This reads `dataset.json`, validates it using `DataValidator.validate()`, and caches it in memory.

---

## 09. Analytics Engine

Located in `backend/app/services/analytics_engine.py`. This is a deterministic engine. It pre-computes everything when `get_analytics()` is called. No AI is used here.

### 10. Capacity Calculation
**File**: `analytics_engine.py` (`_compute_engineer_metrics`)
**Formula**: `Sprint Capacity = effectiveCapacity * sprint_duration_weeks`
- `effectiveCapacity` is a hardcoded field in `dataset.json` (usually `40` or `32` if they have leave).

### 11. Utilization Calculation
**Formula**: `Utilization = (Logged Hours / Sprint Capacity) * 100`
- It sums `loggedHours` for all issues assigned to the engineer in the current sprint.

### 12. Productivity Calculation
**Formula**: `Productivity = Sum(Story Points * Priority Weight)`
- For all *resolved* issues in the sprint, it multiplies the story points by a priority weight (e.g., Critical=1.5, High=1.2, Medium=1.0).

### 13. Jira Analytics
- The system computes **Estimation Accuracy**: `100 - (abs(Logged - Estimate) / Estimate * 100)`.
- It computes **Resolution Time**: Average hours between `startedTime` and `resolvedTime`.

### 14. Skills & Dependency Analytics
**File**: `dashboard.py` (`_compute_team_skills`)
- Analyzes all engineers in a team.
- If a skill has only 1 owner, `Risk = Critical`. If 2 owners, `Risk = Medium`.
- It automatically identifies a cross-training candidate: An engineer on the team with the skill listed in `secondarySkills` who has `utilization <= 80%`.

---

## 15. Team & 16. Engineer Analytics

- **Team Metrics**: Averages the metrics (Utilization, Health, Productivity) of all engineers mapped to `teamId`.
- **Engineer Drilldown**: When clicking an engineer, the frontend calls `/api/dashboard/engineer/{engineerId}`. It fetches the specific engineer object, their assigned issues, and scoped recommendations.

---

## 17. AI Copilot & 18. LangGraph Architecture

This is the crown jewel of the technical architecture. The AI subsystem (`backend/app/ai/graph.py`) is heavily optimized to save tokens and prevent hallucinations.

**Execution Flow:**
1. User asks a question (`/api/copilot/chat`).
2. **Entity Extraction**: `EntityExtractor.extract(question)` runs using Regex/String matching (0 LLM calls).
3. **Intent Classification**: `intent_classifier.py` uses keyword weights to guess intent. (e.g., "forecast", "analytics"). It only falls back to Bedrock if the keyword score is ambiguous.
4. **Context Building**: Based on intent (e.g., "analytics"), the graph routes to a tool node (`analytics_tool`). This node builds a tiny JSON context payload containing *only* the relevant data.
5. **LLM Explainer**: The `llm_explainer` node takes the system prompt + the deterministic context + the user question, and sends it to AWS Bedrock.

**Why is it built this way?**
To ensure the LLM never fabricates metrics. The LLM acts purely as a translator, turning the deterministic JSON context into a polite natural language sentence.

---

## 19. API Inventory

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/dashboard/leadership` | Full org metrics for Leadership persona |
| GET | `/api/dashboard/delivery?managerId=X` | Scoped team metrics for Delivery Manager |
| GET | `/api/dashboard/team/{teamId}` | Specific team drill-down |
| GET | `/api/dashboard/engineer/{engId}` | Specific engineer drill-down |
| POST| `/api/copilot/chat` | Send question to LangGraph Copilot |
| GET | `/api/health`, `/api/health/ai` | System health checks |

---

## 20. End-to-End User Flows

### Scenario: Delivery Manager views their dashboard
1. **Frontend**: User selects "Alice Smith" in Navbar. `persona` state becomes `dm-1`.
2. **Frontend**: `DashboardController.tsx` routes to `<DeliveryDashboard managerId="dm-1" />`.
3. **API Call**: GET `/api/dashboard/delivery?managerId=dm-1`
4. **Backend**: `dashboard.py` calls `AnalyticsEngine.get_analytics()`.
5. **Backend**: Filters the cached teams to only those where `managerId == "dm-1"`. Computes aggregated KPIs for just those teams.
6. **Frontend**: Receives JSON, updates React state, recharts graphs render.

### Scenario: User asks Copilot "Who is at risk of burnout?"
1. **Frontend**: User types in `Copilot.tsx`.
2. **API Call**: POST `/api/copilot/chat` with `{ "question": "Who is at risk...", "persona": "dm-1" }`.
3. **Graph**: `intent_classifier` identifies intent as `analytics`.
4. **Tool**: routes to `analytics_tool`, which builds a tiny JSON string of engineers under `dm-1` who have `burnoutRisk == "High"`.
5. **LLM**: AWS Bedrock receives the prompt and JSON. Replies: "In your teams, Mallory is at high risk due to 16 hours of capacity but high utilization."
6. **Frontend**: Chat UI displays the response.

---

## 21. Implemented vs Mocked vs Planned

- **Implemented**: LangGraph Copilot, Deterministic Analytics, Routing, React UI, Docker Compose.
- **Mocked**: `dataset.json` (simulating Jira/HR data), Authentication (Persona switching in UI).
- **Planned (Not Implemented)**: PostgreSQL database, actual OAuth2/SSO, live Jira webhook ingestion.

---

## 22. Demo Talk Track (5-Minute Script)

*(Start on the Leadership Dashboard)*
"Welcome to CUIA. As an engineering leader, I constantly struggle to answer one question: Are my teams healthy, or are they burning out? Jira gives me raw tickets, but it doesn't give me intelligence. CUIA bridges that gap."

*(Scroll through KPIs)*
"Here on the Leadership view, I can instantly see our Org Utilization and Productivity. But let's look at this from a Delivery Manager's perspective."

*(Switch Persona in Navbar to Alice Smith)*
"I'm now Alice. The system automatically scopes my data. Notice the API just fetched only the teams I manage. I see Team Alpha and Beta. Let's drill into Team Beta."

*(Click Team Beta)*
"Here we see the underlying deterministic calculations. We don't guess at team health. Our Business Rules Engine calculates this based on capacity, story points, and priority weights. Look at our Skills Risk section. CUIA analyzed the team and found that 'Spring Boot' is a critical dependency—only one person knows it. It even recommends 'Eve' for cross-training because she has the capacity."

*(Navigate to AI Copilot)*
"But what if I don't want to dig through dashboards? I can just ask our AI Copilot."
*(Type: "Which of my engineers are at risk of burnout?")*
"Notice how fast that was. We use a hardened LangGraph architecture. The system uses keyword intent classification to bypass the LLM for routing, deterministically grabs Alice's scoped data, and only uses the LLM to format the final sentence. The AI is strictly an explainer—it never hallucinates the math."

---

## 23. Likely Technical Questions & Answers

**Q: Does the LLM calculate utilization?**
**A**: Absolutely not. We built a strict boundary. The `AnalyticsEngine` (Python) calculates all math. The AI is fed a JSON context and acts purely as a linguistic interface.

**Q: How is Authentication handled?**
**A**: For this POC, it's mocked via a Persona switcher in the UI that passes the role to the backend. In production, we would replace this with OAuth2 (e.g., Azure AD or Okta) and inject the user's ID into the FastAPI request context.

**Q: Why LangGraph instead of a simple LangChain chain?**
**A**: We needed stateful routing. We route to specific context builders based on intent. If the user asks for a forecast, we route to the `forecast_tool` to build a specific JSON payload. LangGraph makes this deterministic routing trivial and highly observable.

**Q: How do you handle database latency?**
**A**: Currently, we load `dataset.json` into memory on startup and cache the computed analytics. For a production scale, we would use PostgreSQL with materialized views or a caching layer like Redis for the analytics aggregates.

---

## 24. Final Cheat Sheet

- **Core Metric**: Utilization = Logged / Capacity
- **Data Source**: `backend/sample_data/dataset.json` (Loaded into memory)
- **Analytics Hub**: `backend/app/services/analytics_engine.py` (Where all math happens)
- **AI Hub**: `backend/app/ai/graph.py` (LangGraph implementation)
- **Role Switching**: LocalStorage `cuia_persona`. Passed in API requests.
- **Model**: AWS Bedrock (invoked via `BedrockClient`).
- **Most Important UI Trick**: Changing the user in the top right changes the API endpoint query params (e.g., `?managerId=dm-1`).
- **Safety Boundary**: The AI *never* calculates. It only *explains*.
