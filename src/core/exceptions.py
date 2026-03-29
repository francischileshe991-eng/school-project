from typing import Any, Dict, Optional

class ZedChatbotError(Exception):
    """Base exception for all Zedchatbot errors."""
    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        payload: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

class VectorStoreError(ZedChatbotError):
    """Raised when there is an issue with the vector database (ChromaDB)."""
    def __init__(self, message: str = "Vector store operation failed", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, payload=payload)

class LLMError(ZedChatbotError):
    """Raised when the LLM (OpenAI) fails to provide a response."""
    def __init__(self, message: str = "LLM generation failed", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=502, payload=payload)

class MultilingualError(ZedChatbotError):
    """Raised when language detection or translation fails."""
    def __init__(self, message: str = "Language processing failed", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, payload=payload)

class KnowledgeBaseError(ZedChatbotError):
    """Raised when there is an issue with document ingestion or retrieval."""
    def __init__(self, message: str = "Knowledge base operation failed", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, payload=payload)

class WhatsAppIntegrationError(ZedChatbotError):
    """Raised when Twilio or WhatsApp integration fails."""
    def __init__(self, message: str = "WhatsApp integration failed", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, payload=payload)

class ConfigurationError(ZedChatbotError):
    """Raised when critical configuration settings are missing or invalid."""
    def __init__(self, message: str = "Invalid configuration settings", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, payload=payload)

class ResourceNotFoundError(ZedChatbotError):
    """Raised when a requested document or resource is not found."""
    def __init__(self, message: str = "Resource not found", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, payload=payload)
