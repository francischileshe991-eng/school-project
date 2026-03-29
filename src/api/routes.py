#!/usr/bin/env python3
"""
API Routes for Zedchatbot.
Defines endpoints for web chat and system health.
"""

from fastapi import APIRouter, HTTPException, status
from src.api.schemas import ChatRequest, ChatResponse
from src.core.logger import logger

router = APIRouter()

@router.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Check if the API server and RAG pipeline are healthy."""
    return {"status": "healthy", "service": "zedchatbot-api"}

@router.get("/", tags=["General"])
def read_root() -> dict[str, str]:
    """Landing page for the API."""
    return {
        "message": "Welcome to the Zedchatbot API!",
        "docs": "/docs",
        "status": "ready"
    }

@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for the web interface.
    Accepts a query, country, and optional language.
    Returns a multilingual RAG-based answer.
    """
    logger.info(f"API: Received chat request from country: {payload.country}")
    
    try:
        from src.rag.pipeline import generate_reply

        # Pass request to the Smart RAG Pipeline
        answer, sources = generate_reply(
            message=payload.message,
            country=payload.country,
            language=payload.language
        )
        
        return ChatResponse(
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"API Error in /chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your chat request."
        )
