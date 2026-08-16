# 13. POC Limitations and Future Evolution

The CUIA Proof of Concept successfully demonstrates the viability of a deterministic-first AI workforce analytics platform. However, to transition to a production environment, several limitations must be addressed.

## Current POC Limitations

1. **Static Dataset:** 
   - *POC:* The system reads from a static `dataset.json` loaded at startup.
   - *Production:* Must integrate with live APIs (Jira, Workday, GitHub) via real-time webhooks or scheduled ETL pipelines.
2. **Frontend Persona Declaration:** 
   - *POC:* The user selects their role (`leadership`, `dm-1`) from a dropdown in the UI, and this is trusted by the backend.
   - *Production:* Persona and scope must be derived securely from an authenticated JWT token (e.g., OAuth/OIDC) and cross-referenced with an internal RBAC database.
3. **Simplified Forecasting & Simulations:** 
   - *POC:* The `ForecastEngine` and `SimulationEngine` use basic linear projections and hardcoded heuristic mappings.
   - *Production:* Implement advanced time-series forecasting (e.g., ARIMA) and allow users to define complex, multi-variable what-if scenarios natively in the UI.
4. **Stateless Conversational UI:**
   - *POC:* Conversational context is maintained by the React frontend passing a dictionary back and forth. If the browser refreshes, context is lost.
   - *Production:* Implement a persistent backend session store (e.g., Redis) for chat histories.

## Production Evolution Roadmap

- **Phase 1 (Data Integration):** Build the Jira/HRIS connectors and establish a robust SQL database (e.g., PostgreSQL) replacing the JSON file.
- **Phase 2 (Security):** Implement SSO (Single Sign-On) and backend JWT validation.
- **Phase 3 (Streaming AI):** Implement streaming responses for the Copilot (Server-Sent Events) to improve perceived latency.
- **Phase 4 (Advanced Scenarios):** Upgrade the backend engines to support complex dependency mapping across hundreds of teams.
