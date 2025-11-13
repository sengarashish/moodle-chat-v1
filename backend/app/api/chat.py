"""
Chat API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from loguru import logger

from app.services.agent_service import AgentService

router = APIRouter()
agent_service = AgentService()


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    history: Optional[List[Dict[str, str]]] = []
    user_age: Optional[int] = None
    llm_provider: Optional[str] = None
    api_key: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    content: str
    sources: List[str] = []
    route: str
    model: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message

    Args:
        request: Chat request with message and optional history

    Returns:
        AI response with sources
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        logger.info(f"Chat request: {request.message[:100]}...")

        # Process through agent
        result = await agent_service.process_query(
            query=request.message,
            history=request.history,
            user_age=request.user_age
        )

        return ChatResponse(**result)

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
