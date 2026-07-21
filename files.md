# Capacity & Utilization Intelligence Agent (CUIA)
## Project Documentation Structure

This document defines the complete project knowledge structure that should be created before implementation begins.

The purpose of this structure is to:

- Reduce coding agent token usage
- Improve consistency across development
- Prevent architecture drift
- Centralize business and technical decisions
- Enable coding agents to make high-quality implementation decisions
- Provide a scalable project foundation

---

# Recommended Folder Structure

```text
capacity-utilization-agent/

├── docs/
├── architecture/
├── analytics/
├── security/
├── copilot/
├── dashboards/
├── integrations/
├── api/
├── database/
├── prompts/
├── instructions/
├── skills/
├── schemas/
├── decisions/
├── backlog/
└── implementation/
```

---

# Complete File List

## docs/

```text
docs/
├── PRODUCT_REQUIREMENTS.md
├── IMPLEMENTATION_BLUEPRINT.md
├── POC_SCOPE.md
├── SYSTEM_OVERVIEW.md
├── DEVELOPMENT_ROADMAP.md
└── NON_FUNCTIONAL_REQUIREMENTS.md
```

---

## architecture/

```text
architecture/
├── SYSTEM_ARCHITECTURE.md
├── SYSTEM_CONTEXT.md
├── SEQUENCE_FLOWS.md
├── DATA_FLOW.md
├── FUTURE_MULTI_TENANT_DESIGN.md
├── COMPONENT_RESPONSIBILITIES.md
└── TECHNOLOGY_DECISIONS.md
```

---

## analytics/

```text
analytics/
├── UTILIZATION_ENGINE.md
├── WORKLOAD_ENGINE.md
├── PRODUCTIVITY_ENGINE.md
├── ESTIMATION_ENGINE.md
├── FORECAST_ENGINE.md
├── RISK_ENGINE.md
├── WHAT_IF_SIMULATION.md
├── METRIC_DEFINITIONS.md
└── CONFIDENCE_SCORING.md
```

---

## security/

```text
security/
├── RBAC_MODEL.md
├── AUTHENTICATION_MODEL.md
├── AUTHORIZATION_MODEL.md
├── LLM_GUARDRAILS.md
├── COMPLIANCE_MODEL.md
├── AUDIT_LOGGING.md
├── DATA_ACCESS_POLICY.md
└── SECURITY_ARCHITECTURE.md
```

---

## copilot/

```text
copilot/
├── COPILOT_SPECIFICATION.md
├── INSIGHT_GENERATION.md
├── RECOMMENDATION_ENGINE.md
├── DAILY_SUMMARY_ENGINE.md
├── QUESTION_CATALOG.md
└── TEAMS_BOT_FUTURE.md
```

---

## dashboards/

```text
dashboards/
├── EXECUTIVE_DASHBOARD.md
├── MANAGER_DASHBOARD.md
├── FORECAST_DASHBOARD.md
├── COPILOT_SCREEN.md
├── UI_NAVIGATION.md
└── DASHBOARD_METRICS.md
```

---

## integrations/

```text
integrations/
├── JIRA_INTEGRATION.md
├── LEAVE_DATA_SPEC.md
├── SKILLS_DATA_SPEC.md
├── DATA_SYNC_STRATEGY.md
└── FUTURE_INTEGRATIONS.md
```

---

## api/

```text
api/
├── API_SPECIFICATION.md
├── AUTH_API.md
├── ANALYTICS_API.md
├── COPILOT_API.md
├── FORECAST_API.md
└── SIMULATION_API.md
```

---

## database/

```text
database/
├── DATA_MODEL.md
├── SCHEMA_DESIGN.md
├── ENTITY_RELATIONSHIP_MODEL.md
├── DATA_RETENTION_POLICY.md
└── MIGRATION_STRATEGY.md
```

---

## prompts/

```text
prompts/
├── COPILOT_SYSTEM_PROMPT.md
├── SUMMARY_PROMPT.md
├── RECOMMENDATION_PROMPT.md
├── RISK_ANALYSIS_PROMPT.md
├── FORECAST_PROMPT.md
└── SIMULATION_PROMPT.md
```

---

## instructions/

```text
instructions/
├── GLOBAL_AGENT_RULES.md
├── BACKEND_AGENT.md
├── FRONTEND_AGENT.md
├── DATABASE_AGENT.md
├── ANALYTICS_AGENT.md
├── LANGGRAPH_AGENT.md
├── SECURITY_AGENT.md
├── QA_AGENT.md
└── DEVOPS_AGENT.md
```

