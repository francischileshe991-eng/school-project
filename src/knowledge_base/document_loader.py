import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    DirectoryLoader,
    TextLoader,
)
from langchain_core.documents import Document
from src.core.logger import logger
from src.core.exceptions import KnowledgeBaseError


class ZedDocumentLoader:
    """Handles loading documents for the Zambian and Zimbabwean knowledge bases."""

    def __init__(self, data_path: str = "data/raw"):
        self.data_path = Path(data_path)

    def load_country_documents(self, country_code: str) -> List[Document]:
        """
        Loads all documents from a country-specific subdirectory.
        Example: data/raw/zm/ for Zambia.
        """
        country_path = self.data_path / country_code.lower()

        if not country_path.exists():
            logger.error(
                f"Data path not found for country {country_code}: {country_path}"
            )
            raise KnowledgeBaseError(f"Directory for {country_code} not found.")

        logger.info(
            f"Loading documents for country: {country_code.upper()} from {country_path}"
        )

        documents = []

        loaders = {"*.pdf": PyPDFLoader, "*.txt": TextLoader}

        for pattern, loader_class in loaders.items():
            try:
                dir_loader = DirectoryLoader(
                    str(country_path),
                    glob=pattern,
                    loader_cls=loader_class,
                    recursive=True,
                    silent_errors=True,
                )
                loaded_docs = dir_loader.load()
                documents.extend(loaded_docs)
                logger.info(f"Loaded {len(loaded_docs)} documents matching {pattern}")
            except Exception as e:
                logger.warning(f"Failed to load documents for pattern {pattern}: {e}")

        if not documents:
            logger.warning(
                f"No documents found for {country_code.upper()} in {country_path}"
            )
        else:
            logger.info(
                f"Successfully loaded {len(documents)} total documents for {country_code.upper()}"
            )

        return documents

    def load_single_file(self, file_path: str) -> List[Document]:
        """Loads a single document from a given path."""
        path = Path(file_path)
        if not path.exists():
            raise KnowledgeBaseError(f"File not found: {file_path}")

        logger.debug(f"Loading single file: {file_path}")

        if path.suffix.lower() == ".pdf":
            return PyPDFLoader(str(path)).load()
        elif path.suffix.lower() == ".txt":
            return TextLoader(str(path)).load()
        else:
            raise KnowledgeBaseError(f"Unsupported file format: {path.suffix}")
