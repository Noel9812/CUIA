# 11. Configuration and Business Rules

All thresholds, weights, and business parameters in CUIA are abstracted out of the Python code and into JSON configuration files. This ensures that non-engineers can adjust the definition of "Health" or "Burnout" without requiring a code deployment.

The `ConfigLoader` service (`app/core/config_loader.py`) loads and caches these files on startup.

## 1. analytics_rules.json

Defines core operational parameters.
- `sprint_duration_weeks`: (default: 2) Used to calculate sprint capacity from weekly capacity.
- `active_issue_statuses`: `["To Do", "In Progress", "Blocked", "In Review"]`
- `resolved_issue_statuses`: `["Done", "Closed"]`
- `blocked_status`: `"Blocked"`
- `burnout_thresholds`:
  - `high_utilization_percent`: (e.g., 110)
  - `high_critical_issues`: (e.g., 3)
  - `medium_utilization_percent`: (e.g., 90)
- `utilization_thresholds`:
  - `forecast_risk_above_percent`: (e.g., 100)

## 2. priority_weights.json

Defines the mathematical value assigned to Jira priorities for calculating the Productivity Score.
```json
{
  "Critical": 8,
  "High": 5,
  "Medium": 3,
  "Low": 1
}
```

## 3. health_rules.json

Defines the weights and penalties used to compute the 0-100 Health Score.

- **Weights (Must sum to 1.0 ideally):**
  - `capacity_balance`: (e.g., 0.25) Rewards being near 100% utilization (neither over nor under).
  - `productivity`: (e.g., 0.25)
  - `velocity`: (e.g., 0.25)
  - `estimation_accuracy`: (e.g., 0.15)
  - `dependency_risk`: (e.g., 0.10)
- **Penalties (Subtracted directly from score):**
  - `critical_issue_deduction_per_issue`: (e.g., 5 points)
  - `blocked_issue_deduction_per_issue`: (e.g., 5 points)

## Changing Configuration

To change a business rule:
1. Modify the JSON file in `backend/config/`.
2. Restart the backend service to clear the `ConfigLoader` cache and trigger a re-computation in the `AnalyticsEngine`.