---

## skills/

```text
skills/
├── workforce-analytics.skill.md
├── jira.skill.md
├── rbac.skill.md
├── copilot.skill.md
├── forecasting.skill.md
├── security.skill.md
├── dashboard.skill.md
├── recommendation.skill.md
└── notification.skill.md
```

---

## schemas/

```text
schemas/
├── utilization.schema.json
├── workload.schema.json
├── productivity.schema.json
├── estimation.schema.json
├── forecast.schema.json
├── risk.schema.json
├── recommendation.schema.json
└── summary.schema.json
```

---

## decisions/

```text
decisions/
├── ADR-001-SINGLE-TENANT-POC.md
├── ADR-002-AUTHENTICATION.md
├── ADR-003-LLM_PROVIDER.md
├── ADR-004-DATA_SOURCES.md
├── ADR-005-ANALYTICS_STRATEGY.md
└── ADR-006-COPILOT_STRATEGY.md
```

---

## backlog/

```text
backlog/
├── MVP_BACKLOG.md
├── FUTURE_ENHANCEMENTS.md
├── SPRINT_PLAN.md
├── DEMO_SCENARIOS.md
└── ACCEPTANCE_CRITERIA.md
```

---

# File Content Definitions

# docs/

## PRODUCT_REQUIREMENTS.md

Contains:

```text
Project Vision

Problem Statement

Business Goals

Target Users

Personas

Features

Use Cases

Success Criteria

Expected Outcomes
```

---

## IMPLEMENTATION_BLUEPRINT.md

Contains:

```text
Complete Project Overview

Architecture Summary

System Components

Data Sources

Role Model

Analytics Overview

Copilot Design

Dashboard Design

Security Design

Development Phases
```

---

## POC_SCOPE.md

Contains:

```text
Must Have Features

Nice To Have Features

Future Features

Out Of Scope Features

Project Constraints
```

---

## SYSTEM_OVERVIEW.md

Contains:

```text
How The Platform Works

User Journey

System Lifecycle

Business Workflow
```

---

## DEVELOPMENT_ROADMAP.md

Contains:

```text
Phase Breakdown

Milestones

Timeline

Deliverables
```

---

## NON_FUNCTIONAL_REQUIREMENTS.md

Contains:

```text
Performance

Scalability

Availability

Security

Maintainability

Observability
```

---

# architecture/

## SYSTEM_ARCHITECTURE.md

Contains:

```text
Frontend Architecture

Backend Architecture

Database Architecture

Analytics Layer

Copilot Layer

External Integrations

Technology Stack
```

---

## SYSTEM_CONTEXT.md

Contains:

```text
Actors

Systems

External Dependencies

Boundaries
```

---

## SEQUENCE_FLOWS.md

Contains:

```text
Login Flow

Analytics Flow

Copilot Flow

Notification Flow

Data Sync Flow
```

---

## DATA_FLOW.md

Contains:

```text
Jira

↓

Analytics

↓

Copilot

↓

Dashboard
```

---

## FUTURE_MULTI_TENANT_DESIGN.md

Contains:

```text
Tenant Model

Tenant Isolation

Tenant Aware RBAC

Tenant Expansion Strategy
```

---

# analytics/

## UTILIZATION_ENGINE.md

Contains:

```text
Inputs

Calculations

Outputs

Business Rules

Edge Cases
```

---

## WORKLOAD_ENGINE.md

Contains:

```text
Load Balancing Logic

Ownership Rules

Workload Scoring
```

---

## PRODUCTIVITY_ENGINE.md

Contains:

```text
Complexity Weighting

Productivity Formula

Trend Calculations
```

---

## ESTIMATION_ENGINE.md

Contains:

```text
Variance Formula

Accuracy Categories

Recommendation Rules
```

---

## FORECAST_ENGINE.md

Contains:

```text
Forecast Logic

Trend Analysis

Capacity Gap Logic
```

---

## RISK_ENGINE.md

Contains:

```text
Risk Score Formula

Risk Categories

Recommendations
```

---

## WHAT_IF_SIMULATION.md

Contains:

```text
Scenario Definitions

Simulation Logic

Output Rules
```

---

# security/

## RBAC_MODEL.md

Contains:

```text
Roles

Permissions

Access Matrix

Role Definitions
```

---

## AUTHENTICATION_MODEL.md

Contains:

```text
Microsoft Login

Token Handling

Session Management
```

