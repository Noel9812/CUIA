# 10. Testing and Validation

CUIA enforces rigorous validation of both its data determinism and its AI logic. The project differentiates between **Consistency** (does the UI match the API?) and **Correctness** (does the API match the math?).

## 1. Independent Mathematical Oracle

To prove correctness, the project uses a separate, independent `DashboardOracle` test suite.
Instead of asserting against static "expected" JSON values (which could hide bugs), the Oracle:
1. Loads `dataset.json`.
2. Reads the configuration rules (`config/`).
3. Manually iterates over the dataset in raw Python to calculate Utilization, Health, and Velocity.
4. Compares its manual, independent calculation against the `AnalyticsEngine` output.

If `Oracle Calculation == AnalyticsEngine Calculation`, the formulas are proven correct.

## 2. Hardcoding Validation

Automated tests scan the backend JSON responses to ensure no "mock" data strings or hardcoded percentages exist. Every number served by the API is proven to have been derived dynamically from the dataset.

## 3. AI Copilot Test Harness

The AI Copilot is tested using a specialized test harness that evaluates the deterministic pipeline:
1. **Intent Testing:** Verifies that queries map to the correct intent without LLM usage (e.g., "burnout risk" -> "analytics").
2. **Entity Testing:** Verifies that team names and engineer IDs are accurately extracted from natural language strings.
3. **Persona Security Testing:** Submits queries acting as `dm-1` requesting `dm-2`'s data, and asserts that the `ContextBuilder` produces an empty dataset.
4. **Malicious Testing:** Injects prompt escape strings and asserts that the system instantly categorizes them as malicious without invoking AWS Bedrock.

## 4. End-to-End Validation

The final validation confirms the traceability of data:
`dataset.json` → `AnalyticsEngine` → `Dashboard API` → `React Frontend`

If a user sees 55% Utilization for Team Alpha on the React dashboard, tests prove that value maps perfectly to `(LoggedHours / Capacity) * 100` for Team Alpha's engineers in the dataset.
