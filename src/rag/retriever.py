#!/usr/bin/env python3
"""
Retriever component for Zedchatbot.
Responsible for fetching relevant context from the vector store with country-aware domain prioritization.
"""

from typing import Dict, List
from langchain_core.documents import Document
from src.core.logger import logger
from src.knowledge_base.vector_store import ZedVectorStore

# Country-aware domain keyword mapping for modular retrieval
COUNTRY_DOMAIN_KEYWORDS: Dict[str, Dict[str, str]] = {
    "zm": {
        # Utilities
        "zesco": "utilities",
        "nwasco": "utilities",
        "madzi": "utilities",
        "amenshi": "utilities",
        "electricity": "utilities",
        "malaiti": "utilities",
        "water": "utilities",
        # Government
        "zra": "government",
        "tax": "government",
        "mutero": "government",
        "umutero": "government",
        "nrc": "government",
        "passport": "government",
        "pacra": "government",
        "napsa": "government",
        "tpin": "government",
        "paye": "government",
        # Health
        "nhima": "health",
        "ifumo": "health",
        "malaria": "health",
        "cholera": "health",
        "chipatala": "health",
        "clinic": "health",
        "hospital": "health",
        # Education
        "unza": "education",
        "cbu": "education",
        "ecz": "education",
        "helsb": "education",
        "admission": "education",
        "teveta": "education",
    },
    "zw": {
        # Utilities
        "zesa": "utilities",
        "powertel": "utilities",
        "zinwa": "utilities",
        "electricity": "utilities",
        "water": "utilities",
        # Government
        "zimra": "government",
        "tax": "government",
        "civil registry": "government",
        "registry": "government",
        "passport": "government",
        "national id": "government",
        # Education
        "zimsec": "education",
        "uz": "education",
        "university of zimbabwe": "education",
        "cut": "education",
        "msu": "education",
        "nust": "education",
        # Health
        "cholera": "health",
        "malaria": "health",
        "clinic": "health",
        "hospital": "health",
    },
}


class ZedRetriever:
    """Handles retrieval of context documents for the RAG pipeline."""

    def __init__(self, vector_store: ZedVectorStore):
        self.vector_store = vector_store

    def get_relevant_context(
        self,
        query: str,
        country_code: str,
        top_k: int = 3,
        threshold: float = 0.01,  # Effectively disabled for maximum local language recall
    ) -> List[Document]:
        """
        Retrieves the most relevant document chunks using relevance scores.
        Score is 0 to 1, where 1 is a perfect match.
        Uses country-aware domain filtering when domain keywords are detected.
        """
        c_code = country_code.lower()
        logger.info(f"Retriever: Searching for '{query[:50]}...' in {c_code.upper()}")

        try:
            # 1. Get docs with their relevance scores (0-1)
            results = self.vector_store.similarity_search_with_relevance(
                c_code, query, k=top_k
            )

            # 2. Filter results: Keep documents where score is >= threshold
            relevant_docs = []
            for doc, score in results:
                if score >= threshold:
                    relevant_docs.append(doc)
                    logger.debug(
                        f"Match found: {doc.metadata.get('source')} (Score: {score:.4f})"
                    )
                else:
                    logger.debug(
                        f"Ignoring weak match: {doc.metadata.get('source')} (Score: {score:.4f})"
                    )

            # 3. Country-Aware Domain Filtering
            query_lower = query.lower()
            filtered_docs = []
            country_domains = COUNTRY_DOMAIN_KEYWORDS.get(c_code, {})

            active_domain = None
            for key, domain in country_domains.items():
                if key in query_lower:
                    active_domain = domain
                    break

            if active_domain:
                logger.info(
                    f"Retriever: Prioritizing domain '{active_domain}' for country '{c_code.upper()}'"
                )
                for doc in relevant_docs:
                    raw_source = str(doc.metadata.get("source", ""))
                    norm_path = raw_source.replace("\\", "/").lower()
                    path_parts = [p for p in norm_path.split("/") if p]
                    meta_domain = str(doc.metadata.get("domain", "")).lower()
                    if (
                        meta_domain == active_domain
                        or active_domain in path_parts
                        or f"/{active_domain}/" in norm_path
                        or active_domain in norm_path
                    ):
                        filtered_docs.append(doc)


            # Fall back to unfiltered relevant docs if domain filter yielded nothing
            final_docs = filtered_docs if filtered_docs else relevant_docs

            logger.info(f"Retriever: Found {len(final_docs)} high-quality chunks.")
            return final_docs

        except Exception as e:
            logger.error(f"Retriever: Failed to fetch documents: {e}")
            return []

    def format_docs(self, docs: List[Document]) -> str:
        """Helper to join document contents into a single context string."""
        return "\n\n".join([doc.page_content for doc in docs])
