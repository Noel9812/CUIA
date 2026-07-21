# User Flows

# Capacity & Utilization Intelligence Agent (CUIA)

---

| Document Information | |
|----------------------|------------------------------------------------|
| Project Name | Capacity & Utilization Intelligence Agent (CUIA) |
| Document Type | User Flow Specification |
| Version | 1.0 |
| Status | Draft |
| Project Type | Proof of Concept (POC) |
| Prepared By | Project Team |
| Intended Audience | Developers, UI/UX Designers, Testers, Product Owners |
| Reference Documents | PRD.md, FRS.md |
| Last Updated | July 2026 |

---

# Document Revision History

| Version | Date | Author | Description |
|----------|------|--------|-------------|
| 1.0 | July 2026 | Project Team | Initial User Flow Specification |

---

# Table of Contents

1. Purpose
2. Scope
3. Actors
4. User Flow Conventions
5. High-Level Product Journey
6. Delivery Manager User Flows
7. Leadership User Flows
8. Shared Operational Flows
9. Alternate & Exception Flows
10. User Journey Summary

---

# 1. Purpose

This document describes how users interact with the Capacity & Utilization Intelligence Agent (CUIA) from the moment they access the application until they complete their tasks.

The objective of this document is to define complete end-to-end user journeys for all supported personas within the Proof of Concept.

The user flows describe:

- User actions
- System responses
- Decision points
- Expected outcomes

This document intentionally avoids implementation details such as APIs, database operations, or user interface layouts. Those topics are documented separately in the API Specification, Data Model, and Wireframes documents.

---

# 2. Scope

This document covers all user interactions supported within the Proof of Concept.

Included workflows:

- User authentication
- Jira synchronization
- Leave data upload
- Skill mapping upload
- Workforce analytics generation
- Dashboard interaction
- AI Copilot interaction
- Workforce recommendations
- Daily notifications
- User logout

The following are outside the scope of this document:

- Administrator workflows
- Multi-tenant onboarding
- HR integrations
- Azure DevOps integration
- GitHub integration
- Engineer self-service workflows

---

# 3. Actors

The following actors participate in one or more user journeys.

---

## 3.1 Delivery Manager

Primary operational user responsible for monitoring engineering teams.

Responsibilities include:

- Synchronizing Jira data
- Uploading leave information
- Uploading skill mappings
- Reviewing workforce analytics
- Monitoring utilization
- Reviewing recommendations
- Using the AI Copilot

---

## 3.2 Leadership

Executive user responsible for organizational oversight.

Responsibilities include:

- Viewing executive dashboards
- Monitoring organization-wide trends
- Reviewing capacity forecasts
- Reviewing workforce risks
- Using the AI Copilot

Leadership users do not manage operational datasets directly.

---

## 3.3 Microsoft Entra ID

External identity provider responsible for authenticating users.

Responsibilities include:

- User authentication
- Identity verification
- Access token issuance

---

## 3.4 Jira Cloud

Primary external data source.

Responsibilities include:

- Providing engineering project information
- Providing issue data
- Providing worklogs
- Providing estimates
- Providing sprint information

---

## 3.5 AI Copilot

Conversational assistant that explains workforce analytics and recommendations.

Responsibilities include:

- Interpreting user questions
- Retrieving relevant analytics
- Generating contextual explanations
- Presenting recommendations

The AI Copilot does not calculate workforce metrics.

---

## 3.6 Notification Service

System component responsible for delivering workforce summaries.

Responsibilities include:

- Dashboard notifications
- Email notifications

---

# 4. User Flow Conventions

To maintain consistency throughout this document, every workflow follows a common structure.

Each flow contains:

- Objective
- Preconditions
- Flow Diagram
- Step-by-Step Interaction
- Postconditions

---

## Objective

Describes the purpose of the workflow.

---

## Preconditions

Defines the conditions that must be satisfied before the workflow begins.

---

## Flow Diagram

Illustrates the overall journey using a simplified sequence.

Example:

```text
User Login
      │
      ▼
Microsoft Authentication
      │
      ▼
Role Resolution
      │
      ▼
Dashboard
```

