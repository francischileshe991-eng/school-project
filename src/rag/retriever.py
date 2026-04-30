#!/usr/bin/env python3
"""
Retriever component for Zedchatbot.
Responsible for fetching relevant context from the vector store.
"""

from typing import List
from langchain_core.documents import Document
from src.core.logger import logger
from src.knowledge_base.vector_store import ZedVectorStore

class ZedRetriever:
    """Handles retrieval of context documents for the RAG pipeline."""

    def __init__(self, vector_store: ZedVectorStore):
        self.vector_store = vector_store

    def get_relevant_context(
        self, 
        query: str, 
        country_code: str, 
        top_k: int = 3,
        threshold: float = 999.0 # Effectively disabled
    ) -> List[Document]:
        """
        Retrieves the most relevant document chunks for a given query.
        Uses distance scoring (Lower distance = Better match).
        """
        logger.info(f"Retriever: Searching for '{query[:50]}...' in {country_code.upper()}")
        
        try:
            # Get docs with their distance scores
            # Note: similarity_search_with_score returns (doc, distance)
            results = self.vector_store.get_vector_store(country_code).similarity_search_with_score(
                query, 
                k=top_k
            )
            
            # Filter results: Keep documents where distance is LESS than threshold
            relevant_docs = [doc for doc, distance in results if distance <= threshold]
            
            logger.info(f"Retriever: Found {len(relevant_docs)} relevant chunks (Threshold: {threshold}).")
            return relevant_docs
        except Exception as e:
            logger.error(f"Retriever: Failed to fetch documents: {e}")
            return []

    def format_docs(self, docs: List[Document]) -> str:
        """Helper to join document contents into a single context string."""
        return "\n\n".join([doc.page_content for doc in docs])
