from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional, Any
from pathlib import Path
import json

class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None

    # LLM & Translation Configuration
    LLM_PROVIDER: str = "gemini"  # auto, ollama, gemini, openai
    TRANSLATION_PROVIDER: str = "gemini"  # gemini, nllb
    MODEL_NAME: str = "qwen2.5:7b"
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"

    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # Application Configuration
    APP_NAME: str = "Zedchatbot for African Community"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_VERSION: str = "v1"
    PRELOAD_PIPELINE_ON_STARTUP: bool = True

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    VECTOR_STORE_PATH: str = "./vector_store"

    # Multilingual & Regional Settings
    DEFAULT_COUNTRY: str = "zm"
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_COUNTRIES: List[str] = ["zm", "zw"]
    SUPPORTED_LANGUAGES: List[str] = ["en", "bem", "ny", "sn"]

    @field_validator("SUPPORTED_COUNTRIES", "SUPPORTED_LANGUAGES", mode="before")
    @classmethod
    def parse_string_list(cls, value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(v).strip().lower() for v in value]
        if isinstance(value, str):
            val_str = value.strip()
            if val_str.startswith("[") and val_str.endswith("]"):
                try:
                    parsed = json.loads(val_str)
                    return [str(v).strip().lower() for v in parsed]
                except Exception:
                    pass
            items = [item.strip().lower() for item in val_str.split(",") if item.strip()]
            items = ["sn" if i == "sho" else i for i in items]
            return items
        return value

    # Integration Settings
    WHATSAPP_SANDBOX: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def vector_store_full_path(self) -> Path:
        return self.BASE_DIR / self.VECTOR_STORE_PATH

# Global instance for easy import
settings = Settings()