---

## AUTHORIZATION_MODEL.md

Contains:

```text
Manager Access

Leadership Access

Resource Access Rules
```

---

## LLM_GUARDRAILS.md

Contains:

```text
Prompt Injection Prevention

Data Leakage Prevention

Allowed Queries

Blocked Queries

Protection Mechanisms
```

---

## COMPLIANCE_MODEL.md

Contains:

```text
Data Privacy

Retention Policy

Audit Requirements

Governance Controls
```

---

# copilot/

## COPILOT_SPECIFICATION.md

Contains:

```text
Capabilities

Question Types

Response Format

Limitations
```

---

## INSIGHT_GENERATION.md

Contains:

```text
Observation Rules

Analysis Rules

Recommendation Rules
```

---

## DAILY_SUMMARY_ENGINE.md

Contains:

```text
Daily Summary Structure

Manager Summary

Leadership Summary

Notification Logic
```

---

# dashboards/

## EXECUTIVE_DASHBOARD.md

Contains:

```text
Executive KPIs

Charts

Insights

Forecasts
```

---

## MANAGER_DASHBOARD.md

Contains:

```text
Utilization

Workload

Productivity

Risk Analysis
```

---

## FORECAST_DASHBOARD.md

Contains:

```text
Demand Forecasting

Capacity Planning

Capacity Gap
```

---

## COPILOT_SCREEN.md

Contains:

```text
Chat Design

Suggested Questions

Response Layout
```

---

# integrations/

## JIRA_INTEGRATION.md

Contains:

```text
Authentication

API Endpoints

Data Mapping

Sync Strategy
```

---

## LEAVE_DATA_SPEC.md

Contains:

```text
CSV Format

Validation Rules

Import Logic
```

---

## SKILLS_DATA_SPEC.md

Contains:

```text
Skills Format

Validation

Employee Mapping
```

---

# instructions/

## GLOBAL_AGENT_RULES.md

Critical file for all coding agents.

Contains:

```text
Never bypass RBAC

Never expose hidden data

Never calculate through LLM

Analytics must be deterministic

Follow architecture documents

Follow security documents

Follow API contracts
```

---

## BACKEND_AGENT.md

Contains:

```text
FastAPI Standards

Folder Organization

API Rules

Error Handling Standards
```

---

## FRONTEND_AGENT.md

Contains:

```text
React Standards

Component Structure

UI Guidelines
```

---

## ANALYTICS_AGENT.md

Contains:

```text
Metric Rules

Formula Standards

Validation Rules
```

---

## LANGGRAPH_AGENT.md

Contains:

```text
Workflow Patterns

Node Design

Tool Execution

Token Optimization Rules
```

---

# skills/

## workforce-analytics.skill.md

Contains:

```text
Capacity Concepts

Utilization Concepts

Productivity Concepts

Business Definitions
```

---

## jira.skill.md

Contains:

```text
Issue Types

Story Points

Worklogs

Estimates

Jira Data Model
```

---

## rbac.skill.md

Contains:

```text
Roles

Permissions

Access Rules
```

---

## copilot.skill.md

Contains:

```text
Question Handling

Response Structure

Recommendation Style
```

---

## forecasting.skill.md

Contains:

```text
Forecast Logic

Trend Analysis

Simulation Concepts
```

---

## security.skill.md

Contains:

```text
Data Privacy

Compliance

Guardrails

Security Best Practices
```

---

# Recommended Minimum Files Before Starting Development

These are the absolute minimum files that should exist before any coding begins:

```text
PRODUCT_REQUIREMENTS.md

IMPLEMENTATION_BLUEPRINT.md

POC_SCOPE.md

SYSTEM_ARCHITECTURE.md

RBAC_MODEL.md

LLM_GUARDRAILS.md

UTILIZATION_ENGINE.md

WORKLOAD_ENGINE.md

PRODUCTIVITY_ENGINE.md

FORECAST_ENGINE.md

COPILOT_SPECIFICATION.md

JIRA_INTEGRATION.md

DATA_MODEL.md

API_SPECIFICATION.md

GLOBAL_AGENT_RULES.md

BACKEND_AGENT.md

FRONTEND_AGENT.md

LANGGRAPH_AGENT.md

workforce-analytics.skill.md

jira.skill.md

rbac.skill.md

copilot.skill.md
```

These documents collectively become the project's **knowledge foundation**, ensuring coding agents can build the platform consistently, securely, and with significantly reduced token consumption.