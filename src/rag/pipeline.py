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


LANG_SIGNATURE_WORDS = {
    "bem": {"mwapoleni", "shani", "ngapo", "kabili", "fye", "bana", "umuleti", "napo", "ndafuna", "ukufwaya"},
    "ny": {"muli", "kodi", "ndikufuna", "yankho", "mwai", "lero", "kuyanjana", "bwin", "ndani", "ndifuna", "funa"},
    "sn": {"mhoro", "ndiri", "sei", "zvinhu", "kana", "zvino", "mazuva", "ndinovh"},
}


class RAGPipeline:
    """Handles the end-to-end RAG process."""

    def __init__(self, use_ollama: bool = True):
        self.vector_store = ZedVectorStore(use_ollama=use_ollama)
        self.retriever = ZedRetriever(self.vector_store)
        self.generator = ZedGenerator(use_ollama=use_ollama)
        self.use_ollama = use_ollama

        self.prompt_template = """
        You are a helpful Zambian Community Assistant. 
        Use the following pieces of retrieved context to answer the user's question.
        If you don't know the answer based on the context, just say that you don't know.
        Keep the answer professional and relevant to the Zambian or Zimbabwean context.

        Context: 
        {context}

        Question: 
        {question}

        Answer:
        """

    def _needs_translation(self, text: str, target_lang: str) -> bool:
        """Check if text likely needs translation to target language."""
        if not text or len(text.strip()) < 3:
            return True

        text_lower = text.lower()
        signature_words = LANG_SIGNATURE_WORDS.get(target_lang, set())

        if signature_words:
            has_signature = any(word in text_lower for word in signature_words)
            if has_signature:
                return False

        detected = detect_language(text)
        if detected == target_lang:
            return False

        return True

    def generate_reply(
        self, message: str, country: str, language: str = None
    ) -> Tuple[str, List[str]]:
        """Main entry point for Native Multilingual RAG."""

        user_lang = language or detect_language(message)
        logger.info(f"RAG Pipeline: Processing NATIVE request in {user_lang} for {country}")

        # NATIVE SEARCH: BGE-M3 handles multilingual queries directly
        search_query = message
        
        try:
            # We search directly with the user's message
            docs = self.retriever.get_relevant_context(search_query, country)
            context_text = self.retriever.format_docs(docs)
            sources = list(
                set([doc.metadata.get("source", "Unknown Source") for doc in docs])
            )
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            context_text = ""
            sources = []

        try:
            # NATIVE GENERATION: Qwen2.5 responds in the detected language
            final_answer = self.generator.generate(
                message, context_text, country, user_lang
            )
            
            # Back-translation is now only a FALLBACK if the response is too short 
            # or obviously wrong (English instead of Nyanja)
            if user_lang != "en" and self._needs_translation(final_answer, user_lang):
                logger.info(f"Fallback: LLM failed native {user_lang}, translating from English...")
                translated = translate_text(final_answer, source="en", target=user_lang)
                if translated and translated != final_answer:
                    final_answer = translated

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            final_answer = (
                "I'm sorry, I encountered an error while generating your response."
            )

        return final_answer, sources


_pipeline: Optional[RAGPipeline] = None


def get_pipeline() -> RAGPipeline:
    """Initializes the RAG pipeline only when the app needs it."""
    global _pipeline

    if _pipeline is None:
        _pipeline = RAGPipeline(use_ollama=True)
    return _pipeline


def generate_reply(
    message: str, country: str, language: str = None
) -> Tuple[str, List[str]]:
    """Functional wrapper for the API routes."""
    return get_pipeline().generate_reply(message, country, language)
