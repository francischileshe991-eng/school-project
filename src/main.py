#!/usr/bin/env python3
"""
Zedchatbot - Main Application Entry Point.
Phase 4: Unified entry point for starting the service.
"""

import sys
import os
from pathlib import Path

# Add the project root to sys.path so 'import src' works
root_path = str(Path(__file__).resolve().parent.parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from src.api.web_api import app
from src.configs.settings import settings
from src.core.logger import logger

# This file simply exposes the fully-configured 'app' instance from our modular API setup.
# You can run the application using:
# uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload


if __name__ == "__main__":
    import uvicorn
    
    # Ensure host defaults to 127.0.0.1 for local runs so Uvicorn prints a directly clickable link
    host = "127.0.0.1" if settings.API_HOST in ["0.0.0.0", "127.0.0.1"] else settings.API_HOST
    
    logger.info(f"Launching {settings.APP_NAME}...")
    logger.info(f"Web UI available at: http://{host}:{settings.API_PORT}/app/ (or http://localhost:{settings.API_PORT}/)")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )


