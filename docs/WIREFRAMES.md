# WIREFRAMES.md
# Capacity & Utilization Intelligence Agent (CUIA)

---

| Document Information | |
|----------------------|------------------------------------------------|
| Project Name | Capacity & Utilization Intelligence Agent (CUIA) |
| Document Type | UI Blueprint Specification |
| Version | 1.1 |
| Status | Draft |
| Project Type | Proof of Concept (POC) |
| Prepared By | Project Team |
| Intended Audience | UI/UX Designers, Frontend Developers, QA Engineers, Product Owners |
| Reference Documents | PRD.md, FRS.md, USER_FLOWS.md, SECURITY.md, API_SPEC.md |
| Last Updated | July 2026 |

---

# Document Revision History

| Version | Date | Author | Description |
|----------|------|--------|-------------|
| 1.0 | July 2026 | Project Team | Initial UI Wireframe Specification |
| 1.1 | July 2026 | ARB | Upgraded to formal UI Blueprint. Removed Notifications. Added Platform Administrator module. Corrected RBAC and Role Separation. Added UI States and rigorous screen-level specifications. |

---

# Table of Contents

1. Purpose
2. Scope
3. UI Design Principles
4. Global Application Layout
5. Navigation Structure
6. Shared Components
7. Authentication Screens
8. Platform Administrator Screens
9. Delivery Manager Screens
10. Leadership Screens
11. Shared Screens
12. Responsive Behaviour
13. UI States
14. Screen Navigation Summary
15. Conclusion

---

# 1. Purpose

This document defines the definitive UI Blueprint Specification for the Capacity & Utilization Intelligence Agent (CUIA).
Its purpose is to translate the operational workflows defined in `USER_FLOWS.md` into concrete screen layouts, information hierarchies, and interaction behaviors.
It serves as the authoritative blueprint for frontend developers and UX designers, ensuring that routing, state management, validation presentation, and role-based component rendering can be implemented without inventing UI logic.

This document bridges the gap between functional workflows and the technical `IMPLEMENTATION_PLAN.md`.

---

# 2. Scope

This document specifies the structural layout and behaviour of all screens in the POC:
- Microsoft Entra ID Authentication Flow
- Platform Administrator Interface (Jira Config, Data Uploads, Identity Mapping, Data Quality, Job Triggers)
- Delivery Manager Dashboards and Team Analytics
- Leadership Executive Dashboards and Forecasts
- AI Copilot Interaction Interfaces
- Exception, Error, and Loading States

The following are strictly **out of scope**:
- CSS, Typography, Colors, or specific design system frameworks (e.g., Tailwind, Material UI).
- React components, code, or routing configurations.
- API definitions, database queries, or analytical formulas.
- Notification or Email workflows (permanently excluded).

---

# 3. UI Design Principles

- **Role-Based UI**: The application aggressively enforces RBAC at the rendering level. Users never see navigation links, buttons, or data outside their authorization scope.
- **Executive First**: Dashboards prioritize KPIs, risks, and recommendations above raw tables.
- **Information Before Decoration**: Screen layouts emphasize data density and readability over aesthetic embellishment.
- **Progressive Information Disclosure**: High-level metrics appear first, with drill-down tables available for deeper analysis.
- **Visibility of System Status**: Asynchronous background tasks (like `AnalyticsRun`) and data quality degradations are explicitly visible without blocking the user.
- **Error Prevention**: Forms and uploads validate synchronously where possible, providing clear recovery paths.

---

# 4. Global Application Layout

The application utilizes a persistent application shell to provide consistent navigation and status visibility across all authenticated routes.

## Layout Structure
```text
+--------------------------------------------------------------------------------------+
| Header                                                                     Profile |
+--------------------------------------------------------------------------------------+
|                                                                              |
| Sidebar              Breadcrumbs / Page Title                                         |
|                                                                              |
|                      ----------------------------------------------          |
|                      Main Content Area                           |          |
|                      (Dashboard / Upload / Copilot / Admin)      |          |
|                      ----------------------------------------------          |
|                                                                              |
+--------------------------------------------------------------------------------------+
```

## Global Components
- **Header**: Contains the Product Logo, Application Title, global loading spinner (for background network requests), and User Profile dropdown (Name, Role, Logout).
- **Sidebar**: Sticky navigation menu. Dynamically renders links based on the user's role (Admin, Manager, or Leadership).
- **Breadcrumbs**: Located above the page title to preserve context (e.g., `Home > Admin > Jira Configuration`).
- **Main Content Area**: The scrollable region where specific route components are mounted.

---

# 5. Navigation Structure

Navigation is strictly role-based. Links to unauthorized sections are completely omitted from the DOM, not just disabled.

## 5.1 Platform Administrator Navigation
```text
Administration
│
├── Identity Mapping
├── Data Quality Issues
├── Jira Configuration
├── Data Uploads
│   ├── Leave Data
│   └── Skill Mapping
└── System Jobs (Manual Analytics Trigger)
```

## 5.2 Delivery Manager Navigation
```text
Workforce
│
├── Team Dashboard
├── AI Copilot
└── Historical Snapshots
```