---

## Step-by-Step Interaction

Each workflow distinguishes between user actions and system actions.

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Select Sign In |
| 2 | System | Redirect to Microsoft Entra ID |
| 3 | User | Authenticate |
| 4 | System | Validate token |
| 5 | System | Determine user role |
| 6 | System | Redirect to dashboard |

---

## Postconditions

Defines the expected system state after successful completion of the workflow.

---

# 5. High-Level Product Journey

The following flow represents the complete lifecycle of a typical user session within the Proof of Concept.

```text
Open Application
        │
        ▼
Sign In using Microsoft Entra ID
        │
        ▼
Authentication Successful
        │
        ▼
Determine User Role
        │
        ▼
Display Role-Specific Dashboard
        │
        ▼
Synchronize Jira Data (Manager)
        │
        ▼
Upload Leave Dataset (Manager)
        │
        ▼
Upload Skill Mapping (Manager)
        │
        ▼
Generate Workforce Analytics
        │
        ▼
Generate Recommendations
        │
        ▼
Review Dashboards
        │
        ▼
Interact with AI Copilot
        │
        ▼
Receive Workforce Insights
        │
        ▼
Logout
```

---

# 5.1 Overall User Journey Description

The user accesses the application through a web browser and authenticates using Microsoft Entra ID.

After successful authentication, the system identifies the user's role and presents the appropriate dashboard.

Depending on the user's responsibilities, operational data may be synchronized from Jira and supplementary datasets such as leave information and skill mappings may be uploaded.

Once the required datasets are available, the analytics engine generates workforce metrics, which are then used to produce recommendations and populate dashboards.

Users can explore workforce insights visually through dashboards or interact conversationally with the AI Copilot to obtain explanations, summaries, and recommendations.

The session concludes when the user logs out or the authenticated session expires.

---

# Summary

This section establishes the foundation for all user journeys within the Capacity & Utilization Intelligence Agent.

The following sections define the detailed workflows for each supported user role, beginning with the Delivery Manager, followed by Leadership workflows and shared operational processes.

---

# 6. Delivery Manager User Flows

The Delivery Manager is the primary operational user of the Capacity & Utilization Intelligence Agent (CUIA).

This role is responsible for maintaining workforce data, monitoring team health, reviewing analytics, identifying capacity risks, and using AI-assisted insights to support resource planning decisions.

---

# Flow 1 – User Authentication

## Objective

Authenticate the Delivery Manager and establish a secure application session.

---

## Preconditions

- User has been granted access to the application.
- Microsoft Entra ID is available.
- User possesses valid organizational credentials.

---

## Flow Diagram

```text
Open Application
        │
        ▼
Select "Sign in with Microsoft"
        │
        ▼
Authenticate with Entra ID
        │
        ▼
Token Validation
        │
        ▼
Resolve User Role
        │
        ▼
Open Team Dashboard
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens the application. |
| 2 | User | Clicks **Sign in with Microsoft**. |
| 3 | System | Redirects user to Microsoft Entra ID. |
| 4 | User | Authenticates successfully. |
| 5 | System | Validates the received access token. |
| 6 | System | Determines the user's application role. |
| 7 | System | Creates an authenticated session. |
| 8 | System | Displays the Team Dashboard. |

---

## Postconditions

- User is authenticated.
- Session is established.
- Team Dashboard is displayed.

---

# Flow 2 – Synchronize Jira Data

## Objective

Import the latest engineering project information from Jira.

---

## Preconditions

- User is authenticated.
- Jira connection has been configured.
- User has permission to initiate synchronization.

---

## Flow Diagram

```text
Team Dashboard
        │
        ▼
Select "Synchronize Jira"
        │
        ▼
Connect to Jira
        │
        ▼
Retrieve Project Data
        │
        ▼
Validate Data
        │
        ▼
Store Data
        │
        ▼
