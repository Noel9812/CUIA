# 5. Metrics & Analytics (Implementation Trace)

This document is the exhaustive, implementation-level reference for every metric calculated by CUIA. It documents what the code actually does, what configurations are used, and traces the data lineage exactly from `dataset.json`.

**Source of Truth:** 
- Code: `backend/app/services/analytics_engine.py`
- Configuration: `backend/app/config/analytics_rules.json`, `health_rules.json`, `priority_weights.json`
- Data: `backend/sample_data/dataset.json`

---

## CORE METRICS

### 1. Utilization

1. **Business Meaning:** How much of an engineer's or team's available time is spent logging actual work.
2. **Why CUIA Uses It:** To identify idle capacity or dangerous overloading.
3. **Source Data:** `issue.loggedHours`, `engineer.effectiveCapacity`
4. **Source of Each Value:** 
   - `dataset.json -> issues` (filtered to current sprint)
   - `dataset.json -> engineers`
5. **Calculation:**
   ```text
   Utilization (%) = 
       Sum(loggedHours)
       --------------------------------------------- × 100
       (effectiveCapacity × sprint_duration_weeks)
   ```
6. **Implementation:** 
   `backend/app/services/analytics_engine.py` -> `AnalyticsEngine._compute_engineer_metrics()`
7. **Step-by-Step Calculation:**
   - Step 1: Find all `issues` assigned to Engineer X.
   - Step 2: Sum `loggedHours` across all those issues.
   - Step 3: Multiply Engineer X's `effectiveCapacity` by `sprint_duration_weeks`.
   - Step 4: Divide the total logged hours by the total sprint capacity.
   - Step 5: Multiply by 100.
8. **Configuration:** 
   - `sprint_duration_weeks` (from `analytics_rules.json`, currently `2`). It defines how many weeks are in a sprint to calculate total capacity. If changed to `3`, utilization percentages would drop as the denominator increases.
9. **Edge Cases:**
   - *Zero Capacity:* If `effectiveCapacity` is 0, utilization is hardcoded to return `0.0` to avoid division by zero.
   - *Missing Values:* Null `loggedHours` are treated as `0`.
   - *Utilization > 100%:* Can and does occur. It is not capped at 100%, allowing for accurate burnout detection.
10. **Aggregation:** 
    - **Engineer to Team:** RATIO OF TOTALS. 
      `Team Utilization = Sum(All Members' Logged Hours) / Sum(All Members' Capacity) × 100`
    - *Why not average?* Averaging individual utilizations creates statistical distortion if engineers have different base capacities (e.g., part-time vs full-time). CUIA strictly uses sum-based ratios.
11. **Worked Example (from dataset.json):**
    - **Engineer:** Grace (`eng-5`)
    - **Capacity:** `effectiveCapacity` = 40. Sprint capacity = 40 × 2 = 80 hours.
    - **Logged:** Assumes she logged 60 hours across her tickets.
    - **Result:** (60 / 80) × 100 = 75.0%
12. **Dashboard Output:** Radial charts in `TeamDetails.tsx`.
13. **Copilot Output:** `ContextBuilder._build_dm_analytics()` includes this in the LLM JSON payload.
14. **Validation:** `tests/audit/dashboard_oracle.py` re-calculates this from scratch to prove the API returns the exact mathematical truth.

---

### 2. Productivity Score

1. **Business Meaning:** A weighted measure of output valuing high-priority work.
2. **Why CUIA Uses It:** To distinguish between an engineer completing 10 trivial tickets vs 1 critical ticket.
3. **Source Data:** `issue.storyPoints`, `issue.priority`, `issue.status`
4. **Source of Each Value:** `dataset.json -> issues`
5. **Calculation:**
   ```text
   Productivity = Sum(storyPoints × PriorityWeight) for all resolved issues
   ```
6. **Implementation:** `AnalyticsEngine._compute_engineer_metrics()`
7. **Step-by-Step Calculation:**
   - Step 1: Filter issues to only those in `resolved_issue_statuses` (e.g., "Done").
   - Step 2: Multiply each issue's `storyPoints` by the value in `priority_weights.json` matching its `priority`.
   - Step 3: Sum the results.
8. **Configuration:** 
   - `priority_weights.json` (Critical: 8, High: 5, Medium: 3, Low: 1).
   - `resolved_issue_statuses` (from `analytics_rules.json`).
9. **Edge Cases:** Unestimated tickets (0 points) add 0 to productivity, regardless of priority.
10. **Aggregation:** 
    - **Engineer to Team:** SUM. `Team Productivity = Sum(All Members' Productivity)`

---

## HEALTH SCORE (Deep Explanation)

The Health Score is a composite metric combining positive operational output with negative risk penalties.

