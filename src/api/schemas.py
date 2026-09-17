from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from src.configs.settings import settings


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question or query text",
    )
    country: str = Field(
        default="zm",
        pattern=r"^[a-zA-Z]{2}$",
        description="ISO 2-letter country code",
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code ('en', 'bem', 'ny', 'sn') or None/'auto' for auto-detection",
    )

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        code = v.strip().lower()
        if code not in settings.SUPPORTED_COUNTRIES:
            raise ValueError(
                f"Country '{v}' is not supported. Supported countries: {settings.SUPPORTED_COUNTRIES}"
            )
        return code

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        code = v.strip().lower()
        if code in ("auto", ""):
            return None
        if code not in settings.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language '{v}' is not supported. Supported languages: {settings.SUPPORTED_LANGUAGES} or 'auto'"
            )
        return code



class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    interaction_id: Optional[int] = None
    response_time_ms: Optional[int] = None


class FeedbackRequest(BaseModel):
    interaction_id: int = Field(..., description="The ID of the interaction being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(default=None, description="Optional text feedback")


class FeedbackResponse(BaseModel):
    status: str
    message: str
