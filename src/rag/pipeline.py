#!/usr/bin/env python3
"""
RAG Pipeline for Zedchatbot.
Phase 3: Retrieval-Augmented Generation implementation.
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

    def __init__(self, use_gemini: bool = False):
        self.vector_store = ZedVectorStore(use_gemini=use_gemini)
        self.retriever = ZedRetriever(self.vector_store)
        self.generator = ZedGenerator(use_gemini=use_gemini)
        self.use_gemini = use_gemini
        
        # This is the "System Prompt" that tells the AI how to behave.
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

    def generate_reply(self, message: str, country: str, language: str = None) -> Tuple[str, List[str]]:
        """Main entry point for generating a response."""
        
        # 1. Detect Language
        user_lang = language or detect_language(message)
        logger.info(f"RAG Pipeline: Processing request in {user_lang} for {country}")

        # 2. Translate to English for search (if not already English)
        # This helps the retriever find the best matches in our English documents
        search_query = message
        if user_lang != 'en':
            logger.info(f"Translating query from {user_lang} to English for retrieval...")
            search_query = translate_text(message, source=user_lang, target='en')
            logger.debug(f"Translated query: {search_query}")

        # 3. Retrieve Context
        try:
            docs = self.retriever.get_relevant_context(search_query, country)
            context_text = self.retriever.format_docs(docs)
            sources = list(set([doc.metadata.get('source', 'Unknown Source') for doc in docs]))
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            context_text = ""
            sources = []

        # 4. Generate Answer
        try:
            final_answer = self.generator.generate(message, context_text, country, user_lang)
            
            # 5. Translation Guard (If generator returned English but user spoke something else)
            # This handles cases where the generator is in SIMULATED mode or Gemini failed
            if user_lang != 'en' and final_answer.startswith("Based on our"):
                logger.info(f"Back-translating simulated response to {user_lang}...")
                final_answer = translate_text(final_answer, source='en', target=user_lang)
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            final_answer = "I'm sorry, I encountered an error while generating your response."

        return final_answer, sources

_pipeline: Optional[RAGPipeline] = None


def get_pipeline() -> RAGPipeline:
    """Initializes the RAG pipeline only when the app needs it."""
    global _pipeline

    if _pipeline is None:
        _pipeline = RAGPipeline(use_gemini=True)
    return _pipeline

def generate_reply(message: str, country: str, language: str = None) -> Tuple[str, List[str]]:
    """Functional wrapper for the API routes."""
    return get_pipeline().generate_reply(message, country, language)
