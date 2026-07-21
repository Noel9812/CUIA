# IMPLEMENTATION_PLAN.md
# Capacity & Utilization Intelligence Agent (CUIA)

---

| Document Information | |
|----------------------|------------------------------------------------|
| Project Name | Capacity & Utilization Intelligence Agent (CUIA) |
| Document Type | Engineering Execution Blueprint |
| Version | 2.0 |
| Status | Draft |
| Project Type | Proof of Concept (POC) |
| Prepared By | Engineering Leadership |
| Intended Audience | AI Coding Agents, Backend/Frontend Developers, QA, DevOps |
| Reference Documents | PROJECT_BASELINE.md, PRD.md, FRS.md, ARCHITECTURE.md, DATA_MODEL.md, API_SPEC.md, ANALYTICS_SPEC.md, SECURITY.md, USER_FLOWS.md, WIREFRAMES.md |
| Last Updated | July 2026 |

---

# 1. Implementation Objective & Philosophy

This document is the definitive **Engineering Execution Blueprint** for the CUIA Proof of Concept. It translates the frozen requirements, architecture, analytics, security, workflows, and UI specifications into an actionable, dependency-aware, step-by-step roadmap optimized for execution by human developers and AI Coding Agents (Cursor, Codex, Antigravity, etc.).

**Implementation Philosophy:**
*   **AI-Optimized Execution:** Tasks are atomic, deterministic, and dependency-aware. Output artifacts and validation criteria are explicitly defined.
*   **Immutable Architecture:** The system employs a Modular Monolith with a distinct Background Worker. Analytics are calculated asynchronously (Snapshots), NEVER via synchronous REST APIs.
*   **Strict Security & Role Segregation:** Administration (Jira, CSVs, Data Quality) is built first and restricted entirely to the Platform Administrator.
*   **Database First:** Persistence models drive API contracts, which drive UI consumption.

---

# 2. Dependency Graph & Execution Order

The engineering execution strictly follows this topological order to ensure no module is orphaned or built out of sequence:

| Phase | Module | Depends On | Required By |
| :--- | :--- | :--- | :--- |
| **0** | **Project Initialization** | None | All Phases |
| **1** | **Database & Persistence** | Phase 0 | All Backend/Worker Phases |
| **2** | **Backend Security Core** | Phase 1 | All APIs, Background Worker |
| **3** | **Admin API Implementation** | Phase 2 | Admin UI, Data Pipelines |
| **4** | **Background Worker & ETL** | Phase 3 | Analytics Pipeline |
| **5** | **Analytics Pipeline** | Phase 4 | Dashboard APIs, AI Copilot |
| **6** | **AI Copilot API** | Phase 5 | Frontend AI Copilot |
| **7** | **Dashboard APIs** | Phase 5 | Frontend Dashboards |
| **8** | **Frontend Core** | Phase 2, 7 | All Frontend Modules |
| **9** | **Frontend Admin UI** | Phase 3, 8 | Deployment |
| **10** | **Frontend Consumer UI** | Phase 6, 7, 8 | Deployment |
| **11** | **Deployment & E2E Test** | All Phases | Release |

---

# 3. Phase-by-Phase Execution Plan

---

## Phase 0: Project Initialization

**Objective:** Create the monorepo structure, development environment, and configuration scaffolding.
**Dependencies:** None.

**Atomic Tasks for AI Agents:**
1.  Initialize Git repository.
2.  Create directory structure: `backend/`, `frontend/`, `docs/`, `docker/`.
3.  **Backend:** Initialize Python environment, generate `requirements.txt` (FastAPI, SQLAlchemy, Alembic, Celery or APScheduler, LangGraph, Pydantic, python-jose).
4.  **Frontend:** Initialize Vite React TypeScript project. Install TanStack Query, React Router, React Hook Form, Axios.
5.  **Config:** Create `.env.example` defining `DATABASE_URL`, `JWT_SECRET`, `ENTRA_CLIENT_ID`, `JIRA_API_KEY`, `OPENAI_API_KEY`, `WORKER_BROKER_URL`.

**Deliverables:** Empty runnable services, `docker-compose.yml` for local PostgreSQL + Redis (if using Celery).
**Quality Gate 0:** `docker-compose up` succeeds. Backend health check returns 200. Frontend loads default Vite page.

---

## Phase 1: Database & Persistence Foundation

**Objective:** Implement the frozen Data Model using SQLAlchemy and Alembic.
**Dependencies:** Phase 0.

**Atomic Tasks for AI Agents:**
1.  Configure SQLAlchemy Engine, Base, and SessionLocal.
2.  Initialize Alembic environment (`alembic init`).
3.  Implement User and Security entities (`User`, `Role`).
4.  Implement Operational entities (`Project`, `Employee`, `Worklog`, `Team`, `LeaveRecord`, `SkillRecord`).
5.  Implement Administration entities (`JiraConfig`, `IdentityMapping`, `DataQualityIssue`).
6.  Implement Analytics entities (`AnalyticsRun`, `CapacitySnapshot`, `UtilizationSnapshot`, `RiskSnapshot`, `Recommendation`).
7.  Generate initial Alembic migration script and apply it.

