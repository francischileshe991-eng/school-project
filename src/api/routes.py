#!/usr/bin/env python3
"""
API Routes for Zedchatbot.
Defines endpoints for web chat, feedback rating, system statistics, and health.
"""

import time
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from src.api.schemas import ChatRequest, ChatResponse, FeedbackRequest, FeedbackResponse
from src.configs.settings import settings
from src.core.database import db
from src.core.exceptions import DatabaseError
from src.core.logger import logger
from src.multilingual.language_detector import detect_language

router = APIRouter()


@router.get("/health", tags=["System"])
def health_check() -> Dict[str, Any]:
    """Check if the API server, database, and vector store are healthy."""
    db_ok = db.ping()
    vector_path_ok = settings.vector_store_full_path.exists()

    if not db_ok:
        logger.error("Health check failed: SQLite database ping failed.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "zedchatbot-api",
                "database": "disconnected",
                "vector_store": "ready" if vector_path_ok else "missing",
            },
        )

    return {
        "status": "healthy",
        "service": "zedchatbot-api",
        "database": "connected",
        "vector_store": "ready" if vector_path_ok else "missing",
    }


from fastapi.responses import RedirectResponse

@router.get("/", tags=["General"], include_in_schema=False)
def read_root() -> RedirectResponse:
    """Redirects visitors from root directly to the web application."""
    return RedirectResponse(url="/app/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for the web interface.
    Accepts a query, country, and optional language.
    Returns a multilingual RAG-based answer and logs the interaction.
    """
    start_time = time.perf_counter()

    # Auto-detect language if not explicitly provided or if 'auto'
    req_lang = payload.language
    if not req_lang or req_lang.lower() == "auto":
        detected_lang = detect_language(payload.message)
    else:
        detected_lang = req_lang.lower()

    logger.info(
        f"API: Received chat request for country '{payload.country}', "
        f"requested lang '{payload.language}' -> resolved '{detected_lang}'"
    )

    try:
        from src.rag.pipeline import generate_reply

        # Execute the RAG Pipeline passing resolved detected_lang
        answer, sources = generate_reply(
            message=payload.message,
            country=payload.country,
            language=detected_lang,
        )

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        # Log interaction to SQLite database for evaluation & TAM metrics
        interaction_id = db.log_interaction(
            channel=payload.channel,
            country=payload.country,
            user_query=payload.message,
            detected_language=detected_lang,
            retrieved_sources=sources,
            response=answer,
            response_time_ms=elapsed_ms,
        )

        return ChatResponse(
            answer=answer,
            response=answer,
            sources=sources,
            interaction_id=interaction_id,
            response_time_ms=elapsed_ms,
        )

    except Exception as e:
        logger.error(f"API Error in /chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your chat request.",
        )


@router.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
def feedback_endpoint(payload: FeedbackRequest) -> FeedbackResponse:
    """
    Records user feedback (1 to 5 rating, optional comment) for a specific interaction.
    Enables quantitative and qualitative evaluation as specified in the project proposal.
    """
    logger.info(
        f"API: Received feedback for interaction #{payload.interaction_id}: rating={payload.rating}"
    )

    try:
        success = db.record_feedback(
            interaction_id=payload.interaction_id,
            rating=payload.rating,
            feedback_comment=payload.comment,
        )
    except DatabaseError as dbe:
        logger.error(f"API Database Error in /feedback: {dbe}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while saving feedback.",
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interaction ID #{payload.interaction_id} not found.",
        )

    return FeedbackResponse(
        status="success",
        message="Thank you for your feedback!",
    )


@router.get("/stats", tags=["System"])
def stats_endpoint() -> Dict[str, Any]:
    """Returns aggregated interaction and feedback statistics for evaluation reporting."""
    return db.get_stats()

