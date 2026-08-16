# 2. System Architecture

CUIA is built on a strict "deterministic-first" architecture. The business logic lives entirely in standard Python code, ensuring metrics are 100% reproducible and explainable. AI is used solely as a presentation layer.

## Master Architecture Diagram

```mermaid
flowchart TD
    %% Node Styling
    classDef frontend fill:#2563eb,stroke:#1e3a8a,stroke-width:2px,color:#fff;
    classDef backend fill:#059669,stroke:#064e3b,stroke-width:2px,color:#fff;
    classDef ai fill:#7c3aed,stroke:#4c1d95,stroke-width:2px,color:#fff;
    classDef storage fill:#d97706,stroke:#92400e,stroke-width:2px,color:#fff;
    classDef external fill:#be123c,stroke:#881337,stroke-width:2px,color:#fff;

    %% Elements
    UI["💻 Dashboard & Chat UI (React/Vite)"]:::frontend
    
    API["⚙️ FastAPI Routers"]:::backend
    
    subgraph AI ["AI Orchestration (LangGraph)"]
        direction TB
        LG["🧠 Orchestrator"]:::ai
        IC["🎯 Intent Classifier"]:::ai
        EE["🔍 Entity Extractor"]:::ai
        CB["📦 Context Builders"]:::ai
    end
    
    subgraph Analytics ["Deterministic Analytics Layer"]
        direction TB
        AE["📊 Analytics Engine"]:::backend
        FE["📈 Forecast Engine"]:::backend
        RE["💡 Recommendation Engine"]:::backend
        SE["🧪 Simulation Engine"]:::backend
        BRE["⚖️ Business Rules Engine"]:::backend
    end
    
    subgraph Data ["Data & Configuration"]
        direction LR
        DS[("dataset.json")]:::storage
        CFG[("Config JSONs")]:::storage
    end
    
    LLM["☁️ AWS Bedrock"]:::external

    %% Routing
    UI <-->|1. HTTP / JSON| API
    
    %% Dashboard Flow
    API <-->|2a. Get Dashboard Data| AE
    AE <-->|Apply Rules| BRE
    
    %% Copilot Flow
    API <-->|2b. Chat Query / Response| LG
    
    LG <-->|Classify| IC
    LG <-->|Extract| EE
    LG <-->|Route| CB
    
    CB <-->|Fetch Analytics| AE
    CB <-->|Fetch Forecasts| FE
    CB <-->|Fetch Recs| RE
    CB <-->|Run Scenario| SE
    
    %% Data Loading
    AE -.->|Loads| DS
    BRE -.->|Loads| CFG
    
    %% LLM Execution
    LG <-->|3. Prompt + JSON Context| LLM
```

## Core Subsystems

### 1. Frontend (React)
- **Responsibility:** Provides the UI for Dashboards (Leadership and DM) and the AI Copilot chat interface.
- **Key Files:** `src/pages/LeadershipDashboard.tsx`, `src/pages/DeliveryDashboard.tsx`, `src/pages/Copilot.tsx`

### 2. FastAPI API Layer
- **Responsibility:** Handles HTTP requests, enforces initial routing, and acts as the bridge to backend services.
- **Key Files:** `app/main.py`, `app/api/dashboard.py`, `app/api/copilot.py`

### 3. Deterministic Analytics Layer
- **Responsibility:** The computational heart of CUIA. Computes all metrics (utilization, health, velocity) from raw data. **Never uses AI.**
- **Key Files:** `app/services/analytics_engine.py`, `app/services/business_rules_engine.py`

### 4. AI Orchestration Layer (LangGraph)
- **Responsibility:** Processes natural language questions. It uses deterministic intent classification and entity extraction to figure out what the user wants. It then builds a narrow context payload from the Analytics Layer and sends it to the LLM for explanation.
- **Key Files:** `app/ai/graph.py`, `app/ai/intent_classifier.py`, `app/ai/entity_extractor.py`, `app/ai/context_builders.py`

### 5. AWS Bedrock (LLM)
- **Responsibility:** Generates human-readable explanations based *strictly* on the injected JSON context.
- **Key Files:** `app/ai/bedrock_client.py`

### 6. Data & Configuration Layer
- **Responsibility:** Loads and caches the simulated Jira dataset and JSON-based business rules.
- **Key Files:** `app/services/dataset_loader.py`, `app/core/config_loader.py`