Display Synchronization Summary
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Selects **Synchronize Jira**. |
| 2 | System | Connects to Jira. |
| 3 | System | Retrieves configured project data. |
| 4 | System | Validates retrieved records. |
| 5 | System | Stores synchronized information. |
| 6 | System | Displays synchronization summary and timestamp. |

---

## Postconditions

- Jira data is available for analytics.
- Synchronization status is updated.

---

# Flow 3 – Upload Leave Data

## Objective

Import employee leave information used for capacity calculations.

---

## Preconditions

- User is authenticated.
- Leave dataset is available.

---

## Flow Diagram

```text
Team Dashboard
        │
        ▼
Open Leave Upload
        │
        ▼
Select File
        │
        ▼
Validate Dataset
        │
        ▼
Import Valid Records
        │
        ▼
Display Upload Summary
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens the Leave Upload page. |
| 2 | User | Selects a CSV or Excel file. |
| 3 | System | Validates the uploaded file. |
| 4 | System | Imports valid records. |
| 5 | System | Reports rejected records, if any. |
| 6 | System | Displays upload summary. |

---

## Postconditions

- Leave information becomes available for analytics.

---

# Flow 4 – Upload Skill Mapping

## Objective

Import employee skill information.

---

## Preconditions

- User is authenticated.
- Skill dataset is available.

---

## Flow Diagram

```text
Team Dashboard
        │
        ▼
Open Skill Upload
        │
        ▼
Choose File
        │
        ▼
Validate Dataset
        │
        ▼
Store Skills
        │
        ▼
Display Summary
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens Skill Upload. |
| 2 | User | Selects skill mapping file. |
| 3 | System | Validates uploaded data. |
| 4 | System | Stores employee skill mappings. |
| 5 | System | Displays import summary. |

---

## Postconditions

- Skill information is available for workforce analysis.

---

# Flow 5 – Generate Workforce Analytics

## Objective

Generate workforce intelligence using the latest available datasets.

---

## Preconditions

- Jira synchronization completed.
- Leave data available.
- Skill data available.

---

## Flow Diagram

```text
Validated Datasets
        │
        ▼
Generate Analytics
        │
        ▼
Calculate Metrics
        │
        ▼
Generate Recommendations
        │
        ▼
Update Dashboards
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Selects **Generate Analytics** (or analytics are triggered automatically after data refresh). |
| 2 | System | Validates required datasets. |
| 3 | System | Generates workforce analytics. |
| 4 | System | Generates recommendations. |
| 5 | System | Updates dashboards. |

---

## Postconditions

- Analytics are available.
- Recommendations are generated.
- Dashboards display updated information.

---

# Flow 6 – Review Team Dashboard

## Objective

Monitor workforce health for the manager's assigned team.

---

## Preconditions

- User is authenticated.
- Analytics have been generated.

---

## Flow Diagram

```text
Open Team Dashboard
        │
        ▼
Load Analytics
        │
        ▼
Display KPIs
        │
        ▼
Review Charts
        │
        ▼
Review Recommendations
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens the Team Dashboard. |
| 2 | System | Loads latest analytics. |
| 3 | System | Displays utilization, workload, productivity, and capacity metrics. |
| 4 | User | Reviews charts and KPIs. |
| 5 | User | Reviews generated recommendations. |

---

## Postconditions

- User understands current workforce health.
- User identifies potential risks.

---

# Flow 7 – Use AI Copilot

## Objective

Allow the Delivery Manager to interact with workforce analytics using natural language.

---

## Preconditions

- User is authenticated.
- Analytics are available.

---

## Flow Diagram

```text
Open AI Copilot
        │
        ▼
Enter Question
        │
        ▼
Validate Authorization
        │
        ▼
Retrieve Analytics
        │
        ▼
Generate AI Response
        │
        ▼
Display Answer
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens AI Copilot. |
| 2 | User | Asks a workforce-related question. |
| 3 | System | Validates user authorization. |
| 4 | System | Retrieves relevant analytics. |
| 5 | System | Generates contextual explanation. |
| 6 | System | Displays response and recommendations. |

---

## Example Questions

- Who is overloaded?
- Which engineers are underutilized?
- What capacity risks exist?
- Why is utilization low this sprint?
- What should I prioritize next week?

---

## Postconditions

- User receives contextual business insights.
- User can continue the conversation within the same session.

---

# Flow 8 – Review Notifications

## Objective

Allow the manager to review workforce summaries generated by the system.

---

## Preconditions

- Analytics have been generated.
- Notification summary is available.

---

## Flow Diagram

```text
Open Notifications
        │
        ▼