**Deliverables:** SQLAlchemy models, active PostgreSQL schema, seed script for an initial Platform Administrator user.
**Quality Gate 1:** `alembic upgrade head` succeeds. Unit tests can write and read from all tables.

---

## Phase 2: Backend Security Core

**Objective:** Implement Entra ID JWT validation and strict RBAC middleware.
**Dependencies:** Phase 1.

**Atomic Tasks for AI Agents:**
1.  Implement JWT Decoding utility (JWKS retrieval, signature validation).
2.  Implement `get_current_user` FastAPI dependency.
3.  Implement `System Identity` JWT generator (for Background Worker authorization).
4.  Implement RBAC dependencies: `require_platform_admin`, `require_delivery_manager`, `require_leadership`.
5.  Implement Data Isolation utility (filtering database queries by `user.team_id` for Managers).

**Deliverables:** Security middleware, token validation logic.
**Quality Gate 2:** API requests with invalid tokens return 401. API requests to admin routes with non-admin tokens return 403.

---

## Phase 3: Admin API Implementation

**Objective:** Expose the REST APIs required by the Platform Administrator for system configuration and data ingestion.
**Dependencies:** Phase 2.

**Atomic Tasks for AI Agents:**
1.  Implement `POST /api/v1/admin/jira/config` (Save/Test Jira keys).
2.  Implement `POST /api/v1/admin/upload/leave` (CSV parsing, basic validation, DataQualityIssue generation for bad rows).
3.  Implement `POST /api/v1/admin/upload/skills` (CSV parsing).
4.  Implement `GET` and `PUT` for `/api/v1/admin/identity/mappings`.
5.  Implement `GET` and `POST` for `/api/v1/admin/data-quality/resolve`.
6.  Implement `POST /api/v1/admin/jobs/trigger-analytics` (Enqueue background job).

**Deliverables:** Fully functioning Administration router protected by `require_platform_admin`.
**Quality Gate 3:** CSV uploads correctly persist data or generate `DataQualityIssue` records. Only Admin tokens can access.

---

## Phase 4: Background Worker & ETL Layer

**Objective:** Implement the headless async worker process responsible for Jira synchronization and scheduling `AnalyticsRun`.
**Dependencies:** Phase 3.

**Atomic Tasks for AI Agents:**
1.  Initialize Worker Application (Celery or APScheduler). Configure it to run as a separate process in `docker-compose`.
2.  Implement `JiraClient` (Fetch Projects, Issues, Worklogs using configuration from DB).
3.  Implement task: `sync_jira_data()` (Transforms external Jira data into internal `Project`, `Worklog` entities. Generates `IdentityMapping` issues for unknown users).
4.  Schedule `sync_jira_data()` to run hourly.

**Deliverables:** A background worker container that synchronizes data without blocking the FastAPI server.
**Quality Gate 4:** Worker starts independently. Connecting a mock Jira instance successfully populates the PostgreSQL database.

---

## Phase 5: Analytics Pipeline (The Engine)

**Objective:** Build the deterministic analytics pipeline that generates immutable Snapshots.
**Dependencies:** Phase 4.

**Atomic Tasks for AI Agents:**
1.  Implement `calculate_capacity()` function (Consumes Leave, Worklog, Employee data).
2.  Implement `calculate_utilization()` function.
3.  Implement `calculate_risks()` function (Overload/Underload thresholds).
4.  Implement `generate_recommendations()` function.
5.  Implement the orchestration task: `execute_analytics_run()`.
    *   Creates an `AnalyticsRun` record (Status: IN_PROGRESS).
    *   Executes calculations.
    *   Persists `CapacitySnapshot`, `UtilizationSnapshot`, `RiskSnapshot`, and `Recommendation`.
    *   Updates `AnalyticsRun` record (Status: COMPLETED or FAILED).
6.  Configure Worker to execute `execute_analytics_run()` nightly or when triggered manually via Admin API.

**Deliverables:** A fully automated pipeline that generates snapshots. No synchronous API triggers analytics.
**Quality Gate 5:** Manually triggering the job via the Admin API results in new Snapshot records in the database.

---

## Phase 6: AI Copilot API

**Objective:** Integrate LangGraph to orchestrate AI explanations over generated Snapshots.
**Dependencies:** Phase 5.

**Atomic Tasks for AI Agents:**
1.  Implement LangGraph state definition (`ConversationState`).
2.  Implement Analytics Tools for the LLM: `get_latest_team_snapshot()`, `get_latest_org_snapshot()`, `get_active_risks()`. These tools query the DB for existing Snapshots; they DO NOT run calculations.
3.  Implement the `system_prompt` enforcing strict constraints (No calculations, no PII, strictly explain provided data).
4.  Implement context injection (Injecting RBAC bounds—Manager only gets team data).
5.  Implement `POST /api/v1/copilot/chat`.

