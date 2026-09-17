#!/usr/bin/env python3
"""
Build the vector index for Zambian and Zimbabwean documents with Text Chunking and optional clean reset.
"""

import argparse
import sys
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.logger import logger
from src.knowledge_base.document_loader import ZedDocumentLoader
from src.knowledge_base.vector_store import ZedVectorStore
from src.configs.settings import settings


def build_indices(reset: bool = False, country_filter: str = None):
    loader = ZedDocumentLoader()
    store = ZedVectorStore()

    target_countries = (
        [country_filter.lower()] if country_filter else settings.SUPPORTED_COUNTRIES
    )

    for country in target_countries:
        logger.info(f"Starting build_index for {country.upper()}...")

        # 1. Reset collection if requested to prevent vector duplication
        if reset:
            logger.info(f"Purging existing index for {country.upper()}...")
            store.reset_collection(country)

        # 2. Load RAW documents
        logger.info(f"Loading documents from data/raw/{country}...")
        try:
            raw_docs = loader.load_country_documents(country)
        except Exception as e:
            logger.error(f"Could not load documents for {country}: {e}")
            continue

        if not raw_docs:
            logger.warning(f"No documents found for {country}. Skipping.")
            continue

        logger.info(f"Total RAW documents found for {country}: {len(raw_docs)}")

        # 3. CHUNK the documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            length_function=len,
        )
        chunked_docs = text_splitter.split_documents(raw_docs)
        logger.info(f"Created {len(chunked_docs)} chunks for {country.upper()}.")

        # 4. Add to store
        try:
            store.add_documents(country, chunked_docs)
            logger.info(
                f"Successfully indexed {len(chunked_docs)} chunks for {country.upper()}"
            )
        except Exception as e:
            logger.error(f"Failed to build index for {country}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Index documents into country-specific ChromaDB collections."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Purge existing collection before indexing to avoid duplicates.",
    )
    parser.add_argument(
        "--country",
        type=str,
        default=None,
        help="Build index for a specific country only (e.g., zm or zw).",
    )
    args = parser.parse_args()

    build_indices(reset=args.reset, country_filter=args.country)
