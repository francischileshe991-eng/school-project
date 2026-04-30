#!/usr/bin/env python3
"""
Web API Entry Point for Zedchatbot.
Phase 4: FastAPI server configuration and CORS setup.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router as web_router
from src.api.whatsapp_api import router as whatsapp_router
from src.configs.settings import settings
from src.core.logger import logger

def create_app() -> FastAPI:
    """Configures and returns the FastAPI application."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.API_VERSION,
        description="Multilingual RAG Chatbot for African Communities"
    )

    # CORS configuration...
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(web_router, tags=["Web"])
    app.include_router(whatsapp_router, tags=["WhatsApp"])

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.APP_NAME} API...")
        if settings.PRELOAD_PIPELINE_ON_STARTUP:
            from src.rag.pipeline import get_pipeline

            logger.info("Preloading RAG pipeline and models into memory...")
            get_pipeline()
            logger.info("RAG pipeline and models ready.")

    return app

app = create_app()

if __name__ == "__main__":
    # Allows running the script directly via 'python src/api/web_api.py'
    import uvicorn

    uvicorn.run(
        "src.api.web_api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
