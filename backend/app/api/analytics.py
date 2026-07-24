from fastapi import APIRouter
from app.services.analytics_engine import AnalyticsEngine

router = APIRouter()

@router.get("/analytics")
def get_analytics():
    return AnalyticsEngine.get_analytics()
