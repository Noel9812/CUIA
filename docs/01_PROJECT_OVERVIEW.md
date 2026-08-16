# 1. Project Overview

## What is CUIA?

**CUIA (Capacity & Utilization Intelligence Agent)** is a deterministic workforce analytics platform combined with an AI-driven natural language interface. 

### The Business Problem
Currently, organizations track engineering capacity, utilization, and team health manually using fragmented Jira queries, massive spreadsheets, and anecdotal updates. This manual process is:
- **Slow & Reactive:** By the time utilization drops or burnout risk spikes, it's too late.
- **Error-Prone:** Subjective definitions of "capacity" lead to inaccurate metrics.
- **Hard to Query:** Asking "Why is Team Alpha underperforming?" requires hours of cross-referencing data.

### The Engineering Solution
CUIA solves this by acting as a single source of truth for workforce intelligence. It automatically computes deterministic metrics (utilization, velocity, health scores) and allows authorized managers to ask natural language questions about their teams. 

**Crucially, the AI does not calculate anything.** It only explains the deterministic results produced by the backend analytics engine.

## Target Personas

### Leadership
- **Needs:** Organization-wide visibility, spotting systemic risks, understanding cross-team dependencies, finding the healthiest/unhealthiest teams, and macro-level capacity planning.
- **Scope:** Access to all teams, all delivery managers, and all engineers.

### Delivery Manager (DM)
- **Needs:** Deep visibility into their specific teams. Managing engineer workload, identifying burnout, resolving critical blockers, and planning sprint capacity.
- **Scope:** Strictly isolated to teams they directly manage. They cannot see other DMs' data.

## What CUIA is NOT

To manage expectations, it is important to understand what the CUIA POC is not:
- **Not a generic chatbot:** It cannot answer questions outside of workforce analytics.
- **Not a Jira replacement:** It reads simulated data; it is not a project management tool.
- **Not an autonomous manager:** It provides insights and recommendations, but does not auto-assign tickets or fire engineers.
- **Not a general-purpose AI assistant:** It is highly specialized to the defined data model.

## Technology Stack

The current POC is built using the following stack:

**Frontend:**
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Charting:** Recharts
- **API Client:** Axios
- **Routing:** React Router

**Backend:**
- **Framework:** FastAPI (Python)
- **Data Validation:** Pydantic
- **Data Processing:** Python standard library (deterministic services)

**AI & Orchestration:**
- **Orchestrator:** LangGraph
- **LLM Provider:** AWS Bedrock
- **Core Strategy:** Deterministic keyword-based intent classification and entity extraction, followed by a single LLM call for explanation.

**Data & Infrastructure:**
- **Data Source:** Static JSON dataset (`sample_data/dataset.json`) simulating Jira.
- **Configuration:** JSON-based business rules (`config/`).
- **Deployment:** Docker & Docker Compose
- **Proxy:** Caddy / Nginx

**Testing:**
- **Framework:** Pytest
- **Validation:** Independent mathematical oracle for metric correctness.
