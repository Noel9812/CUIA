from fastapi import APIRouter
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter()

@router.get("/recommendations")
def get_recommendations():
    recs = RecommendationEngine.get_recommendations()
    return [r.model_dump() for r in recs]