Load Summary
        │
        ▼
Review Risks
        │
        ▼
Review Recommendations
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens Notifications. |
| 2 | System | Displays the latest workforce summary. |
| 3 | User | Reviews highlighted risks. |
| 4 | User | Reviews recommended actions. |

---

## Postconditions

- User is informed about the latest workforce status.

---

# Flow 9 – Logout

## Objective

Terminate the authenticated session securely.

---

## Preconditions

- User is authenticated.

---

## Flow Diagram

```text
Select Logout
        │
        ▼
Terminate Session
        │
        ▼
Return to Sign-In Page
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Selects **Logout**. |
| 2 | System | Invalidates the active session. |
| 3 | System | Redirects the user to the sign-in page. |

---

## Postconditions

- User session is terminated.
- Protected application resources are no longer accessible.

---

# Summary

The Delivery Manager workflows represent the primary operational journey within the Capacity & Utilization Intelligence Agent.

These workflows cover the complete lifecycle of workforce management, including authentication, data synchronization, supplemental data uploads, analytics generation, dashboard review, AI-assisted analysis, notification review, and secure logout.

The following section defines the user journeys for Leadership users and shared operational workflows that support the overall application.

# 7. Leadership User Flows

The Leadership role provides an organization-wide view of workforce health, capacity trends, operational risks, and strategic planning insights.

Unlike the Delivery Manager, Leadership users primarily consume analytical information and do not manage operational datasets.

---

# Flow 1 – User Authentication

## Objective

Authenticate the Leadership user and establish a secure application session.

---

## Preconditions

- User has been granted access.
- Microsoft Entra ID is available.
- User possesses valid organizational credentials.

---

## Flow Diagram

```text
Open Application
        │
        ▼
Sign in with Microsoft
        │
        ▼
Authenticate
        │
        ▼
Validate Token
        │
        ▼
Resolve Leadership Role
        │
        ▼
Executive Dashboard
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens the application. |
| 2 | User | Selects **Sign in with Microsoft**. |
| 3 | System | Redirects user to Microsoft Entra ID. |
| 4 | User | Authenticates successfully. |
| 5 | System | Validates access token. |
| 6 | System | Resolves Leadership role. |
| 7 | System | Displays Executive Dashboard. |

---

## Postconditions

- Leadership session established.
- Executive Dashboard displayed.

---

# Flow 2 – Review Executive Dashboard

## Objective

Review the overall health of engineering teams.

---

## Preconditions

- User is authenticated.
- Analytics have been generated.

---

## Flow Diagram

```text
Executive Dashboard
        │
        ▼
Load Organization Analytics
        │
        ▼
Display KPIs
        │
        ▼
Display Trends
        │
        ▼
Display Risks
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens Executive Dashboard. |
| 2 | System | Loads organization-wide analytics. |
| 3 | System | Displays executive KPIs. |
| 4 | System | Displays trend visualizations. |
| 5 | User | Reviews overall workforce health. |

---

## Postconditions

- Leadership gains an organization-wide operational overview.

---

# Flow 3 – Review Forecast Dashboard

## Objective

Understand future workforce demand and capacity.

---

## Preconditions

- Forecast data has been generated.

---

## Flow Diagram

```text
Forecast Dashboard
        │
        ▼
Load Forecast
        │
        ▼
Display Capacity Trends
        │
        ▼
Display Predicted Risks
        │
        ▼
Review Recommendations
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens Forecast Dashboard. |
| 2 | System | Loads forecast analytics. |
| 3 | System | Displays future capacity projections. |
| 4 | System | Highlights predicted capacity gaps. |
| 5 | User | Reviews future workforce planning recommendations. |

