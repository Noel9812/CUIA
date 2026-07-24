# Capacity & Utilization Intelligence Agent (CUIA)

## Overview
CUIA is a Proof of Concept (POC) demonstrating how engineering workforce data can be transformed into deterministic workforce insights and explained through an AI Copilot. 

The application is built with a highly secure architecture enforcing server-side persona isolation, preventing data leakage across organizational scopes. The AI Copilot uses LangGraph to securely route intent to deterministic backend calculation tools, meaning it strictly functions as an "Explainer" and is forbidden from hallucinating analytics.

## Key Features
- **Persona-Based Scope Isolation:** Real-time data segregation between Leadership (org-wide) and Delivery Managers (team-specific).
- **Deterministic Analytics Engine:** Accurate calculations for capacity, utilization, velocity, and burnout risk.
- **AI Copilot (LangGraph Workflow):** Intent-classified, safe AI interaction backed by Gemini 2.0 Flash. Features token optimization, prompt guardrails, and output validation to prevent hallucinated metrics.
- **Reporting Engine:** Generate daily, weekly, and monthly PDF reports based on active persona scope.
- **Advanced UI/UX:** Built with React, Tailwind CSS, Recharts, and Lucide icons for a premium, accessible user experience.

## Technology Stack
- **Frontend**: React, TypeScript, Tailwind CSS, Recharts, Vite
- **Backend**: FastAPI, Pandas, LangChain/LangGraph, Google Gemini API
- **Infrastructure**: Docker, Docker Compose, Nginx


## Prerequisites
- Docker and Docker Compose
- Google Gemini API Key (Gemini 2.0 Flash or higher recommended)

## Running Locally

1. **Configure Environment Variables:**
   Copy the example environment file and add your Gemini API Key.
   ```bash
   cp .env.example .env
   # Edit .env and paste your GEMINI_API_KEY
   ```

2. **Start the Application:**
   Run the containers using Docker Compose. The backend includes an active health-check that will automatically halt startup if your API key is missing or invalid.
   ```bash
   docker compose up --build
   ```

3. **Access the Application:**
   - **Frontend UI**: http://localhost
   - **API Docs (Swagger)**: http://localhost/api/docs
   - **AI Subsystem Health Check**: http://localhost/api/health/ai

## Security & Rate Limits
- The AI Copilot implements **Token Optimization**, compressing heavy JSON payloads before sending them to the LLM. 
- If you encounter a `429 Too Many Requests` error, the UI will gracefully handle it. This happens if you hit the Free Tier Request Per Minute limit on Google AI Studio. Wait 60 seconds and try again.

## API Endpoints
- `GET /api/analytics`: Raw calculated metrics
- `GET /api/dashboard/leadership`: Organization KPIs
- `GET /api/dashboard/delivery?managerId=dm-1`: Manager-specific KPIs
- `GET /api/recommendations`: AI/Rule-based recommendations
- `GET /api/reports/download/{type}`: Generate Reports (Daily/Weekly/Monthly)
- `POST /api/copilot/chat`: Chat with AI Copilot
- `GET /api/health/ai`: AI System Diagnostic Status
