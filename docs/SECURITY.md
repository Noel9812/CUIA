# SECURITY.md
# Capacity & Utilization Intelligence Agent (CUIA)

---

| Document Information | |
|----------------------|------------------------------------------------|
| Project Name | Capacity & Utilization Intelligence Agent (CUIA) |
| Document Type | Security Specification |
| Version | 1.1 |
| Status | Draft |
| Project Type | Proof of Concept (POC) |
| Prepared By | Project Team |
| Intended Audience | Backend Developers, DevSecOps Engineers, QA Engineers, AI Engineers, Product Owners |
| Reference Documents | PROJECT_BASELINE.md, PRD.md, FRS.md, ARCHITECTURE.md, DATA_MODEL.md, API_SPEC.md, ANALYTICS_SPEC.md |
| Last Updated | July 2026 |

---

# Document Revision History

| Version | Date | Author | Description |
|----------|------|--------|-------------|
| 1.0 | July 2026 | Project Team | Initial Security Specification |
| 1.1 | July 2026 | ARB | Removed Notification Scope. Added Background Processing Security. Completed Platform Administrator RBAC matrix. Expanded Upload Security, Trust Boundaries, Data Protection, and Audit Logging. |

---

# 1. Security Overview & Vision
The Capacity & Utilization Intelligence Agent (CUIA) processes highly sensitive workforce intelligence data. The platform provides insights related to engineer utilization, workload distribution, productivity, forecasting, and workforce risks, alongside AI-generated recommendations. 

Because these insights influence management decisions, the security architecture is designed to enforce:
- **Identity First**: All access requires strong identity validation via Microsoft Entra ID.
- **Authorization Second**: Every resource request passes through strict Role-Based Access Control (RBAC).
- **Data Filtering Third**: All data retrieval is scoped to the user's explicit permissions.
- **Trusted Analytics Execution**: Analytics runs independently from user influence.
- **Restricted AI Processing**: The LLM consumes only authorized, deterministic outputs and cannot bypass RBAC.

Security is not treated as an additional feature; it is a fundamental design requirement embedded in the API middleware, database transactions, and background processing context.

---

# 2. Security Boundaries & Trust Zones
CUIA defines strict trust boundaries.

## 2.1 Untrusted Zones
- **Frontend (React Client)**: Cannot decide permissions, calculate analytics, or access the database. It is only responsible for rendering data and attaching the JWT.
- **User Inputs (APIs/CSV Uploads)**: All inputs, JSON payloads, search queries, and CSV files are considered untrusted and subject to strict validation.
- **AI Layer (LLM)**: Treated as an untrusted reasoning engine. It cannot execute database queries, validate permissions, or manage security states.

## 2.2 Trusted Zones
- **FastAPI Backend**: The ultimate authority for authentication, authorization, data scoping, and analytics execution.
- **Background Worker**: Executes within the trusted backend perimeter using a dedicated System Identity.
- **Database (PostgreSQL)**: Isolated behind the backend. Accessible only via authenticated backend connections.

---

# 3. Identity & Authentication Security
CUIA delegates user authentication entirely to **Microsoft Entra ID**. The system does not manage, store, or validate user passwords.

## 3.1 Authentication Flow
1. **User Login**: User authenticates via the Microsoft Entra ID OAuth 2.0 / OIDC flow.
2. **JWT Issuance**: Entra ID issues a JSON Web Token (JWT) Access Token containing user claims (e.g., `oid`, `email`, `name`, `tid`).
3. **API Request**: The React Frontend attaches the JWT to the `Authorization: Bearer` header.
4. **Backend Validation**: The FastAPI middleware intercepts the request and verifies the JWT.

## 3.2 JWT Validation Rules
The backend enforces the following checks before granting access:
- **Signature Validation**: Ensures the token was signed by Entra ID public keys (RS256).
- **Issuer (`iss`)**: Must match the expected Entra ID tenant URL.
- **Audience (`aud`)**: Must match the CUIA Application ID.
- **Expiration (`exp`)**: Validates the token is not expired (with standard clock skew allowances).
- **Tenant ID (`tid`)**: Ensures the user belongs to the authorized Entra tenant.

## 3.3 Token Failures & Expiration
- **Expired Tokens**: Rejected with `401 Unauthorized`. The frontend is responsible for triggering a silent token refresh via MSAL.
- **Malformed/Invalid Signature**: Rejected immediately with `401 Unauthorized` and flagged in the Audit Log as a potential security incident.
- **Revocation**: Handled at the Entra ID level; short-lived access tokens mitigate the window of compromise.

---

# 4. Authorization & RBAC Security
Authentication proves identity; authorization determines privileges. CUIA uses a strict, backend-enforced **Role-Based Access Control (RBAC)** model.

## 4.1 Principle of Least Privilege
The system applies a default-deny model. If a permission is not explicitly granted in the RBAC matrix, access is rejected with `403 Forbidden`.

