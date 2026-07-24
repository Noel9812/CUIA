from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.ai.graph import CopilotGraph

router = APIRouter()
graph = CopilotGraph()

@router.post("/copilot/chat", response_model=ChatResponse)
def chat_copilot(request: ChatRequest):
    try:
        if not graph.llm:
            raise HTTPException(status_code=500, detail={"error_type": "Missing API Key", "message": "GEMINI_API_KEY is not configured on the server."})
            
        answer = graph.chat(request.question, request.persona)
        
        # graph.chat returns a string. If it contains "Error communicating with AI", it was caught inside graph.py.
        # But we want to raise structured HTTP exceptions. Let's raise them here if graph.chat caught an error.
        if answer.startswith("Error communicating with AI:"):
            error_str = answer.replace("Error communicating with AI: ", "")
            if "API key not valid" in error_str:
                raise HTTPException(status_code=401, detail={"error_type": "Invalid API Key", "message": error_str})
            elif "not found" in error_str.lower() or "unsupported model" in error_str.lower():
                raise HTTPException(status_code=400, detail={"error_type": "Unsupported Model", "message": error_str})
            elif "429" in error_str or "quota" in error_str.lower():
                raise HTTPException(status_code=429, detail={"error_type": "Rate Limit", "message": error_str})
            elif "timeout" in error_str.lower():
                raise HTTPException(status_code=504, detail={"error_type": "Timeout", "message": error_str})
            else:
                raise HTTPException(status_code=500, detail={"error_type": "Gemini API Failure", "message": error_str})
                
        return ChatResponse(answer=answer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error_type": "LangGraph Failure", "message": str(e)})
