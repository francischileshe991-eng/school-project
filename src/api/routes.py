#!/usr/bin/env python3
"""
API Routes for Zedchatbot.
Defines endpoints for web chat, feedback rating, system statistics, and health.
"""

import csv
import io
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import Response
from src.api.schemas import ChatRequest, ChatResponse, FeedbackRequest, FeedbackResponse
from src.configs.settings import settings
from src.core.database import db
from src.core.exceptions import DatabaseError
from src.core.logger import logger
from src.multilingual.language_detector import detect_language

router = APIRouter()


def _to_local_timestamp(ts: Optional[str]) -> str:
    """Converts a SQLite UTC timestamp ('YYYY-MM-DD HH:MM:SS') to server local time."""
    if not ts:
        return ""
    try:
        dt = datetime.strptime(str(ts), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


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


def _api_key_configured(key: Optional[str]) -> bool:
    """Returns True when an API key is present and not a placeholder."""
    return bool(key) and "your_" not in key.lower()


@router.get("/v1/models", tags=["System"])
def list_models() -> Dict[str, Any]:
    """
    OpenAI-compatible model listing.
    Reports the models configured for the current provider cascade
    (kept for external monitoring/discovery clients).
    """
    models: list = [
        {"id": settings.MODEL_NAME, "object": "model", "owned_by": "ollama (local)"},
    ]
    if _api_key_configured(getattr(settings, "GOOGLE_API_KEY", None)):
        models.extend(
            [
                {"id": settings.GEMINI_MODEL, "object": "model", "owned_by": "google"},
                {"id": settings.GEMINI_FALLBACK_MODEL, "object": "model", "owned_by": "google"},
            ]
        )
    if _api_key_configured(getattr(settings, "OPENAI_API_KEY", None)):
        models.append({"id": settings.OPENAI_MODEL, "object": "model", "owned_by": "openai"})
    if _api_key_configured(getattr(settings, "GROQ_API_KEY", None)):
        models.append({"id": settings.GROQ_MODEL, "object": "model", "owned_by": "groq"})

    return {"object": "list", "data": models}


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


@router.get("/interactions", tags=["Admin"])
def interactions_endpoint(
    limit: int = Query(50, ge=1, le=500, description="Rows per page"),
    offset: int = Query(0, ge=0, description="Rows to skip for pagination"),
    country: Optional[str] = Query(None, description="Filter by country code (zm, zw)"),
    channel: Optional[str] = Query(None, description="Filter by channel (web, whatsapp)"),
    language: Optional[str] = Query(None, description="Filter by detected language"),
    rating: Optional[str] = Query(
        None, description="Filter by rating: 'rated', 'unrated', or a number 1-5"
    ),
    search: Optional[str] = Query(
        None, max_length=200, description="Substring match on query or response text"
    ),
) -> Dict[str, Any]:
    """
    Admin telemetry endpoint: returns filtered, paginated raw interaction logs
    (query, response, channel, country, language, latency, sources, rating).
    """
    return db.get_interactions(
        limit=limit,
        offset=offset,
        country=country,
        channel=channel,
        language=language,
        rating=rating,
        search=search,
    )


@router.get("/interactions/export", tags=["Admin"])
def interactions_export_endpoint(
    country: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    rating: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
) -> Response:
    """Admin telemetry endpoint: downloads the filtered interaction log as CSV."""
    data = db.get_interactions(
        limit=100000,
        offset=0,
        country=country,
        channel=channel,
        language=language,
        rating=rating,
        search=search,
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "timestamp",
            "channel",
            "country",
            "detected_language",
            "response_time_ms",
            "rating",
            "feedback_comment",
            "user_query",
            "response",
            "retrieved_sources",
        ]
    )
    for item in data["items"]:
        writer.writerow(
            [
                item.get("id"),
                _to_local_timestamp(item.get("timestamp")),
                item.get("channel"),
                item.get("country"),
                item.get("detected_language"),
                item.get("response_time_ms"),
                item.get("rating"),
                item.get("feedback_comment"),
                item.get("user_query"),
                item.get("response"),
                json.dumps(item.get("retrieved_sources") or []),
            ]
        )

    logger.info(f"Admin: exported {data['count']} interactions to CSV")
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=zedchatbot_interactions.csv"
        },
    )

