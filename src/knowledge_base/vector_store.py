import os
import shutil
from pathlib import Path
from typing import List, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.configs.settings import settings
from src.core.logger import logger
from src.core.exceptions import VectorStoreError

_EmbeddingsCache = {}


def _get_embeddings_instance():
    """Returns cached embeddings instance (BGE-M3) for native multilingual support."""
    model_name = getattr(settings, "EMBEDDING_MODEL", "BAAI/bge-m3")
    cache_key = f"huggingface_{model_name}"

    if cache_key not in _EmbeddingsCache:
        logger.info(f"Initializing Native Multilingual Embeddings: {model_name}")
        # BGE-M3 is powerful and runs locally via HuggingFaceEmbeddings
        _EmbeddingsCache[cache_key] = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},  # Use 'cuda' if you have a GPU later
            encode_kwargs={"normalize_embeddings": True},
        )
    return _EmbeddingsCache[cache_key]


class ZedVectorStore:
    """Manages country-specific ChromaDB vector stores."""

    def __init__(self):
        self.base_path = settings.vector_store_full_path
        self.embeddings = _get_embeddings_instance()

    def _get_country_db_path(self, country_code: str) -> str:
        """Returns the local path for a country's vector database."""
        c = country_code.strip().lower()
        if c not in settings.SUPPORTED_COUNTRIES:
            raise VectorStoreError(
                f"Unsupported country code: '{country_code}'. Supported: {settings.SUPPORTED_COUNTRIES}"
            )
        path = self.base_path / c
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    def get_vector_store(self, country_code: str) -> Chroma:
        """Initializes or loads a ChromaDB instance for a specific country."""
        persist_directory = self._get_country_db_path(country_code)

        try:
            return Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
                collection_name=f"zedchatbot_{country_code.lower()}",
            )
        except Exception as e:
            logger.error(f"Failed to initialize Vector Store for {country_code}: {e}")
            raise VectorStoreError(f"ChromaDB initialization failed: {e}")

    def reset_collection(self, country_code: str) -> None:
        """
        Deletes the existing ChromaDB collection for a country to avoid duplicate chunks.
        """
        c_code = country_code.lower()
        persist_directory = self._get_country_db_path(c_code)

        try:
            vector_db = self.get_vector_store(c_code)
            vector_db.delete_collection()
            logger.info(f"VectorStore: Dropped collection for {c_code.upper()}")
        except Exception as e:
            logger.warning(
                f"VectorStore: API delete_collection for {c_code.upper()} returned: {e}"
            )

        # Ensure directory is cleanly purged
        try:
            if os.path.exists(persist_directory):
                shutil.rmtree(persist_directory)
                os.makedirs(persist_directory, exist_ok=True)
                logger.info(
                    f"VectorStore: Cleanly purged persist directory for {c_code.upper()}"
                )
        except Exception as rm_err:
            logger.error(f"VectorStore: Failed to clear directory: {rm_err}")

    def add_documents(self, country_code: str, documents: List[Document]):
        """Adds a list of document chunks to the country's vector store."""
        if not documents:
            logger.warning(f"No documents to add for {country_code}")
            return

        logger.info(
            f"Adding {len(documents)} chunks to {country_code.upper()} vector store"
        )
        vector_db = self.get_vector_store(country_code)

        try:
            vector_db.add_documents(documents)
            logger.info(f"Successfully indexed documents for {country_code}")
        except Exception as e:
            logger.error(f"Failed to add documents to {country_code} vector store: {e}")
            raise VectorStoreError(f"Failed to index documents: {e}")

    def similarity_search(
        self, country_code: str, query: str, k: int = 4
    ) -> List[Document]:
        """Performs a similarity search in the country-specific database."""
        vector_db = self.get_vector_store(country_code)

        try:
            logger.debug(
                f"Searching {country_code.upper()} vector store for: '{query}'"
            )
            return vector_db.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Similarity search failed for {country_code}: {e}")
            raise VectorStoreError(f"Search operation failed: {e}")

    def similarity_search_with_relevance(
        self, country_code: str, query: str, k: int = 4
    ) -> List[tuple[Document, float]]:
        """Performs a search and returns documents with their relevance scores."""
        vector_db = self.get_vector_store(country_code)
        try:
            return vector_db.similarity_search_with_relevance_scores(query, k=k)
        except Exception as e:
            logger.error(f"Relevance search failed: {e}")
            return []
