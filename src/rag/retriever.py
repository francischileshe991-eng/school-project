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
        top_k: int = 3
    ) -> List[Document]:
        """
        Retrieves the most relevant document chunks for a given query.
        """
        logger.info(f"Retriever: Searching for '{query[:50]}...' in {country_code.upper()}")
        
        try:
            # We use the similarity search from our vector store implementation
            docs = self.vector_store.similarity_search(
                country_code=country_code,
                query=query,
                k=top_k
            )
            logger.info(f"Retriever: Found {len(docs)} relevant chunks.")
            return docs
        except Exception as e:
            logger.error(f"Retriever: Failed to fetch documents: {e}")
            return []

    def format_docs(self, docs: List[Document]) -> str:
        """Helper to join document contents into a single context string."""
        return "\n\n".join([doc.page_content for doc in docs])
