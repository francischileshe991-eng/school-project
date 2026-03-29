import sys
import logging
from pathlib import Path
from src.configs.settings import settings

def setup_logger(name: str = "zedchatbot") -> logging.Logger:
    """Configures and returns a logger instance."""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.hasHandlers():
        return logger

    # Set log level based on APP_ENV/DEBUG
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(level)

    # Log Format
    # Example: 2024-03-27 10:00:00 [INFO] src.rag.retriever: Starting retrieval...
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Optional: Log to a file if needed)
    log_dir = settings.BASE_DIR / "logs"
    try:
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback if log directory cannot be created (e.g., permission issues)
        print(f"Warning: Could not create log file: {e}")

    return logger

# Global logger instance
logger = setup_logger()
