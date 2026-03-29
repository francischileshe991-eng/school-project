from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    country: str = Field(default="zm")
    language: str = Field(default="en")


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
