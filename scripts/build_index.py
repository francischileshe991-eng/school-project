#!/usr/bin/env python3
"""
Build the vector index for Zambian documents with Text Chunking.
"""

import sys
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.logger import logger
from src.knowledge_base.document_loader import ZedDocumentLoader
from src.knowledge_base.vector_store import ZedVectorStore

def build_zambia_index():
    logger.info("Starting build_index for Zambia...")
    
    loader = ZedDocumentLoader()
    store = ZedVectorStore(use_gemini=False)
    
    # 1. Load RAW documents
    logger.info(f"Loading documents from data/raw/zm...")
    try:
        raw_docs = loader.load_country_documents("zm")
    except Exception as e:
        logger.error(f"Could not load documents: {e}")
        return

    if not raw_docs:
        logger.error("No documents found to index! Make sure files are in data/raw/zm/")
        return
    logger.info(f"Total RAW documents found: {len(raw_docs)}")

    # 2. CHUNK the documents into smaller context pieces
    logger.info("Splitting documents into smaller chunks for the AI...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       # About 200-300 words per chunk
        chunk_overlap=100,    # 100 characters overlap to keep sentences unbroken
        length_function=len,
    )
    chunked_docs = text_splitter.split_documents(raw_docs)
    logger.info(f"Your {len(raw_docs)} files were split into {len(chunked_docs)} readable chunks!")

    # 3. Add chunks to the vector store
    try:
        store.add_documents("zm", chunked_docs)
        logger.info("Successfully built and persisted the Zambia vector index.")
    except Exception as e:
        logger.error(f"Failed to build index: {e}")

if __name__ == "__main__":
    build_zambia_index()