## 5.3 Leadership Navigation
```text
Executive
│
├── Executive Dashboard
├── Capacity Forecast
└── AI Copilot
```

## 5.4 Shared Navigation Behaviours
- **Entry Page**: Post-login, the user is routed to the topmost allowed item (e.g., Team Dashboard for Managers, Identity Mapping for Admins).
- **Logout**: Triggers immediate session termination and redirects to the public Authentication screen.
- **Session Timeout**: Automatically redirects to the Session Expired screen with the URL preserved for post-login return.

---

# 6. Shared Components

## 6.1 KPI Cards
- **Usage**: Display high-level metrics.
- **Behaviour**: Displays title, primary value, trend indicator (arrow up/down), and an optional Risk Badge. Shows a skeleton loader when data is fetching.

## 6.2 Data Tables
- **Usage**: Present tabular data (Identity Mappings, Data Quality Issues, Engineer Utilization).
- **Behaviour**: Supports client-side sorting, pagination, and a global search input.
- **Empty State**: Displays "No records found."

## 6.3 File Dropzone (Upload)
- **Usage**: Accepting CSV files.
- **Behaviour**: Highlights on drag-over. Displays file name and size upon selection. Validates MIME type on client before upload.

## 6.4 Confirmation Dialog
- **Usage**: Destructive or high-impact actions (e.g., "Confirm Manual Analytics Run").
- **Behaviour**: Modal overlay. Traps focus. Contains Title, Warning Message, Cancel (Secondary), and Confirm (Primary/Danger) buttons.

## 6.5 Error Banners & Toast Messages
- **Usage**: Communicate non-blocking errors or success states.
- **Behaviour**: Toast messages slide in from the top right and auto-dismiss after 5 seconds (Success). Error banners persist at the top of the main content area until dismissed manually.

## 6.6 Background Processing Indicator
- **Usage**: Show that the backend is executing an `AnalyticsRun`.
- **Behaviour**: A small pulsing icon next to the "Last Refreshed" timestamp.

---

# 7. Authentication Screens

## 7.1 Sign-In Screen
- **Purpose**: Public entry point for the application.
- **Intended Users**: Anonymous
- **Layout**: Centered card on a branded background. CUIA Logo, Application Title, and a primary "Sign in with Microsoft Entra ID" button.
- **Primary Actions**: Click Sign-In.
- **Loading State**: Button disables and shows a spinner while exchanging tokens.
- **Error States**: Toast message: "Authentication failed. Please try again."

## 7.2 Session Expired / Unauthorized Screen
- **Purpose**: Handle expired JWTs or 403 Forbidden errors.
- **Layout**: Centered card. Warning Icon.
- **Primary Actions**: "Return to Login" or "Return to Dashboard".

---

# 8. Platform Administrator Screens

## 8.1 Jira Configuration
- **Purpose**: Connect CUIA to Jira.
- **Intended Users**: Platform Administrator
- **Entry Conditions**: Authenticated Admin.
- **Layout**: Form layout inside Main Content Area.
- **Components Present**: Text inputs for Jira URL, Project Keys, and Service Account Token (masked). "Test Connection" and "Save Configuration" buttons.
- **Validation Behaviour**: Client-side required field checks.
- **Success/Error States**: Toast message on successful save. Error banner if connection test fails.

## 8.2 Data Uploads (Leave & Skills)
- **Purpose**: Import operational CSV data.
- **Intended Users**: Platform Administrator
- **Layout**: Split view. Top half: File Dropzone and "Download Template" link. Bottom half: Validation Results Table.
- **Primary Actions**: "Upload File", "Commit Data".
- **Validation Behaviour**: If backend rejects rows, the Validation Results Table displays the exact row numbers and error reasons (e.g., "Missing Column"). "Commit Data" is disabled until validation passes.

## 8.3 Identity Mapping
- **Purpose**: Map Jira Account IDs to Entra IDs.
- **Intended Users**: Platform Administrator
- **Layout**: Data Table. Columns: Jira ID, Jira Name, Suggested Entra ID, Action.
- **Primary Actions**: "Confirm Mapping", "Search Directory".
- **Related Upstream Documents**: `USER_FLOWS.md` (Flow 7.3).

## 8.4 Data Quality Resolution
- **Purpose**: View and resolve malformed operational records.
- **Intended Users**: Platform Administrator
- **Layout**: Data Table. Columns: Issue Type, Description, Jira Key, Status.
- **Primary Actions**: "Re-validate Selected".
- **Empty State**: "No data quality issues detected. System health is optimal."

## 8.5 System Jobs (Manual Analytics Trigger)
- **Purpose**: Monitor the background worker and force an immediate `AnalyticsRun`.
- **Intended Users**: Platform Administrator
- **Layout**: Status Card (Last Run Time, Status) + Action Panel.
- **Primary Actions**: "Trigger Analytics Run Now".
- **Validation Behaviour**: Confirmation dialog required to prevent accidental heavy loads.

---

# 9. Delivery Manager Screens