---

## Postconditions

- Leadership understands projected workforce risks.

---

# Flow 4 – Use AI Copilot

## Objective

Obtain executive insights using natural language.

---

## Preconditions

- Analytics are available.
- User is authenticated.

---

## Flow Diagram

```text
Open AI Copilot
        │
        ▼
Ask Question
        │
        ▼
Authorize Request
        │
        ▼
Retrieve Analytics
        │
        ▼
Generate Response
        │
        ▼
Display Executive Insight
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens AI Copilot. |
| 2 | User | Asks an executive-level question. |
| 3 | System | Validates authorization. |
| 4 | System | Retrieves relevant analytics. |
| 5 | System | Generates contextual response. |
| 6 | System | Displays answer and recommendations. |

---

## Example Questions

- Which teams are at the highest capacity risk?
- What are the organization-wide utilization trends?
- What staffing risks exist next month?
- Which managers require attention?
- What is the overall workforce health score?

---

## Postconditions

- Leadership receives organization-level insights.

---

# Flow 5 – Logout

## Objective

Securely terminate the authenticated session.

---

## Preconditions

- User is authenticated.

---

## Flow Diagram

```text
Logout
        │
        ▼
Terminate Session
        │
        ▼
Return to Login
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Selects Logout. |
| 2 | System | Terminates session. |
| 3 | System | Redirects user to Sign-In page. |

---

## Postconditions

- Session terminated.

---

# 8. Shared Operational Flows

The following workflows are system-driven and support all user roles.

These processes execute in the background or are shared across multiple application modules.

---

# Flow 1 – Workforce Analytics Generation

## Objective

Generate workforce intelligence from synchronized organizational data.

---

## Preconditions

- Jira data available.
- Leave data available.
- Skill mappings available.

---

## Flow Diagram

```text
Validate Datasets
        │
        ▼
Generate Metrics
        │
        ▼
Generate Recommendations
        │
        ▼
Store Analytics
        │
        ▼
Refresh Dashboards
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | System | Validates required datasets. |
| 2 | System | Calculates workforce analytics. |
| 3 | System | Generates recommendations. |
| 4 | System | Stores analytical results. |
| 5 | System | Refreshes dashboard data. |

---

## Postconditions

- Latest workforce intelligence available.

---

# Flow 2 – Dashboard Refresh

## Objective

Present the latest available workforce analytics.

---

## Preconditions

- Analytics exist.

---

## Flow Diagram

```text
Open Dashboard
        │
        ▼
Load Analytics
        │
        ▼
Apply Role Filter
        │
        ▼
Render Dashboard
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Opens a dashboard. |
| 2 | System | Retrieves latest analytics. |
| 3 | System | Applies role-based filtering. |
| 4 | System | Displays dashboard contents. |

---

## Postconditions

- Dashboard displays authorized information.

---

# Flow 3 – AI Copilot Processing

## Objective

Generate secure, contextual AI responses.

---

## Preconditions

- User authenticated.
- Analytics available.

---

## Flow Diagram

```text
Receive Question
        │
        ▼
Authorize User
        │
        ▼
Interpret Intent
        │
        ▼
Retrieve Analytics
        │
        ▼
Generate AI Response
        │
        ▼
Return Answer
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Submits a question. |
| 2 | System | Validates authorization. |
| 3 | System | Determines user intent. |
| 4 | System | Retrieves relevant analytics. |
| 5 | System | Sends analytical context to the AI model. |
| 6 | System | Returns AI-generated explanation. |

---

## Postconditions

- User receives an authorized analytical response.

---

# Flow 4 – Daily Summary Notification

## Objective

Provide proactive workforce summaries.

---

## Preconditions

- Analytics generated.
- Notification schedule reached.

---

## Flow Diagram

```text
Scheduled Trigger
        │
        ▼
Load Analytics
        │
        ▼
Generate Summary
        │
        ▼
Deliver Notification
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | System | Starts scheduled notification process. |
| 2 | System | Retrieves latest analytics. |
| 3 | System | Generates workforce summary. |
| 4 | System | Applies recipient authorization. |
| 5 | System | Sends dashboard notification and email. |

