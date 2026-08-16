# 15. Engineering Learnings

Building the CUIA POC revealed several critical lessons regarding the intersection of enterprise analytics and Generative AI.

## 1. LLMs Cannot Do Math on Tabular Data
Early iterations attempted to pass raw CSV/JSON data to the LLM and asked it to "calculate the utilization." This failed consistently. LLMs hallucinate numbers, fail at basic division, and struggle with multi-step aggregations across large contexts.
- **Learning:** Never let the AI own the business truth. Offload all calculations to deterministic, unit-tested code (the `AnalyticsEngine`). Pass the *final results* to the LLM for explanation.

## 2. Aggregation Pitfalls
A major bug discovered during the audit involved how organizational utilization was calculated. Initially, the system took the average of each individual team's utilization percentage. This distorted the math when teams had vastly different capacities.
- **Learning:** Ratios (like utilization) must be calculated from the "sum of the totals" (Sum of all Logged Hours / Sum of all Capacity), not the average of the ratios.

## 3. The Power of Deterministic Intent Routing
We initially used an LLM agent to decide which tool to call based on the user's prompt. This added 500ms+ of latency and cost money for every single chat message, even greetings.
- **Learning:** 90% of queries can be classified using a robust, weighted keyword taxonomy and regex. Reserving the LLM only for ambiguous intent fallbacks drastically reduced latency and cost.

## 4. Persona Isolation Must Happen Before the Prompt
You cannot rely on the LLM to filter data based on system prompts (e.g., "Only talk about Team Alpha").
- **Learning:** Security must be enforced at the Python/data layer. The Context Builders physically remove unauthorized data from the JSON payload before it ever reaches the Bedrock API.

## 5. Configuration-Driven Business Rules
Hardcoding thresholds (e.g., `utilization > 100%`) in the UI or Python scripts caused synchronization issues between the API, the Frontend, and the AI.
- **Learning:** Extracting all business rules into `config.json` files ensured a single source of truth that governed the entire stack simultaneously.
