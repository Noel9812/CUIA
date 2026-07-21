# Data Model
# Capacity & Utilization Intelligence Agent (CUIA)
---
| Document Information | |
|----------------------|------------------------------------------------|
| Project Name | Capacity & Utilization Intelligence Agent (CUIA) |
| Document Type | Data Model |
| Version | 1.0 |
| Status | Draft |
| Project Type | Proof of Concept (POC) |
| Prepared By | Project Team |
| Intended Audience | Backend Developers, Database Designers, AI Engineers, Frontend Developers, Testers |
| Reference Documents | PRD.md, FRS.md, USER_FLOWS.md, WIREFRAMES.md, ANALYTICS_SPEC.md |
| Last Updated | July 2026 |
---
# Document Revision History
| Version | Date | Author | Description |
|----------|------|--------|-------------|
| 1.0 | July 2026 | Project Team | Initial Data Model |
---
# Table of Contents
1. Purpose
2. Data Model Overview
3. Data Architecture
4. Data Categories
5. Data Lifecycle
6. Entity Overview
7. Naming Standards
8. Common Entity Attributes
9. Audit Strategy
10. Summary
---
# 1. Purpose
This document defines the conceptual and logical data model for the Capacity & Utilization Intelligence Agent (CUIA).
It describes:
- The data managed by the application
- The relationships between entities
- Data ownership
- Data flow
- Database design principles
- Future extensibility considerations
The purpose of this document is to establish a consistent data foundation that supports the Analytics Engine, dashboards, AI Copilot, notifications, and backend services.
This document intentionally focuses on the logical structure of the application's data and does not define database-specific implementation details such as SQL scripts or ORM models.
---
# 2. Data Model Overview
The Capacity & Utilization Intelligence Agent is a data-driven application.
Its primary responsibility is to transform operational workforce data into actionable workforce intelligence.
The system collects operational information from supported data sources, validates the data, stores it in a structured format, generates analytics, and exposes the resulting insights through dashboards and the AI Copilot.
The database acts as the central source of truth for all application data.
Every application module—including analytics, dashboards, notifications, and AI interactions—retrieves information from this centralized data model.
---
## Design Principles
The data model follows the principles established throughout the project.
- Single-tenant architecture
- Monolithic implementation with future microservice readiness
- Backend as the source of truth
- Deterministic analytics
- Normalized data model where practical
- Separation of operational data from analytical results
- Implemented on PostgreSQL in every environment
- Extensible for future multi-tenancy
---
## Data Ownership
The application treats each category of data according to its ownership.
| Data Category | Source of Truth |
|---------------|-----------------|
| User Information | Microsoft Entra ID |
| Team Assignments | Application Database |
| Jira Operational Data | Jira |
| Leave Data | Uploaded Files |
| Skill Mapping | Uploaded Files |
| Analytics Results | Analytics Engine |
| Recommendations | Recommendation Engine |
| AI Conversations | Application Database |
| Notifications | Application Database |
The application never modifies externally managed operational data such as Jira issues or Microsoft Entra ID user information.
---
# 3. Data Architecture
The application's data architecture separates operational information from analytical intelligence.
Operational data is imported into the system, validated, and stored.
The Analytics Engine processes this data and generates analytical results.
These analytical results are then consumed by dashboards, notifications, and the AI Copilot.
---
## Data Flow
```text
Microsoft Entra ID
        │
        ▼
Authenticated Users
        │
Jira ───────────────┐
                    │
Leave Upload ───────┤
                    │
Skill Upload ───────┘
        │
        ▼
Data Validation
        │
        ▼
Application Database
        │
        ▼
Analytics Engine
        │
        ▼
Analytics Results
        │
        ├──────────────┐
        │              │
        ▼              ▼
Dashboards      Recommendation Engine
                       │
                       ▼
               Notifications
                       │
                       ▼
                  AI Copilot
```
The application always operates on validated data.
The AI Copilot never accesses raw imported files or performs independent calculations.
---
# 4. Data Categories
The application organizes information into five logical categories.
---
## Master Data
Relatively static information required for application operation.
Examples include:
- Users
- Teams
- Roles
- Skills
---
## Operational Data
Data imported from external sources.
Examples include:
- Jira Issues
- Jira Worklogs
- Leave Records
- Skill Mapping Uploads
Operational data forms the foundation of workforce analytics.
---
## Analytical Data
Data generated by the Analytics Engine.
Examples include:
- Utilization Results
- Workload Results
- Productivity Results
- Forecast Results
- Skill Risk Results
Analytical data is deterministic and reproducible.
---
## Application Data
Information created internally by the application.
Examples include:
- Notifications
- Copilot Conversations
- Configuration
- Audit Logs
---
## Reference Data
Configuration values that influence business calculations.
Examples include:
- Working Hours
- Utilization Thresholds
- Productivity Weights
- Forecast Parameters
Reference data allows analytical behaviour to be adjusted without changing application logic.
---
# 5. Data Lifecycle
Each category of information follows a defined lifecycle within the application.
```text
External Source
        │
        ▼
Import
        │
        ▼
Validation
        │
        ▼
Storage
        │
        ▼
Analytics Processing
        │
        ▼
Recommendation Generation
        │
        ▼
Dashboard & Copilot Consumption
```
Throughout this lifecycle:
- Imported operational data remains unchanged.
- Analytics are regenerated whenever required.
- Recommendations are produced from analytics.
- AI responses are generated from analytics and recommendations.
---
# 6. Entity Overview
The application data model consists of several logical entity groups.
---
## Master Entities
Represent organizational information.
Examples:
- User
- Team
- Team Membership
- Role
- Skill
- User Skill
---
## Operational Entities
Represent imported operational information.
Examples:
- Jira Issue
- Worklog
- Leave Record
- File Import History
---
## Analytical Entities
Represent calculated workforce intelligence.
Examples:
- Utilization Result
- Workload Result
- Productivity Result
- Estimation Result
- Forecast Result
- Skill Risk Result
- Recommendation
---
## Application Entities
Support application functionality.
Examples:
- Copilot Conversation
- Copilot Message
- Notification
- Audit Log
- Application Configuration
The following sections define each entity in detail.
---
# 7. Naming Standards
To ensure consistency across the application, the following naming conventions shall be used.
---
## Entity Names
Entity names shall use singular nouns.
Examples:
- User
- Team
- Jira Issue
- Worklog
---
## Attribute Names
Attributes shall use descriptive camelCase names in application code.
Examples:
- displayName
- originalEstimateHours
- loggedHours
- utilizationPercentage
Database column naming conventions may differ depending on the implementation technology.
---
## Identifiers
Each entity shall have a unique identifier.
The Proof of Concept will use UUIDs for all primary keys.
---
## Dates and Times
All timestamps shall be stored in UTC.
Examples:
- createdAt
- updatedAt
- importedAt
---
# 8. Common Entity Attributes
Most application-managed entities share a common set of metadata fields.
| Attribute | Purpose |
|-----------|---------|
| id | Unique identifier |
| createdAt | Creation timestamp |
| updatedAt | Last modification timestamp |
| createdBy | User who created the record |
| updatedBy | User who last modified the record |
Externally managed entities such as imported Jira data may not contain all metadata fields.
---
# 9. Audit Strategy
The application maintains an audit trail for internally managed operations.
Audit information supports:
- Operational troubleshooting
- Security reviews
- Administrative reporting
The audit trail records:
- User performing the action
- Action performed
- Timestamp
- Entity affected
- Result of the operation
Operational data imported from external systems is not modified and therefore retains its original ownership.
---
# Summary
This section establishes the foundational principles of the CUIA data model by defining the purpose of the database, data ownership, architectural approach, logical data categories, lifecycle, naming conventions, and audit strategy.
The following sections describe each entity group in detail, including their attributes, relationships, and role within the application's analytics and intelligence platform.
---
# 10. Master Data Entities
Master Data represents relatively stable information that defines the organizational structure of the application.
Unlike operational data imported from Jira, master data changes infrequently and serves as the foundation for authorization, analytics, and workforce organization.
The following entities are classified as Master Data:
- User
- Role
- Team
- Team Membership
- Skill
- User Skill
---
# User
## Purpose
The User entity represents an authenticated application user.
Authentication is managed by Microsoft Entra ID.
The application stores only the information required for authorization, team assignment, analytics ownership, and application-specific functionality.
---
## Data Source
Primary Source:
- Microsoft Entra ID
Application-managed fields:
- Role
- Team Assignment
- Status
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal application identifier |
| entraObjectId | String | Yes | Microsoft Entra Object ID |
| displayName | String | Yes | User's display name |
| email | String | Yes | Primary email address |
| roleId | UUID | Yes | Assigned application role |
| status | Enum | Yes | Active / Inactive |
| lastLoginAt | DateTime | No | Most recent successful login |
| createdAt | DateTime | Yes | Record creation time |
| updatedAt | DateTime | Yes | Last modification time |
---
## Business Rules
- Each authenticated user has one application profile.
- Email addresses should be unique.
- Microsoft Entra ID remains the source of truth for identity.
- User records are never created manually.
- User profiles are automatically created during first successful login if they do not already exist.
---
## Relationships
```text
User
 │
 ├───────────────► Role
 │
 ├───────────────► Team Membership
 │
 ├───────────────► User Skill
 │
 ├───────────────► Leave Record
 │
 ├───────────────► Analytics Results
 │
 ├───────────────► Notifications
 │
 └───────────────► Copilot Conversations
```
---
# Role
## Purpose
The Role entity defines application-level authorization.
Authentication is delegated to Microsoft Entra ID.
Authorization is enforced by the backend using application roles.
---
## Supported Roles
For the Proof of Concept, three application roles exist.
| Role | Purpose |
|------|----------|
| Delivery Manager | Team-level workforce management |
| Leadership | Organization-level visibility |
| Platform Admin | Platform administration, governance and authorized operational support |
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| name | String | Yes | Role name |
| description | String | Yes | Business description |
---
## Business Rules
- A user may have multiple active roles; effective permissions are the union of role permissions.
- Authorization is enforced exclusively by the backend.
- Frontend role checks are for user experience only.
- AI Copilot receives only authorized data.
---
## Relationships
```text
Role
 │
 ▼
Users
```
---
# Team
## Purpose
The Team entity represents an engineering delivery team.
Teams provide the primary organizational boundary used throughout the application.
Analytics, dashboards, notifications, and recommendations are generated at the team level.
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| name | String | Yes | Team name |
| description | String | No | Team description |
| createdAt | DateTime | Yes | Creation timestamp |
| updatedAt | DateTime | Yes | Last modification timestamp |
---
## Business Rules
- Teams have zero or more active managers through `team_managers`; each manager may manage zero or more teams.
- Leadership users are not required to belong to a specific team.
- Analytics are generated independently for each team.
---
## Relationships
```text
Team
 │
 ├────────────► Team Membership
 │
 ├────────────► Jira Issues
 │
 ├────────────► Analytics Results
 │
 └────────────► Recommendations
```
---
# Team Membership
## Purpose
The Team Membership entity associates users with engineering teams.
Although the POC assumes one primary team per engineer, this entity provides flexibility for future expansion without redesigning the data model.
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| teamId | UUID | Yes | Associated team |
| userId | UUID | Yes | Associated user |
| joinedAt | DateTime | Yes | Date user joined the team |
| status | Enum | Yes | Active / Inactive |
---
## Business Rules
- A user may belong to one active team during the POC.
- The entity supports many-to-many relationships for future extensibility.
- Team membership controls analytical scope for Delivery Managers.
---
## Relationships
```text
User
 │
 ▼
Team Membership
 │
 ▼
Team
```
---
# Skill
## Purpose
The Skill entity defines the catalog of technical competencies recognized by the application.
Skills are used for dependency analysis and workforce planning.
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| name | String | Yes | Skill name |
| category | String | No | Optional grouping |
| createdAt | DateTime | Yes | Creation timestamp |
---
## Example Skills
- Azure
- Kubernetes
- Python
- React
- FastAPI
- PostgreSQL
- Terraform
---
## Business Rules
- Skill names must be unique.
- Skills are reusable across multiple users.
- Skills may belong to an optional category.
---
## Relationships
```text
Skill
 │
 ▼
User Skill
```
---
# User Skill
## Purpose
The User Skill entity maps engineers to their technical skills.
It supports many-to-many relationships between users and skills.
This entity forms the foundation of the Skill Risk Analysis module.
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| userId | UUID | Yes | Associated user |
| skillId | UUID | Yes | Associated skill |
| createdAt | DateTime | Yes | Mapping creation timestamp |
---
## Business Rules
- A user may possess multiple skills.
- A skill may belong to multiple users.
- Duplicate mappings are not permitted.
- Skills are imported through the Skill Mapping dataset.
---
## Relationships
```text
User
 │
 ▼
User Skill
 │
 ▼
Skill
```
---
# Master Entity Relationship Summary
The relationships between master entities are illustrated below.
```text
                Role
                 │
                 │
                 ▼
               User
              ╱   ╲
             ╱     ╲
            ▼       ▼
 Team Membership  User Skill
        │              │
        ▼              ▼
      Team           Skill
```
---
# Master Data Integrity Rules
The following integrity rules apply to all master entities.
| Rule | Description |
|------|-------------|
| Unique User Email | No duplicate email addresses |
| Unique Entra Object ID | Each Entra identity maps to one application user |
| Unique Team Name | Team names must be unique |
| Unique Skill Name | Skill names must be unique |
| No Duplicate User Skill | A user cannot have the same skill assigned twice |
| Valid Team Membership | Membership must reference existing users and teams |
| Valid Role Assignment | Every user must have exactly one application role |
---
# Summary
The Master Data entities establish the organizational structure of the Capacity & Utilization Intelligence Agent.
They define authenticated users, application roles, engineering teams, and technical skills, forming the foundation for authorization, analytics, recommendations, and workforce intelligence throughout the application.
The following section introduces the Operational Data entities, which capture information imported from Jira and user-uploaded datasets.
---
# 11. Operational Data Entities
Operational Data represents information imported from external systems or user-uploaded datasets.
Unlike Master Data, operational data changes frequently and serves as the primary input for the Analytics Engine.
The application stores only the operational data required to generate workforce analytics.
For the Proof of Concept, operational data originates from:
- Jira
- Leave Data Upload
- Skill Mapping Upload
- File Import Operations
---
# Jira Issue
## Purpose
The Jira Issue entity represents a locally synchronized copy of Jira work items required for workforce analytics.
The application stores only the fields necessary for reporting, analytics, forecasting, and recommendations.
The application does not attempt to replicate the complete Jira data model.
---
## Data Source
Primary Source:
- Jira REST API
Synchronization:
- Manual synchronization (POC)
- Future support for scheduled synchronization
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal application identifier |
| jiraIssueKey | String | Yes | Jira issue key (e.g., PROJ-101) |
| summary | String | Yes | Issue summary |
| issueType | String | Yes | Story, Bug, Task, etc. |
| priority | String | Yes | Issue priority |
| status | String | Yes | Current workflow status |
| assigneeUserId | UUID | No | Assigned application user |
| reporterName | String | No | Issue reporter |
| sprintName | String | No | Sprint name |
| storyPoints | Decimal | No | Story points |
| originalEstimateHours | Decimal | No | Planned effort |
| remainingEstimateHours | Decimal | No | Remaining effort |
| createdDate | DateTime | Yes | Issue creation date |
| resolvedDate | DateTime | No | Issue resolution date |
| labels | String | No | Comma-separated labels |
| components | String | No | Component names |
| importedAt | DateTime | Yes | Last synchronization timestamp |
---
## Business Rules
- Jira Issue Key must be unique.
- Issues are synchronized from Jira.
- Issues are never manually edited within the application.
- Analytics always operate on the synchronized copy.
---
## Relationships
```text
User
 │
 ▼
Jira Issue
 │
 ├──────────────► Worklog
 │
 └──────────────► Analytics Results
```
---
# Worklog
## Purpose
The Worklog entity records engineering effort logged against Jira issues.
Worklogs provide the primary input for utilization and productivity calculations.
---
## Data Source
Primary Source:
- Jira REST API
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| jiraWorklogId | String | Yes | Jira worklog identifier |
| issueId | UUID | Yes | Associated Jira issue |
| userId | UUID | Yes | Engineer logging work |
| loggedHours | Decimal | Yes | Hours logged |
| workDate | Date | Yes | Date work was performed |
| comment | String | No | Worklog comment |
| importedAt | DateTime | Yes | Synchronization timestamp |
---
## Business Rules
- Logged hours cannot be negative.
- Worklogs always reference an existing Jira Issue.
- Worklogs are imported from Jira.
- Imported worklogs are read-only.
---
## Relationships
```text
Jira Issue
 │
 ▼
Worklog
 │
 ▼
User
```
---
# Leave Record
## Purpose
The Leave Record entity stores approved leave imported from uploaded files.
Leave data adjusts engineer availability before utilization calculations are performed.
---
## Data Source
Primary Source:
- CSV Upload
- Excel Upload
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| userId | UUID | Yes | Associated engineer |
| leaveType | String | Yes | Leave classification |
| startDate | Date | Yes | Leave start date |
| endDate | Date | Yes | Leave end date |
| importedAt | DateTime | Yes | Upload timestamp |
---
## Business Rules
- Start date must not be later than end date.
- Leave records must reference an existing user.
- Overlapping leave entries should be detected during validation.
- Leave data is imported through the upload process.
---
## Relationships
```text
User
 │
 ▼
Leave Record
```
---
# File Import History
## Purpose
The File Import History entity records every operational data import performed within the application.
It provides visibility into import status, validation results, and upload history.
Although primarily an operational feature, it is valuable for administration, troubleshooting, and demonstration purposes.
---
## Supported Import Types
- Jira Synchronization
- Leave Upload
- Skill Upload
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| importType | Enum | Yes | Jira, Leave, Skill |
| fileName | String | No | Uploaded file name |
| importedByUserId | UUID | Yes | User initiating the import |
| importedAt | DateTime | Yes | Import timestamp |
| status | Enum | Yes | Success, Warning, Failed |
| totalRecords | Integer | Yes | Records processed |
| successfulRecords | Integer | Yes | Successfully imported |
| failedRecords | Integer | Yes | Failed validation |
| validationSummary | String | No | Summary of validation results |
---
## Business Rules
- Every import operation generates one history record.
- Import history is immutable after creation.
- Failed records are reported but do not prevent successful records from being imported.
---
## Relationships
```text
User
 │
 ▼
File Import History
```
---
# Operational Entity Relationship Summary
The relationships between operational entities are illustrated below.
```text
                 User
                  │
        ┌─────────┼─────────┐
        │         │         │
        ▼         ▼         ▼
 Jira Issue   Leave Record  File Import History
      │
      ▼
   Worklog
```
---
# Operational Data Integrity Rules
The following integrity rules apply to operational data.
| Rule | Description |
|------|-------------|
| Unique Jira Issue Key | Each synchronized issue must be unique |
| Valid Assignee | Assigned engineer must exist in the User entity when mapped |
| Valid Worklog Reference | Every worklog must reference an existing Jira Issue |
| Non-Negative Logged Hours | Logged effort cannot be negative |
| Valid Leave Dates | Leave start date must precede end date |
| Import Traceability | Every upload operation must have a corresponding history record |
---
# Operational Data Retention
Operational data is retained for analytical purposes throughout the Proof of Concept.
The application may periodically refresh synchronized Jira data during future enhancements.
Imported datasets remain available until replaced or explicitly removed by an administrator.
---
# Summary
Operational Data entities capture the external workforce information required by the Capacity & Utilization Intelligence Agent.
These entities represent synchronized Jira data and user-uploaded datasets, providing the validated operational foundation consumed by the Analytics Engine to generate workforce metrics, recommendations, forecasts, and AI-assisted insights.
The following section defines the Analytics and Intelligence entities that are generated internally by the application.
---
# 12. Analytics & Intelligence Entities
Analytics and Intelligence entities represent data generated internally by the application.
Unlike Operational Data, these entities are not imported from external systems.
They are produced by the Analytics Engine after processing validated operational data.
These entities serve as the primary data source for:
- Dashboards
- AI Copilot
- Notifications
- Historical trend analysis
- Capacity forecasting
---
# Analytics Run
## Purpose
The Analytics Run entity represents a single execution of the Analytics Engine.
It provides traceability for generated analytics and enables historical comparison between analytical executions.
Every analytical result generated by the system belongs to one Analytics Run.
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| analysisPeriodStart | Date | Yes | Analysis start date |
| analysisPeriodEnd | Date | Yes | Analysis end date |
| generatedAt | DateTime | Yes | Analytics generation time |
| generatedBy | String | Yes | Manual or Scheduled |
| status | Enum | Yes | Completed / Failed |
---
## Business Rules
- Every analytics execution creates one Analytics Run.
- Analytical results must reference an Analytics Run.
- Historical analytics are preserved for comparison.
---
## Relationships
```text
Analytics Run
 │
 ├────────► Utilization Snapshot
 ├────────► Workload Snapshot
 ├────────► Productivity Snapshot
 ├────────► Estimation Snapshot
 ├────────► Forecast Snapshot
 ├────────► Skill Risk Snapshot
 └────────► Recommendation
```
---
# Utilization Snapshot
## Purpose
Stores utilization metrics calculated for an engineer during an Analytics Run.
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| analyticsRunId | UUID | Yes | Analytics execution |
| userId | UUID | Yes | Engineer |
| availableCapacityHours | Decimal | Yes | Available capacity |
| loggedHours | Decimal | Yes | Logged effort |
| utilizationPercentage | Decimal | Yes | Utilization |
| classification | Enum | Yes | Underutilized / Healthy / High / Overloaded |
---
## Business Rules
- One utilization snapshot per engineer per analytics run.
- Values are generated only by the Analytics Engine.
- Manual editing is not permitted.
---
# Workload Snapshot
## Purpose
Stores workload distribution metrics.
---
## Attributes
| Attribute | Type | Required |
|-----------|------|----------|
| id | UUID | Yes |
| analyticsRunId | UUID | Yes |
| userId | UUID | Yes |
| assignedTickets | Integer | Yes |
| activeTickets | Integer | Yes |
| remainingHours | Decimal | Yes |
| criticalTicketCount | Integer | Yes |
| workloadClassification | Enum | Yes |
---
## Business Rules
- Generated during every analytics execution.
- Represents workload at the time of analysis.
---
# Productivity Snapshot
## Purpose
Stores productivity measurements generated by the Analytics Engine.
---
## Attributes
| Attribute | Type | Required |
|-----------|------|----------|
| id | UUID | Yes |
| analyticsRunId | UUID | Yes |
| userId | UUID | Yes |
| resolvedTickets | Integer | Yes |
| weightedCompletion | Decimal | Yes |
| averageResolutionTime | Decimal | Yes |
| loggedHours | Decimal | Yes |
---
## Business Rules
- Generated only for completed analysis periods.
- Used for historical productivity trends.
---
# Estimation Snapshot
## Purpose
Stores estimation accuracy metrics.
---
## Attributes
| Attribute | Type | Required |
|-----------|------|----------|
| id | UUID | Yes |
| analyticsRunId | UUID | Yes |
| userId | UUID | Yes |
| estimatedHours | Decimal | Yes |
| actualHours | Decimal | Yes |
| varianceHours | Decimal | Yes |
| variancePercentage | Decimal | Yes |
| accuracyClassification | Enum | Yes |
---
# Forecast Snapshot
## Purpose
Stores workforce forecasting results.
---
## Attributes
| Attribute | Type | Required |
|-----------|------|----------|
| id | UUID | Yes |
| analyticsRunId | UUID | Yes |
| forecastPeriod | String | Yes |
| forecastCapacity | Decimal | Yes |
| forecastDemand | Decimal | Yes |
| capacityGap | Decimal | Yes |
| forecastClassification | Enum | Yes |
---
# Skill Risk Snapshot
## Purpose
Stores calculated skill dependency analytics.
---
## Attributes
| Attribute | Type | Required |
|-----------|------|----------|
| id | UUID | Yes |
| analyticsRunId | UUID | Yes |
| skillId | UUID | Yes |
| engineerCount | Integer | Yes |
| dependencyLevel | Enum | Yes |
| criticalWorkOwnership | Integer | Yes |
---
# Recommendation
## Purpose
Represents deterministic recommendations generated from analytical results.
Recommendations are produced by the Recommendation Engine and consumed by dashboards, notifications, and the AI Copilot.
---
## Attributes
| Attribute | Type | Required |
|-----------|------|----------|
| id | UUID | Yes |
| analyticsRunId | UUID | Yes |
| category | Enum | Yes |
| priority | Enum | Yes |
| title | String | Yes |
| description | String | Yes |
| triggeredBy | String | Yes |
| targetUserId | UUID | No |
| targetTeamId | UUID | No |
| generatedAt | DateTime | Yes |
---
## Business Rules
- Recommendations are immutable once generated.
- Every recommendation references one Analytics Run.
- Recommendations are deterministic.
- AI Copilot may explain recommendations but cannot modify them.
---
# Analytics Entity Relationship Summary
```text
Analytics Run
      │
      ├──────────────┐
      │              │
      ▼              ▼
Utilization     Workload
      │              │
      ├──────────────┤
      ▼              ▼
Productivity   Estimation
      │              │
      └──────────────┐
                     ▼
              Forecast
                     │
                     ▼
              Skill Risk
                     │
                     ▼
             Recommendation
```
---
# Analytics Data Integrity Rules
| Rule | Description |
|------|-------------|
| Every snapshot belongs to one Analytics Run | Ensures traceability |
| Snapshots are read-only | Prevents manual modification |
| Recommendations reference an Analytics Run | Maintains explainability |
| Analytics are deterministic | Same input produces same output |
| Historical runs are retained | Supports trend analysis |
---
# Summary
Analytics and Intelligence entities represent the outputs generated by the Analytics Engine.
Rather than recalculating metrics on every request, the application stores analytical snapshots that provide a consistent, auditable, and performant source of workforce intelligence.
These entities power dashboards, AI Copilot interactions, forecasting, notifications, and historical trend analysis while preserving the deterministic nature of the platform.
The following section defines the AI and Application entities that support conversations, notifications, configuration, and operational management.
---
# 13. AI & Application Entities
Application entities support the operation of the Capacity & Utilization Intelligence Agent.
Unlike Operational Data and Analytics Data, these entities do not represent workforce information.
Instead, they enable application features such as:
- AI Copilot conversations
- Notifications
- Audit logging
- Application configuration
These entities improve usability, security, traceability, and operational management.
---
# Copilot Conversation
## Purpose
The Copilot Conversation entity represents a single AI conversation initiated by an authenticated user.
A conversation groups multiple user questions and AI responses into a logical session.
The conversation provides context for follow-up questions while maintaining a complete interaction history.
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| userId | UUID | Yes | User who initiated the conversation |
| title | String | No | Conversation title |
| startedAt | DateTime | Yes | Conversation start time |
| lastActivityAt | DateTime | Yes | Last interaction time |
| status | Enum | Yes | Active / Archived |
---
## Business Rules
- Every conversation belongs to one authenticated user.
- Users can have multiple conversations.
- Conversations are read-only once archived.
- Conversation ownership is enforced by backend authorization.
---
## Relationships
```text
User
 │
 ▼
Copilot Conversation
 │
 ▼
Copilot Message
```
---
# Copilot Message
## Purpose
The Copilot Message entity stores individual messages exchanged between the user and the AI Copilot.
Messages maintain conversational history and provide context for future responses.
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| conversationId | UUID | Yes | Associated conversation |
| sender | Enum | Yes | User / Assistant |
| message | Text | Yes | Message content |
| createdAt | DateTime | Yes | Message timestamp |
| analyticsRunId | UUID | No | Analytics snapshot referenced during response |
---
## Business Rules
- Messages belong to exactly one conversation.
- Messages are immutable after creation.
- AI responses may reference an Analytics Run to ensure explainability.
---
## Relationships
```text
Copilot Conversation
 │
 ▼
Copilot Message
 │
 ▼
Analytics Run
```
---
# Notification
## Purpose
The Notification entity stores workforce summaries and system-generated notifications delivered to users.
Notifications provide proactive visibility into important workforce events.
---
## Notification Types
- Daily Workforce Summary
- Capacity Alert
- Utilization Alert
- Forecast Alert
- Recommendation Alert
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| recipientUserId | UUID | Yes | Notification recipient |
| type | Enum | Yes | Notification type |
| title | String | Yes | Notification title |
| message | Text | Yes | Notification content |
| deliveryChannel | Enum | Yes | Dashboard / Email |
| status | Enum | Yes | Pending / Sent / Failed |
| generatedAt | DateTime | Yes | Creation timestamp |
| deliveredAt | DateTime | No | Delivery timestamp |
---
## Business Rules
- Notifications are generated automatically.
- Delivery status is tracked.
- Notifications are never shared across users.
- Notification content is generated from analytics results.
---
## Relationships
```text
User
 │
 ▼
Notification
```
---
# Audit Log
## Purpose
The Audit Log entity records security-sensitive and operational events occurring within the application.
Audit logging supports governance, traceability, and troubleshooting.
---
## Audited Events
Examples include:
- User login
- File upload
- Jira synchronization
- Analytics execution
- Copilot query
- Notification generation
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| userId | UUID | No | User performing the action |
| action | String | Yes | Operation performed |
| entity | String | Yes | Entity affected |
| result | Enum | Yes | Success / Failure |
| timestamp | DateTime | Yes | Event time |
| details | Text | No | Additional event information |
---
## Business Rules
- Audit records are immutable.
- Audit logs cannot be edited.
- Failed operations are also recorded.
- Audit logs are available only to authorized administrators.
---
## Relationships
```text
User
 │
 ▼
Audit Log
```
---
# Application Configuration
## Purpose
The Application Configuration entity stores configurable values used by the Analytics Engine and application services.
Configuration allows business rules to evolve without requiring application code changes.
---
## Configuration Categories
- Working Hours
- Utilization Thresholds
- Productivity Weights
- Forecast Parameters
- Notification Settings
---
## Attributes
| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Internal identifier |
| configKey | String | Yes | Configuration name |
| configValue | String | Yes | Configuration value |
| description | String | No | Business description |
| updatedAt | DateTime | Yes | Last modification time |
---
## Example Configuration
| Configuration | Example Value |
|--------------|---------------|
| Working Hours Per Day | 8 |
| Working Days Per Week | 5 |
| Underutilization Threshold | 60 |
| Healthy Utilization Threshold | 85 |
| Overload Threshold | 100 |
| Daily Summary Time | 09:00 |
---
## Business Rules
- Configuration keys must be unique.
- Configuration changes are audited.
- Analytics Engine always uses the latest active configuration.
---
# Application Entity Relationship Summary
```text
                    User
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
 Conversation  Notification  Audit Log
      │
      ▼
 Message
      │
      ▼
 Analytics Run
Application Configuration
        │
        ▼
Analytics Engine
```
---
# Application Data Integrity Rules
| Rule | Description |
|------|-------------|
| Conversation Ownership | Users can access only their own conversations |
| Immutable Messages | Messages cannot be modified after creation |
| Notification Privacy | Notifications are visible only to the intended recipient |
| Immutable Audit Logs | Audit records cannot be changed |
| Unique Configuration Keys | Configuration entries must be unique |
---
# Summary
Application entities provide the operational capabilities required by the Capacity & Utilization Intelligence Agent.
They support secure AI conversations, notification delivery, auditability, and configurable business rules while remaining independent of operational workforce data and analytical calculations.
Together with the Master Data, Operational Data, and Analytics entities, these application entities complete the logical data model required for the Proof of Concept.
---
# 14. Complete Data Model Relationships
The CUIA data model is organized into four logical layers.
Each layer has a clearly defined responsibility and interacts with adjacent layers through well-defined relationships.
```text
                    ┌────────────────────────────┐
                    │   Microsoft Entra ID       │
                    │ (Authentication Provider)  │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │       User       │
                         └────────┬─────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 ▼                ▼                ▼
              Role             Team           User Skill
                                  │                │
                                  ▼                ▼
                          Team Membership       Skill
────────────────────────────────────────────────────────────
                   External Operational Data
      Jira Issues        Worklogs        Leave Records
           │                 │                 │
           └─────────────────┴─────────────────┘
                             │
                             ▼
                    Analytics Engine
────────────────────────────────────────────────────────────
                     Analytics Layer
                     Analytics Run
                           │
      ┌──────────────┬──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
 Utilization     Workload     Productivity   Estimation
      │
      ├──────────────┬──────────────┐
      ▼              ▼              ▼
 Forecast      Skill Risk    Recommendation
────────────────────────────────────────────────────────────
                   Application Layer
User
 │
 ├──────── Conversation ─────── Message
 │
 ├──────── Notification
 │
 ├──────── Audit Log
 │
 └──────── Application Configuration
```
The layered architecture ensures that operational data, analytical processing, and application services remain loosely coupled while sharing a common data foundation.
---
# 15. Primary Keys
Every application-managed entity uses a universally unique identifier (UUID) as its primary key.
## Rationale
Using UUIDs provides:
- Globally unique identifiers
- Easier future migration to distributed services
- Reduced risk of key collisions
- Simplified PostgreSQL migration
- Future multi-tenant compatibility
Externally managed identifiers such as Jira Issue Keys and Microsoft Entra Object IDs are stored as business identifiers rather than primary keys.
---
# 16. Foreign Key Relationships
The application enforces referential integrity between related entities.
Examples include:
| Parent Entity | Child Entity |
|---------------|--------------|
| Role | User |
| User | Team Membership |
| Team | Team Membership |
| User | User Skill |
| Skill | User Skill |
| User | Leave Record |
| User | Jira Issue (Assignee) |
| Jira Issue | Worklog |
| Analytics Run | All Analytics Snapshots |
| Analytics Run | Recommendation |
| User | Notification |
| User | Copilot Conversation |
| Copilot Conversation | Copilot Message |
| User | Audit Log |
All foreign key relationships are validated by the backend before persistence.
---
# 17. Data Integrity Constraints
The application enforces a number of business-level integrity rules to ensure data consistency.
## Identity
- Every authenticated user must have one application profile.
- Microsoft Entra Object IDs must be unique.
- Email addresses must be unique.
---
## Team Structure
- A Delivery Manager with no active manager relationship has no team-scoped analytics access.
- Every engineer belongs to one active team in the POC.
- Team names must be unique.
---
## Skills
- Skill names must be unique.
- Duplicate User Skill mappings are not permitted.
---
## Jira Data
- Jira Issue Keys must be unique.
- Worklogs must reference existing Jira Issues.
- Logged hours cannot be negative.
---
## Leave Data
- Leave records must reference existing users.
- Leave start dates must precede end dates.
- Overlapping leave entries should be flagged during validation.
---
## Analytics
- Every analytics snapshot belongs to one Analytics Run.
- Analytics snapshots are read-only.
- Recommendations cannot exist without an Analytics Run.
---
## Application
- Copilot Messages belong to exactly one conversation.
- Notifications belong to one recipient.
- Audit Logs are immutable.
- Configuration keys are unique.
---
# 18. Recommended Indexes
The following indexes are recommended to improve application performance.
| Entity | Indexed Fields |
|----------|----------------|
| User | email, entraObjectId |
| Team | name |
| Skill | name |
| Jira Issue | jiraIssueKey, assigneeUserId, status |
| Worklog | issueId, userId, workDate |
| Leave Record | userId, startDate |
| Analytics Run | generatedAt |
| Utilization Snapshot | userId, analyticsRunId |
| Forecast Snapshot | forecastPeriod |
| Recommendation | priority, analyticsRunId |
| Notification | recipientUserId, status |
| Copilot Conversation | userId |
| Copilot Message | conversationId |
These indexes represent logical optimization guidance rather than implementation-specific database definitions.
---
# 19. Data Retention Strategy
The Proof of Concept maintains sufficient historical information to support trend analysis and demonstrations.
| Data Category | Retention |
|---------------|-----------|
| Master Data | Permanent |
| Operational Data | Retained until refreshed or removed |
| Analytics Snapshots | Permanent during POC |
| Recommendations | Permanent during POC |
| Notifications | Permanent during POC |
| Copilot Conversations | Permanent during POC |
| Audit Logs | Permanent during POC |
Future production implementations may introduce configurable retention policies.
---
# 20. PostgreSQL Readiness
PostgreSQL is used in every environment. Schema migrations are version controlled and use the PostgreSQL constraints, indexes and transaction semantics specified in this document.
---
# 21. Future Multi-Tenant Readiness
Although the Proof of Concept is intentionally single-tenant, the data model has been designed to support future multi-tenancy.
Future enhancements may introduce:
- Tenant management
- Tenant-specific configuration
- Tenant-level RBAC
- Tenant-specific Jira integrations
- Tenant isolation
The majority of entities can support this by introducing a `tenantId` attribute without requiring significant structural changes.
No tenant-specific logic is implemented within the Proof of Concept.
---
# 22. Data Ownership Summary
The table below summarizes ownership responsibilities across the platform.
| Data Category | Owner |
|---------------|-------|
| Authentication | Microsoft Entra ID |
| User Profile | Application |
| Teams | Application |
| Skills | Application |
| Jira Operational Data | Jira |
| Leave Data | Uploaded Dataset |
| Analytics Results | Analytics Engine |
| Recommendations | Recommendation Engine |
| AI Conversations | Application |
| Notifications | Application |
| Audit Logs | Application |
The application never modifies data owned by external systems.
---
# 23. Conclusion
This document defines the complete logical data model for the Capacity & Utilization Intelligence Agent (CUIA).
The model separates data into four logical layers:
- Master Data
- Operational Data
- Analytics & Intelligence Data
- Application Data
This separation ensures that operational information remains independent from analytical processing while enabling dashboards, recommendations, notifications, and the AI Copilot to operate on consistent, deterministic analytical results.
The model is intentionally designed to satisfy the needs of the Proof of Concept while remaining extensible for future enhancements, including scheduled analytics and multi-tenant support.
This Data Model provides the structural foundation for the API Specification, System Architecture, Security Design, and backend implementation.
---
# End of Document