## 4.2 Role Definitions

### Role 1: Platform Administrator
- **Purpose**: Manage the technical and data operations of the platform. Isolated from business analytics.
- **Responsibilities**: Configure integrations, manage identity mappings, resolve data quality issues, monitor background jobs, and review audit logs.
- **Allowed Resources**: Admin APIs, Data Upload endpoints, Background Job triggers.
- **Denied Resources**: Team Dashboards, Organization Dashboards, Analytics APIs, Business Copilot interactions. The Admin cannot view leadership analytics unless explicitly granted an additional role.

### Role 2: Delivery Manager
- **Purpose**: Manage engineering teams and understand team health.
- **Responsibilities**: Review team utilization, workload, and productivity.
- **Allowed Resources**: Team Dashboard, Team Analytics, Copilot (scoped to assigned teams).
- **Denied Resources**: Organization-wide data, Admin APIs, Data Uploads.

### Role 3: Leadership
- **Purpose**: View organization-wide workforce metrics.
- **Responsibilities**: Strategic capacity planning and risk mitigation.
- **Allowed Resources**: Executive Dashboard, Organization Metrics, Copilot (organization scope).
- **Denied Resources**: Admin APIs, Data Uploads.

## 4.3 Permission Matrix
| Capability | Platform Administrator | Delivery Manager | Leadership |
|---|---|---|---|
| Configure Jira | Yes | No | No |
| Manage Identity Mappings | Yes | No | No |
| View/Resolve Data Quality Issues| Yes | No | No |
| Upload CSV (Leave/Skills) | Yes | No | No |
| Trigger Background Jobs | Yes | No | No |
| View Audit Logs | Yes | No | No |
| View Team Dashboard | No | Yes (Assigned Only)| Yes (All) |
| View Exec Dashboard | No | No | Yes |
| Query Copilot | No | Yes (Assigned Only)| Yes (All) |

---

# 5. Background Processing Security
Scheduled Analytics calculations occur asynchronously via a Background Processing module (e.g., cron or background task worker).

## 5.1 Trusted System Identity
- **Purpose**: Background tasks operate without a user JWT. They execute under a trusted internal **System Identity**.
- **Trust Boundary**: The Background Worker runs entirely within the trusted backend perimeter.
- **Capabilities**: Allowed to execute Jira API syncs, generate `DataQualityIssue` records, execute the Analytics modules, and persist `AnalyticsRun`, `UtilizationSnapshot`, and `Recommendation` entities.
- **Restrictions**: Cannot respond to external HTTP requests, cannot read user passwords, cannot bypass Entra ID for interactive sessions.

## 5.2 Manual Administrative Triggers
When a Platform Administrator triggers a background job manually via the REST API (`POST /api/v1/admin/jobs/run`):
- The API validates the Administrator's JWT.
- The action is logged to the `AuditLog` mapping the Administrator to the job trigger.
- The backend asynchronously delegates execution to the System Identity, returning an immediate 202 Accepted.

---

# 6. Administrative Resource Security
The Platform Administrator manages critical configuration entities. Access is strictly audited.

## 6.1 Jira Configuration
- **Protection**: Jira API credentials (tokens) are NEVER retrievable via API. Updates via `PATCH /api/v1/admin/jira-config` act as write-only operations for the secret fields.

## 6.2 Identity Mappings
- **Protection**: External Jira Account IDs are mapped to internal Entra IDs. Read/Write access is restricted exclusively to the Platform Administrator. Any modification triggers an `AuditLog` event.

## 6.3 Data Quality Issues
- **Protection**: Malformed records (missing estimates, unmapped users) are stored as `DataQualityIssue` entities. The Platform Admin can view and resolve these, ensuring data integrity before the next Analytics Run.

---

# 7. Data Protection & Privacy

## 7.1 Data Classification
- **Highly Sensitive**: `UtilizationSnapshot`, `ProductivitySnapshot`, `Recommendation`. Protected by strict RBAC and Team-scoping.
- **Confidential/Administrative**: `IdentityMapping`, `DataQualityIssue`, `AuditLog`. Protected by Platform Admin RBAC.
- **Secrets**: Jira Tokens, LLM API Keys, Database Passwords. Stored exclusively in environment variables / secure vaults.

## 7.2 Storage and Encryption Assumptions
- **In Transit**: All communication (Frontend to Backend, Backend to DB, Backend to Integrations) strictly mandates HTTPS/TLS 1.2+.
- **At Rest**: The underlying Database (PostgreSQL) is assumed to use standard volume-level encryption provided by the cloud hosting environment.
- **Data Deletion**: Deletion policies (soft vs. hard delete) are defined in the Data Model. Snapshots are immutable.

---

# 8. Upload Security
Platform Administrators upload CSV data for Leave and Skill mapping.