## 9.1 Team Dashboard
- **Purpose**: Review workforce health for assigned teams.
- **Intended Users**: Delivery Manager
- **Entry Conditions**: Authenticated Manager.
- **Layout**: Top row: KPI Cards. Middle row: Utilization Trend Chart (Left), Recommendations Panel (Right). Bottom row: Engineer Utilization Data Table.
- **Primary Actions**: Change Time Filter (Current Sprint vs. Trailing 30 Days).
- **Permissions**: Hard-filtered to the user's `team_id`.
- **Loading State**: Skeleton loaders for all widgets while fetching Snapshots.
- **Data Quality State**: If issues exist, a subtle warning banner appears: "Some metrics may be incomplete due to unresolved Data Quality issues."

## 9.2 AI Copilot
- **Purpose**: Natural language querying of Snapshots.
- **Intended Users**: Delivery Manager, Leadership
- **Layout**: Split view. Left: Suggested Prompts. Right: Chat Window (Message History + Input Box).
- **Primary Actions**: "Send Message", "Clear Chat".
- **Error States**: If the LLM times out or rejects a prompt injection, the chat bubble displays the error gracefully.

---

# 10. Leadership Screens

## 10.1 Executive Dashboard
- **Purpose**: View organization-wide trends and capacity gaps.
- **Intended Users**: Leadership
- **Layout**: Top row: Org KPI Cards. Middle row: Team Comparison Bar Chart. Bottom row: Risk Heatmap and Strategic Recommendations.
- **Permissions**: Displays aggregated organizational data. No operational drill-downs.

## 10.2 Capacity Forecast
- **Purpose**: Long-term workforce planning.
- **Intended Users**: Leadership
- **Layout**: Line chart displaying Capacity vs. Predicted Demand over the next 3 months, highlighting the Capacity Gap.

---

# 11. Shared Screens

## 11.1 404 Not Found & 500 Server Error
- **Purpose**: Handle invalid routes and fatal backend crashes.
- **Layout**: Minimal centered layout. Friendly messaging. Primary action: "Return to Home".

## 11.2 AI Service Unavailable
- **Purpose**: Graceful degradation when the LLM provider fails.
- **Layout**: Replaces the Chat Window with a placeholder: "The Workforce Copilot is currently unavailable. Dashboards remain fully operational."

---

# 12. Responsive Behaviour

- **Desktop (1024px+)**: Sidebar is permanently expanded. Charts display full legends. Data tables show all columns.
- **Tablet (768px - 1023px)**: Sidebar collapses to icons only. Charts stack vertically if necessary.
- **Mobile (< 768px)**: The POC does not optimize complex dashboards for mobile. Navigation is hidden behind a hamburger menu. Tables become horizontally scrollable.

---

# 13. UI States

Every screen component must handle the following explicit states:
- **Loading**: Skeleton loaders for widgets; spinners for buttons.
- **Empty**: Informative messages guiding the user to the next action (e.g., "No records found").
- **Success**: Green toast notifications confirming data mutations.
- **Validation Error**: Red text below form inputs or inline within tables.
- **System Error**: Red banners for network timeouts or 5xx responses.
- **Unauthorized**: Components the user lacks permission for are completely omitted from the DOM (not disabled/greyed out).
- **Data Quality Degradation**: Yellow warning banners on dashboards indicating partial data.

---

# 14. Screen Navigation Summary

The following dictates every valid route transition:

| Origin Screen | Action / Trigger | Destination Screen | Role Restriction |
| :--- | :--- | :--- | :--- |
| **Authentication** | Valid Login | Default Role Dashboard | None |
| **Admin Dashboard** | Click "Uploads" | CSV Uploads | Platform Admin |
| **Admin Dashboard** | Click "Mappings" | Identity Mappings | Platform Admin |
| **Admin Dashboard** | Click "Jobs" | System Jobs | Platform Admin |
| **Team Dashboard** | Click "Copilot" | AI Copilot | Manager |
| **Exec Dashboard** | Click "Forecast" | Capacity Forecast | Leadership |
| **Any Screen** | Session Timeout | Session Expired | None |
| **Any Screen** | Direct URL to forbidden route | Unauthorized (403) | Enforced by Route Guard |

---

# 15. Conclusion

This `WIREFRAMES.md` UI Blueprint Specification defines the complete visual structure, information architecture, and interaction states for the Capacity & Utilization Intelligence Agent (CUIA) Proof of Concept.

By explicitly removing unauthorized actions (like Delivery Manager CSV uploads and Notifications) and introducing the complete Platform Administrator module, this specification ensures absolute alignment with the frozen upstream requirements (`USER_FLOWS.md`, `SECURITY.md`, `ARCHITECTURE.md`).

UX Designers can now construct high-fidelity mockups with absolute confidence in the component requirements. Frontend Developers can construct the React router, layout shells, and state management logic without inventing UI behaviour. 

Detailed React implementations, CSS styling, API integrations, and deployment strategies are deferred to the final `IMPLEMENTATION_PLAN.md`.

---
# End of Document