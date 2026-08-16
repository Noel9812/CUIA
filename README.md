# CUIA — Capacity & Utilization Intelligence Agent

Welcome to the **CUIA (Capacity & Utilization Intelligence Agent)** project documentation. This is the authoritative technical reference for the current CUIA Proof of Concept (POC).

## What is CUIA?

CUIA is a workforce analytics and intelligence platform designed to replace manual, spreadsheet-driven utilization tracking with an automated, data-driven system. It aggregates simulated Jira data to provide real-time visibility into engineering capacity, workload distribution, team health, and delivery risks.

The POC demonstrates how deterministic backend analytics can be combined with a scoped, token-optimized AI Copilot (powered by LangGraph and AWS Bedrock) to answer natural language queries securely and reliably.

## Target Audience

This documentation is designed for:
- **Developers** needing to understand the architecture, data flow, and code structure.
- **Technical Reviewers** auditing the system for security, determinism, and mathematical correctness.
- **Delivery Managers & Leadership** exploring the capabilities of the system.

## Documentation Structure

The documentation is structured to guide you from high-level architecture down to specific component implementations. We recommend reading in the following order:

1. [Project Overview](docs/01_PROJECT_OVERVIEW.md) - Business problem, personas, and tech stack.
2. [System Architecture](docs/02_SYSTEM_ARCHITECTURE.md) - Subsystems and responsibilities.
3. [End-to-End Application Flow](docs/03_END_TO_END_APPLICATION_FLOW.md) - How a request travels through the system.
4. [Data Model & Data Flow](docs/04_DATA_MODEL_AND_DATA_FLOW.md) - Entities, relationships, and JSON schema.
5. [Metrics & Analytics](docs/05_METRICS_AND_ANALYTICS.md) - Mathematical formulas and business definitions.
6. [AI Copilot](docs/06_AI_COPILOT.md) - Overview of the natural language interface.
7. [LangGraph Architecture](docs/07_LANGGRAPH_ARCHITECTURE.md) - Deep dive into the AI orchestration workflow.
8. [Security & Persona Isolation](docs/08_SECURITY_AND_PERSONA_ISOLATION.md) - How data is strictly scoped per user.
9. [API & System Integration](docs/09_API_AND_SYSTEM_INTEGRATION.md) - FastAPI endpoints and frontend integration.
10. [Testing & Validation](docs/10_TESTING_AND_VALIDATION.md) - Assurance of mathematical correctness and AI behavior.
11. [Configuration & Business Rules](docs/11_CONFIGURATION_AND_BUSINESS_RULES.md) - Thresholds, weights, and JSON configs.
12. [Cost Optimization](docs/12_COST_OPTIMIZATION.md) - Minimizing LLM usage and token consumption.
13. [POC Limitations & Future](docs/13_POC_LIMITATIONS_AND_FUTURE.md) - What the POC does and what production needs.
14. [Demo Guide](docs/14_DEMO_GUIDE.md) - How to effectively present the CUIA POC.
15. [Engineering Learnings](docs/15_ENGINEERING_LEARNINGS.md) - Architectural lessons from building CUIA.

_Note: All historical documentation and previous audit reports have been moved to the `docs/archive/` directory to preserve the history without polluting the current source of truth._