**Deliverables:** Secure, role-bound AI chat API.
**Quality Gate 6:** Prompt injection attacks are rejected. A Delivery Manager asking for Org data is gracefully denied.

---

## Phase 7: Dashboard APIs

**Objective:** Provide read-only access to the latest Snapshots for the UI.
**Dependencies:** Phase 5.

**Atomic Tasks for AI Agents:**
1.  Implement `GET /api/v1/dashboard/leadership` (Fetches Org-level Snapshots, Risks, Recommendations).
2.  Implement `GET /api/v1/dashboard/team/{team_id}` (Fetches Team-level Snapshots, validates user is Manager of `team_id`).
3.  Implement `GET /api/v1/system/status` (Returns latest `AnalyticsRun` status for background job UI indicators).

**Deliverables:** Read-only Dashboard APIs.
**Quality Gate 7:** Valid responses formatted according to `API_SPEC.md`.

---

## Phase 8: Frontend Core

**Objective:** Establish the React application shell, routing, and global state.
**Dependencies:** Phase 2, 7.

**Atomic Tasks for AI Agents:**
1.  Implement React Router with Route Guards (`<ProtectedRoute role="admin">`).
2.  Implement AuthContext (JWT decoding, Role storage).
3.  Implement Global Application Layout (Sidebar, Header).
4.  Implement Shared UI Components: `KPI Card`, `DataTable`, `ErrorBanner`, `BackgroundProcessingBadge`, `DataQualityWarning`.
5.  Implement Error Boundaries and 404/403/500 screens.

**Deliverables:** React shell with functioning navigation restrictions.
**Quality Gate 8:** Unauthenticated users are redirected to login. Role-based links hide/show correctly.

---

## Phase 9: Frontend Admin UI

**Objective:** Implement the Platform Administrator interface.
**Dependencies:** Phase 3, 8.

**Atomic Tasks for AI Agents:**
1.  Implement `AdminDashboard` (Status of integrations and jobs).
2.  Implement `JiraConfigForm` with validation.
3.  Implement `CSVUploadDropzone` for Leave and Skills (Requires TanStack mutation and error handling for Data Quality rejections).
4.  Implement `IdentityMappingTable` with resolution actions.
5.  Implement `DataQualityTable` with resolution actions.
6.  Implement "Trigger Analytics Run" button with Confirmation Dialog.

**Deliverables:** Complete Administration UI matching `WIREFRAMES.md`.
**Quality Gate 9:** Admin can successfully configure Jira and upload CSVs. Form validation traps client-side errors.

---

## Phase 10: Frontend Consumer UI

**Objective:** Implement the Dashboards and Copilot for Leadership and Managers.
**Dependencies:** Phase 6, 7, 8.

**Atomic Tasks for AI Agents:**
1.  Implement `LeadershipDashboard` (Org KPIs, Charts consuming Snapshots).
2.  Implement `TeamDashboard` (Team KPIs, Workload distribution).
3.  Implement conditional `DataQualityWarning` banners on dashboards if issues exist.
4.  Implement `CopilotChatWindow` (Message history, typing indicators, Markdown rendering).

**Deliverables:** Final user-facing analytics views.
**Quality Gate 10:** Dashboards render correctly. AI Chat provides streaming or standard responses safely.

---

## Phase 11: Deployment & E2E Testing

**Objective:** Prepare the POC for demonstration and validation.
**Dependencies:** All previous phases.

**Atomic Tasks for AI Agents:**
1.  Finalize `docker-compose.yml` defining exactly four services: `db` (Postgres), `api` (FastAPI), `worker` (Celery/APScheduler), `frontend` (React/Nginx).
2.  Write database seed scripts injecting realistic demo data (employees, leave, snapshot history).
3.  Write E2E API tests verifying full RBAC segregation (Admin vs Manager vs Leadership).
4.  Document demo startup commands.

**Deliverables:** A complete, single-command deployable POC (`docker-compose up --build`).
**Quality Gate 11:** The entire CUIA architecture launches cleanly. Data flows from Jira -> Worker -> Snapshots -> Dashboards/AI without manual intervention.

---

# 4. Critical Constraints for AI Coding Agents

When executing this blueprint, AI agents must adhere to the following rules:
*   **Do not modify database schema** outside of Phase 1.
*   **Do not create sync analytics.** Any prompt requesting "calculate utilization API" must be rejected in favor of fetching `UtilizationSnapshot`.
*   **Do not add Notifications.** If a process fails, it is logged to `AnalyticsRun` or `DataQualityIssue`; no emails are sent.
*   **Respect RBAC decorators.** Every endpoint MUST be decorated with the explicit required role.

---
# End of IMPLEMENTATION_PLAN.md