---

## Postconditions

- Workforce summary delivered to intended recipients.

---

# Summary

Leadership workflows focus on strategic oversight rather than operational data management.

Shared operational workflows ensure that analytics, dashboards, AI responses, and notifications are generated consistently and securely for all supported user roles.

The final section of this document defines alternate and exception flows that describe how the application behaves when authentication, synchronization, uploads, analytics, or external services encounter failures.

# 9. Alternate & Exception Flows

The following workflows describe how the system behaves when normal operations cannot be completed successfully.

These flows ensure that users receive clear feedback while maintaining system integrity and preventing unauthorized access or inconsistent analytical results.

---

# Flow 1 – Authentication Failure

## Objective

Prevent unauthorized access when authentication cannot be completed.

---

## Trigger

Authentication fails because of one of the following:

- Invalid credentials
- Expired session
- Expired access token
- Authentication cancelled
- Microsoft Entra ID unavailable

---

## Flow Diagram

```text
Open Application
        │
        ▼
Sign In
        │
        ▼
Authentication Failed
        │
        ▼
Display Error Message
        │
        ▼
Retry Authentication
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Attempts to sign in. |
| 2 | System | Sends authentication request to Microsoft Entra ID. |
| 3 | System | Authentication cannot be completed. |
| 4 | System | Displays authentication failure message. |
| 5 | User | Chooses to retry authentication. |

---

## Outcome

- No session is created.
- Protected resources remain inaccessible.

---

# Flow 2 – Authorization Failure

## Objective

Prevent users from accessing information outside their authorized scope.

---

## Trigger

User attempts to access data or functionality not permitted for their role.

---

## Flow Diagram

```text
Request Protected Resource
        │
        ▼
Validate Authorization
        │
        ▼
Access Denied
        │
        ▼
Display Access Denied Message
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Attempts to access restricted information. |
| 2 | System | Validates user permissions. |
| 3 | System | Rejects unauthorized request. |
| 4 | System | Displays access denied message. |

---

## Outcome

- Protected information is not exposed.
- User remains within authorized scope.

---

# Flow 3 – Jira Synchronization Failure

## Objective

Handle synchronization failures without affecting existing analytical data.

---

## Trigger

Synchronization cannot complete because of:

- Network interruption
- Invalid Jira credentials
- Jira API unavailable
- Configuration error

---

## Flow Diagram

```text
Start Synchronization
        │
        ▼
Connection Failure
        │
        ▼
Synchronization Failed
        │
        ▼
Notify User
        │
        ▼
Retry Later
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Initiates synchronization. |
| 2 | System | Attempts connection to Jira. |
| 3 | System | Connection fails. |
| 4 | System | Displays synchronization failure message. |
| 5 | User | Retries synchronization at a later time. |

---

## Outcome

- Previously synchronized data remains available.
- No partial analytical update occurs.

---

# Flow 4 – Leave Upload Validation Failure

## Objective

Handle invalid leave datasets while preserving valid information.

---

## Trigger

Uploaded file contains invalid records or formatting issues.

---

## Flow Diagram

```text
Upload Dataset
        │
        ▼
Validate File
        │
        ▼
Validation Failed
        │
        ▼
Display Validation Report
        │
        ▼
Upload Corrected File
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Uploads leave dataset. |
| 2 | System | Validates uploaded data. |
| 3 | System | Detects invalid records. |
| 4 | System | Displays validation report. |
| 5 | User | Corrects dataset and uploads again. |

---

## Outcome

- Invalid records are not imported.
- Valid records remain available.

---

# Flow 5 – Skill Mapping Validation Failure

## Objective

Prevent invalid skill information from entering the system.

---

## Trigger

Skill upload contains missing or invalid information.

---

## Flow Diagram

