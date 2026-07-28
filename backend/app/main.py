"""
CUIA Backend — Capacity & Utilization Intelligence Agent

A deterministic workforce analytics platform where AI is used only
for natural language understanding and explanation. All analytics,
recommendations, forecasting, and simulations are computed by
deterministic Python services from dataset.json.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging
from app.services.dataset_loader import DatasetLoader
from app.services.analytics_engine import AnalyticsEngine
from app.api import analytics, dashboard, recommendations, reports, copilot, forecast, simulation


# Initialize structured logging
setup_logging()
logger = logging.getLogger("cuia.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown."""
    # ── Startup ──
    logger.info("CUIA Backend starting up...")
    
    # Load and validate dataset
    try:
        dataset = DatasetLoader.get_dataset()
        logger.info(
            "Dataset loaded: %d engineers, %d teams, %d issues.",
            len(dataset.engineers), len(dataset.teams), len(dataset.issues)
        )
    except Exception as e:
        logger.error("Dataset loading failed: %s", str(e))
        raise RuntimeError(f"Startup failed: Dataset loading error — {str(e)}")
    
    # Pre-compute analytics
    try:
        analytics_data = AnalyticsEngine.get_analytics()
        logger.info("Analytics pre-computed: %d engineers, %d teams.",
                     len(analytics_data.get("engineers", [])),
                     len(analytics_data.get("teams", [])))
    except Exception as e:
        logger.error("Analytics computation failed: %s", str(e))
        raise RuntimeError(f"Startup failed: Analytics computation error — {str(e)}")
    
    # Validate AI availability (non-blocking for POC)
    try:
        from app.ai.bedrock_client import BedrockClient
        client = BedrockClient()
        if client.is_available:
            logger.info("AI service available: AWS Bedrock (%s)", client.model_id)
        else:
            logger.warning("AI service unavailable. Copilot will not function.")
    except Exception as e:
        logger.warning("AI initialization warning: %s", str(e))
    
    logger.info("CUIA Backend startup complete.")
    
    yield
    
    # ── Shutdown ──
    logger.info("CUIA Backend shutting down.")


app = FastAPI(
    title="CUIA API",
    version="2.0.0",
    description="Capacity & Utilization Intelligence Agent — Deterministic Analytics Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health endpoints ──

@app.get("/api/health")
def health_check():
    """Basic health check."""
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/api/health/ai")
def ai_health_check():
    """AI service health check."""
    try:
        from app.ai.bedrock_client import BedrockClient
        client = BedrockClient()
        health = client.get_health()
        health["tools_registered"] = 5
        return health
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/api/health/data")
def data_health_check():
    """Dataset and analytics health check."""
    try:
        dataset = DatasetLoader.get_dataset()
        
        from app.core.data_validator import DataValidator
        errors = DataValidator.validate(dataset)
        critical = [e.to_dict() for e in errors if e.severity == "error"]
        warnings = [e.to_dict() for e in errors if e.severity == "warning"]
        
        return {
            "status": "healthy" if not critical else "degraded",
            "dataset": {
                "engineers": len(dataset.engineers),
                "teams": len(dataset.teams),
                "issues": len(dataset.issues),
                "deliveryManagers": len(dataset.deliveryManagers),
            },
            "validation": {
                "errors": len(critical),
                "warnings": len(warnings),
                "details": critical[:5] if critical else [],
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# ── Register routers ──

app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(recommendations.router, prefix="/api", tags=["Recommendations"])
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(copilot.router, prefix="/api", tags=["Copilot"])
app.include_router(forecast.router, prefix="/api", tags=["Forecast"])
app.include_router(simulation.router, prefix="/api", tags=["Simulation"])