## 8.1 CSV Validation Rules
- **Authorization**: Only users with the Platform Administrator role can access upload endpoints.
- **Format Validation**: Files must be exactly `text/csv`. MIME types and file extensions are validated.
- **Size Limits**: Enforced at the middleware level (e.g., max 5MB) to prevent Denial of Service (DoS).
- **Schema Validation**: The backend validates required headers, date formats, and data types before processing any row.
- **Malicious Content**: The backend strips any executable formulas (e.g., `=CMD()`) to prevent CSV injection vulnerabilities.

---

# 9. AI Security & LLM Governance
CUIA utilizes LangGraph to orchestrate an LLM Copilot. AI introduces risks like Prompt Injection and data leakage.

## 9.1 AI Authorization Boundaries
- **No Calculations**: The LLM is prohibited from calculating business metrics. It can only query deterministic Snapshots.
- **No RBAC Bypass**: The AI cannot override data filters. If a Delivery Manager asks "Show all organization metrics", the backend intercepts the tool call, enforces the Team Scope, and returns a 403 Forbidden to the LLM context, which the LLM then relays as "You do not have access."

## 9.2 Prompt Injection Protection
- **Instruction Hierarchy**: The system prompt forces the LLM to prioritize security instructions over user input.
- **Tool-Based Execution**: The LLM does not generate SQL. It is restricted to calling explicit REST-like internal functions (e.g., `get_utilization()`).
- **Context Isolation**: The LLM is fed ONLY the data relevant to the specific question and within the user's authorized scope. It never receives the entire database schema or full employee records.

## 9.3 Conversation & Audit Security
- **Conversations**: Stored securely. Conversations belong strictly to the user who created them.
- **Hallucination Mitigation**: The LLM is explicitly instructed to refuse answering questions if the provided tool outputs lack sufficient evidence.

---

# 10. Integration & Infrastructure Security

## 10.1 Jira Integration
- **Credentials**: Stored in backend environment variables, never committed to source control.
- **Permissions**: The Jira API token operates with Least Privilege (Read-Only access to Issues, Worklogs, Projects, and Users).

## 10.2 LLM Provider Integration
- **API Keys**: Stored in backend environment variables.
- **Data Minimization**: The backend strips PII (Personal Identifiable Information) before sending context to the LLM where possible, sending only aggregated Snapshot metrics.

---

# 11. Security Operations & Audit Logging
Audit logging ensures accountability for critical business and security events.

## 11.1 Audit Events
The backend records `AuditLog` entities for:
- **Authentication**: JWT validation failures (malformed, signature mismatch).
- **Authorization**: API access denied (403 Forbidden).
- **Administrative Actions**: Jira configuration updates, Identity Mapping creation/deletion.
- **Data Modifications**: CSV uploads completed, Data Quality issues resolved.
- **Background Jobs**: Manual triggers of the Analytics Run.

## 11.2 Audit Log Structure
Every audit event captures:
- `timestamp` (UTC)
- `user_id` (If authenticated)
- `action` (e.g., "IDENTITY_MAPPING_CREATED")
- `resource_id`
- `status` (SUCCESS, FAILURE)

## 11.3 Audit Log Visibility
Only the **Platform Administrator** is authorized to view Audit Logs. Audit logs are append-only and cannot be modified via the API.

---

# 12. Threat Mitigation

| Threat | Impact | Mitigation Strategy | Residual Risk |
|---|---|---|---|
| **Unauthorized API Access** | Data Leakage | All routes protected by JWT middleware. Reject missing/invalid tokens with 401. | Low |
| **Privilege Escalation** | Admin Takeover | Strict RBAC middleware checks `roles` claim against endpoint requirements. Default deny. | Low |
| **Prompt Injection** | Data Exfiltration | LLM restricted to predefined tools. Tools enforce the user's RBAC scope internally. | Medium |
| **CSV Poisoning** | Code Execution | Strict MIME typing, size limits, and formula stripping (`=`,`+`,`-`,`@`). | Low |
| **Token Theft / Replay** | Session Hijacking| Enforced HTTPS. Short-lived tokens. Standard clock skew expirations. | Low |
| **Jira Credential Leak** | External Breach | Credentials excluded from frontend/git. Stored securely in backend environment. | Low |

---

# 13. Security Assumptions & Limitations
For the Proof of Concept (POC), the following assumptions apply:
- **No Notification Security**: Email / SMTP capabilities are permanently out of scope. No notifications exist.
- **No Advanced SIEM**: Logs are written to standard output / basic database tables, not forwarded to Azure Sentinel or Splunk.
- **Single Tenant**: Data isolation is handled via RBAC and Team mapping, not multi-tenant physical database separation.
- **Environment Management**: Secrets are managed via secure Environment Variables, assuming standard containerized injection, rather than Azure Key Vault (which is deferred to production).

---
# End of SECURITY.md