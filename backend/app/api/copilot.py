"""Copilot API routes."""

import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.ai.graph import CopilotGraph

logger = logging.getLogger("cuia.api.copilot")

router = APIRouter()
graph = CopilotGraph()


@router.post("/copilot/chat", response_model=ChatResponse)
def chat_copilot(request: ChatRequest):
    """Handle AI copilot chat requests."""
    try:
        if not graph.bedrock.is_available:
            raise HTTPException(
                status_code=503,
                detail={
                    "error_type": "ServiceUnavailable",
                    "message": "AI service is not available. Check AWS Bedrock configuration."
                }
            )
        
        logger.info("Copilot chat: persona=%s, question_length=%d", request.persona, len(request.question))
        answer = graph.chat(request.question, request.persona)
        
        # Detect and structure errors from graph.chat
        if answer.startswith("Error communicating with AI:"):
            error_str = answer.replace("Error communicating with AI: ", "")
            
            if "authentication" in error_str.lower() or "AccessDenied" in error_str:
                raise HTTPException(status_code=401, detail={"error_type": "AuthenticationError", "message": error_str})
            elif "ThrottlingException" in error_str or "rate limit" in error_str.lower():
                raise HTTPException(status_code=429, detail={"error_type": "RateLimit", "message": error_str})
            elif "timeout" in error_str.lower():
                raise HTTPException(status_code=504, detail={"error_type": "Timeout", "message": error_str})
            else:
                raise HTTPException(status_code=500, detail={"error_type": "AIServiceError", "message": error_str})
        
        return ChatResponse(answer=answer)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Copilot error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={"error_type": "CopilotError", "message": str(e)}
        )
