#!/usr/bin/env python3
"""
RAG Pipeline for Zedchatbot.
Enhanced with improved multilingual support.
"""

from typing import List, Optional, Tuple
from src.core.logger import logger
from src.multilingual.language_detector import detect_language
from src.multilingual.translator import translate_text
from src.knowledge_base.vector_store import ZedVectorStore
from src.rag.retriever import ZedRetriever
from src.rag.generator import ZedGenerator


class RAGPipeline:
    """Handles the end-to-end RAG process."""

    def __init__(self):
        self.vector_store = ZedVectorStore()
        self.retriever = ZedRetriever(self.vector_store)
        self.generator = ZedGenerator()


    def generate_reply(
        self,
        message: Optional[str] = None,
        country: str = "zm",
        language: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Tuple[str, List[str]]:
        """Main entry point for High-Quality Multilingual RAG."""
        actual_message = message if message is not None else (query or "")
        clean_lang = language.strip().lower() if (language and isinstance(language, str)) else None
        if not clean_lang or clean_lang == "auto":
            user_lang = detect_language(actual_message)
        else:
            user_lang = clean_lang
        logger.info(f"RAG Pipeline: Processing request in {user_lang} for {country}")

        # 1. NATIVE SEARCH: Trust the BGE-M3 top results
        try:
            # Get the top 4 most relevant documents
            docs = self.retriever.get_relevant_context(actual_message, country, top_k=4)
            
            if docs:
                context_text = self.retriever.format_docs(docs)
                sources = list(set([doc.metadata.get("source", "Unknown Source") for doc in docs]))
            else:
                logger.info(f"No relevant documents found for {country}.")
                return "I'm sorry, I don't have that specific official record in my database yet.", []
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            context_text = ""
            sources = []

        try:
            # 2. EXPERT GENERATION (English)
            english_answer = self.generator.generate(actual_message, context_text, country, "en")
            final_answer = english_answer

            # 3. EXPERT TRANSLATION (Local Language)
            # Edge case handling: If the generator returned the raw context excerpt fallback,
            # keep it in English rather than translating an unformatted raw text wall.
            if user_lang != "en":
                if english_answer.startswith("According to official public records:"):
                    logger.info("Grounded excerpt fallback preserved in English to avoid unformatted translation degradation.")
                else:
                    logger.info(f"Translating expert answer to {user_lang}...")
                    translated = translate_text(english_answer, source="en", target=user_lang)
                    if translated:
                        final_answer = translated

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            final_answer = "I encountered a technical error while processing your request."

        return final_answer, sources


_pipeline: Optional[RAGPipeline] = None


def get_pipeline() -> RAGPipeline:
    """Initializes the RAG pipeline only when the app needs it."""
    global _pipeline

    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


def generate_reply(
    message: Optional[str] = None,
    country: str = "zm",
    language: Optional[str] = None,
    query: Optional[str] = None,
) -> Tuple[str, List[str]]:
    """Functional wrapper for the API routes."""
    actual_message = message if message is not None else (query or "")
    return get_pipeline().generate_reply(
        message=actual_message, country=country, language=language
    )