```text
Upload Skill File
        │
        ▼
Validate Dataset
        │
        ▼
Validation Failed
        │
        ▼
Display Validation Report
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Uploads skill mapping file. |
| 2 | System | Validates uploaded information. |
| 3 | System | Rejects invalid records. |
| 4 | System | Displays validation summary. |

---

## Outcome

- Only validated skills are retained.

---

# Flow 6 – Analytics Generation Failure

## Objective

Prevent incomplete analytics from being presented to users.

---

## Trigger

Required datasets are unavailable or incomplete.

---

## Flow Diagram

```text
Generate Analytics
        │
        ▼
Dataset Validation
        │
        ▼
Validation Failed
        │
        ▼
Display Missing Data Message
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Requests analytics generation. |
| 2 | System | Validates required datasets. |
| 3 | System | Detects missing information. |
| 4 | System | Stops analytics generation. |
| 5 | System | Displays explanation to user. |

---

## Outcome

- Previous analytics remain available.
- No inconsistent metrics are generated.

---

# Flow 7 – AI Copilot Service Unavailable

## Objective

Ensure application usability even when AI services are unavailable.

---

## Trigger

External AI provider cannot generate a response.

---

## Flow Diagram

```text
Ask Copilot
        │
        ▼
Call AI Service
        │
        ▼
Service Unavailable
        │
        ▼
Display Friendly Message
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | User | Submits question. |
| 2 | System | Sends request to AI provider. |
| 3 | System | AI request fails. |
| 4 | System | Displays friendly service unavailable message. |

---

## Outcome

- Dashboards remain operational.
- Workforce analytics remain accessible.

---

# Flow 8 – Notification Delivery Failure

## Objective

Prevent notification failures from affecting workforce analytics.

---

## Trigger

Notification cannot be delivered.

---

## Flow Diagram

```text
Generate Notification
        │
        ▼
Delivery Failure
        │
        ▼
Record Failure
        │
        ▼
Continue Application
```

---

## Step-by-Step Interaction

| Step | Actor | Action |
|------|-------|--------|
| 1 | System | Generates workforce summary. |
| 2 | System | Attempts notification delivery. |
| 3 | System | Delivery fails. |
| 4 | System | Records failure. |
| 5 | System | Continues normal application operation. |

---

## Outcome

- Workforce analytics remain unaffected.
- Notification may be retried later.

---

# 10. User Journey Summary

The following table summarizes the primary workflows supported by the Capacity & Utilization Intelligence Agent.

| User / Component | Primary Journey |
|------------------|-----------------|
| Delivery Manager | Login → Synchronize Jira → Upload Leave → Upload Skills → Generate Analytics → Team Dashboard → AI Copilot → Notifications → Logout |
| Leadership | Login → Executive Dashboard → Forecast Dashboard → AI Copilot → Logout |
| Analytics Engine | Validate Data → Generate Analytics → Generate Recommendations → Refresh Dashboards |
| AI Copilot | Receive Question → Authorize → Retrieve Analytics → Generate Response → Return Answer |
| Notification Service | Retrieve Analytics → Generate Summary → Deliver Notification |

---

# Overall User Journey

```text
Open Application
        │
        ▼
Authenticate with Microsoft Entra ID
        │
        ▼
Determine User Role
        │
        ▼
Display Appropriate Dashboard
        │
        ▼
Acquire / Refresh Workforce Data
        │
        ▼
Generate Workforce Analytics
        │
        ▼
Generate Recommendations
        │
        ▼
Review Dashboards
        │
        ▼
Interact with AI Copilot
        │
        ▼
Review Notifications
        │
        ▼
Logout
```

---

# Conclusion

The user flows documented in this specification define the complete end-to-end interaction model for the Capacity & Utilization Intelligence Agent (CUIA) Proof of Concept.

The document describes the operational journeys for Delivery Managers and Leadership users, the shared system workflows that support workforce intelligence generation, and the alternate flows that ensure predictable behaviour during exceptional conditions.

Together with the Product Requirements Specification (PRD) and Functional Requirements Specification (FRS), these user flows provide a complete functional view of how users interact with the application.

The detailed user interface layouts, analytical calculations, system architecture, data model, API contracts, and security implementation are documented separately in the remaining project documentation.