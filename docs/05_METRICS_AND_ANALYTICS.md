# 5. Metrics & Analytics

This document is the authoritative reference for every metric calculated by CUIA. 
**Crucial Architecture Note:** The LLM *never* computes these metrics. The `AnalyticsEngine` calculates them deterministically based on configuration values defined in `config/analytics_rules.json` and `config/priority_weights.json`.

## Core Mathematical Formulas

### 1. Utilization

**Business Meaning:** How much of an engineer's or team's available time is spent logging actual work.

- **Source Fields:** `Issue.loggedHours`, `Engineer.effectiveCapacity`
- **Configuration:** `sprint_duration_weeks` (default: 2)

**Formula (Engineer):**
```text
Utilization (%) = 
  Sum of loggedHours for all issues in current sprint
  --------------------------------------------------- × 100
  (effectiveCapacity × sprint_duration_weeks)
```

**Formula (Team / Organization):**
```text
Utilization (%) = 
  Sum of all members' loggedHours
  ------------------------------- × 100
  Sum of all members' capacity
```
_Note: CUIA aggregates by **Sum of Totals**, not an average of individual percentages. This prevents mathematical distortion when capacities vary._

### 2. Velocity (Story Points)

**Business Meaning:** The raw output of completed agile story points.

- **Source Fields:** `Issue.storyPoints`, `Issue.status` (must be in `resolved_statuses`)

**Formula (Engineer):**
```text
Velocity = Sum of storyPoints for all resolved issues in current sprint
```

### 3. Productivity Score

**Business Meaning:** A weighted measure of output that values high-priority work over low-priority work.

- **Source Fields:** `Issue.storyPoints`, `Issue.priority`
- **Configuration:** `priority_weights.json` (e.g., Critical=8, High=5, Medium=3, Low=1)

**Formula (Engineer):**
```text
Productivity = Sum(storyPoints × Priority Weight) for all resolved issues
```

### 4. Estimation Accuracy

**Business Meaning:** How closely the logged effort matches the original estimate.

- **Source Fields:** `Issue.loggedHours`, `Issue.originalEstimate`

**Formula (Engineer):**
```text
Accuracy (%) = 
  100 - ( |Sum(loggedHours) - Sum(originalEstimate)| / Max(1, Sum(originalEstimate)) × 100 )
```
_Capped at a minimum of 0%._

### 5. Health Score

**Business Meaning:** A holistic 0-100 score reflecting team or engineer operational health, balancing output against risk factors.

- **Source Fields:** Utilization, Productivity, Velocity, Estimation Accuracy, Active Critical Issues, Blocked Issues
- **Configuration:** `health_rules.json` (weights and penalties)

**Formula (Engineer):**
```text
Health Score = 
  (Capacity Balance Score × weight) +
  (Utilization Score × weight) +
  (Normalized Productivity Score × weight) +
  (Normalized Velocity Score × weight) +
  (Estimation Accuracy × weight) -
  (Critical Issues × Penalty) -
  (Blocked Issues × Penalty)
```
_Note: Team health is the mathematical average of member health scores._

### 6. Burnout Risk

**Business Meaning:** An indicator of engineers working dangerously beyond capacity or under extreme stress from critical issues.

- **Configuration:** `analytics_rules.json` (`high_utilization_percent`, `high_critical_issues`)

**Logic:**
```text
IF utilization > high_utilization_percent (e.g., 110%) 
   OR critical_issues > high_critical_issues:
   Risk = "High"
ELSE IF utilization > medium_utilization_percent (e.g., 90%):
   Risk = "Medium"
ELSE:
   Risk = "Low"
```

### 7. Average Resolution Time

**Business Meaning:** The average hours taken to resolve an issue from start to finish.

- **Source Fields:** `Issue.startedTime`, `Issue.resolvedTime` (ISO strings)

**Formula:**
```text
Resolution Time (hours) = Average of (resolvedTime - startedTime) for all resolved issues
```

### 8. Dependency Risk / SPOF (Single Point of Failure)

**Business Meaning:** The count of unique critical skills within a team (or org) that are possessed by exactly one engineer.

- **Source Fields:** `Engineer.primarySkills`

**Logic:**
Count occurrences of each skill in a team. If a skill appears exactly 1 time, it is a SPOF. The team's `dependencyRisk` is the total count of such skills.

## Metric Traceability Example

How a Team's Utilization appears on the Dashboard:
1. **Dataset:** `Issue` 1 has 40 `loggedHours`. `Issue` 2 has 20 `loggedHours`. Both belong to Engineer A.
2. **Dataset:** Engineer A has an `effectiveCapacity` of 32.
3. **AnalyticsEngine:** Computes Engineer A's sprint capacity: `32 × 2 weeks = 64`.
4. **AnalyticsEngine:** Computes Engineer A's utilization: `(60 / 64) × 100 = 93.75%`.
5. **AnalyticsEngine:** Rolls this up with Engineer B to compute the Team Utilization.
6. **API:** Returns JSON containing `"utilization": 93.75` for the team.
7. **React Component:** Renders the radial progress chart using the exact JSON value.
