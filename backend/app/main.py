from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analytics, dashboard, recommendations, reports, copilot
from app.services.dataset_loader import DatasetLoader

app = FastAPI(title="CUIA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    import os
    # Load dataset into memory on startup
    DatasetLoader.get_dataset()
    
    # AI Startup Validation
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("AI Startup Validation Failed: GEMINI_API_KEY environment variable is not set.")
        
    try:
        from app.ai.graph import CopilotGraph
        graph = CopilotGraph()
        if not graph.llm:
            raise RuntimeError("AI Startup Validation Failed: Failed to initialize Gemini LLM.")
        if not graph.app:
            raise RuntimeError("AI Startup Validation Failed: Failed to compile LangGraph workflow.")
        print("AI Startup Validation: SUCCESS. LangGraph and Gemini client initialized.")
    except Exception as e:
        raise RuntimeError(f"AI Startup Validation Failed: {str(e)}")

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/health/ai")
def ai_health_check():
    import os
    try:
        from app.ai.graph import CopilotGraph
        api_key_loaded = bool(os.getenv("GEMINI_API_KEY"))
        graph = CopilotGraph() if api_key_loaded else None
        
        return {
          "status": "healthy" if (api_key_loaded and graph and graph.llm) else "unhealthy",
          "provider": "Google Gemini",
          "sdk": "langchain-google-genai 4.3.1",
          "model": "gemini-2.0-flash",
          "api_key_loaded": api_key_loaded,
          "langgraph_initialized": bool(graph and graph.app),
          "tools_registered": 5
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(recommendations.router, prefix="/api", tags=["Recommendations"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(copilot.router, prefix="/api", tags=["Copilot"])