**Implementation File:** `health_rules.json` and `AnalyticsEngine._compute_engineer_metrics()`

### Components

**1. Capacity Balance (Weight: 0.20)**
- *Source:* Engineer Utilization.
- *Formula:* `100 - abs(100 - utilization)`. (e.g., 90% util = 90 pts. 110% util = 90 pts).
- *Contribution:* Rewards being near 100%; heavily penalizes severe over/under utilization.

**2. Utilization (Weight: 0.20)**
- *Source:* Engineer Utilization (capped at 100 for this component).
- *Contribution:* Rewards actual time spent working.

**3. Productivity (Weight: 0.15)**
- *Source:* Productivity Score.
- *Normalization:* `(productivity / max_productivity_benchmark) * 100` (capped at 100).
- *Contribution:* Rewards high-value output.

**4. Velocity (Weight: 0.15)**
- *Source:* Total resolved Story Points.
- *Normalization:* `(velocity / max_velocity_benchmark_sp) * 100` (capped at 100).

**5. Estimation Accuracy (Weight: 0.10)**
- *Formula:* `100 - (abs(Logged - Estimate) / Estimate * 100)`.

**6. Dependency Risk (Weight: 0.10)**
- *Source:* Spof evaluation. Max points (100) if no single points of failure exist.

### Penalties (Flat Deductions)
- **Critical Issues:** `critical_issues * critical_issue_deduction_per_issue` (Configured as 20).
- **Blocked Issues:** `blocked_issues * blocked_issue_deduction_per_issue` (Configured as 20).

### Final Score Calculation
```text
Base Score = (CapBal × 0.20) + (Util × 0.20) + (Prod × 0.15) + (Vel × 0.15) + (EstAcc × 0.10) + (DepRisk × 0.10)
Final Score = Max(0, Base Score - (CriticalIssues × 20) - (BlockedIssues × 20))
```
*Why can a team have high utilization but low health?* If a team is 110% utilized, but has 3 blocked issues (60 point penalty), their health score will crash despite working hard.

---

## BURNOUT RISK

**Implementation:** `AnalyticsEngine._compute_burnout_risk()`
**Configuration:** `analytics_rules.json` (`burnout_thresholds`)

The logic uses strict comparison operators:
```python
if utilization > 110 or critical_count > 2:
    return "High"
elif utilization > 95:
    return "Medium"
return "Low"
```
*Note the strictly greater-than `>` operator.* Exactly 110.0% utilization is "Medium", but 110.1% is "High". Exactly 2 critical issues is "Medium", but 3 is "High".

---

## FORECASTING ENGINE

**Implementation:** `backend/app/services/forecast_engine.py`

**Goal:** Predict capacity shortfalls based on historical trends.

1. **Calculate Historical Velocity:** Uses a simple moving average (configured `window_size` = 3) of past sprint velocities.
2. **Calculate Historical Effort:** Averages `loggedHours / storyPoints` to find the team's historical ratio.
3. **Analyze Backlog:** Sums the points of all "To Do" issues assigned to the next sprint.
4. **Project Shortfall:** `(Backlog Points × Historical Effort Ratio) - Next Sprint Capacity`.
5. **Risk Evaluation:** If Projected Utilization > `forecast_risk_above_percent` (90%), it flags "Risk", else "Balanced".

---

## WHAT-IF / SIMULATION ENGINE

**Implementation:** `backend/app/services/simulation_engine.py`

The Simulation engine operates via strict state-mutation:
1. Performs a deep copy of the `Dataset` object in memory.
2. Applies the requested mutation (e.g., removing an engineer).
3. Reallocates the engineer's active `Issues` to remaining engineers on the same team who share the required `primarySkills`.
4. Re-runs the entire `AnalyticsEngine._compute_team_metrics()` on the mutated dataset.
5. Returns a JSON diff comparing the original metrics to the simulated metrics, which the LangGraph Copilot translates into a natural language impact assessment.

---

## RECOMMENDATION ENGINE

**Implementation:** `backend/app/services/recommendation_engine.py`

Recommendations are entirely deterministic and rule-based. The LLM does *not* invent recommendations.

**Execution:**
1. The engine iterates through configured rules in `recommendation_rules.json`.
2. Rule: `High Burnout`
   - Trigger: `team.burnoutRisk > 0` (Meaning at least 1 engineer has High Burnout).
   - Generated Action: *"Reallocate tickets or extend sprint deadline to alleviate high burnout risk."*
3. Rule: `Blocked Flow`
   - Trigger: `team.blockedIssues > 3`.
   - Generated Action: *"Schedule an immediate unblocking swarm session."*
4. Output: The raw strings are passed in the JSON context payload to the LLM, which simply repeats/formats them for the user.
