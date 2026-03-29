import sys
import os
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.configs.settings import settings
from src.core.logger import logger
from src.knowledge_base.document_loader import ZedDocumentLoader
from src.knowledge_base.vector_store import ZedVectorStore
from langchain_core.documents import Document

def test_configurations():
    print("\n--- Testing Configurations ---")
    print(f"App Name: {settings.APP_NAME}")
    print(f"Supported Countries: {settings.SUPPORTED_COUNTRIES}")
    print(f"Supported Languages: {settings.SUPPORTED_LANGUAGES}")
    logger.info("Configuration test passed.")

def test_document_loader():
    print("\n--- Testing Document Loader (Recursive) ---")
    loader = ZedDocumentLoader()
    
    # Ensure our sample directories and files from earlier exist
    # (ZRA, ECZ, NHIMA info we created in the other script)
    
    try:
        # Load all documents for Zambia recursively
        docs = loader.load_country_documents("zambia") 
        print(f"Loaded {len(docs)} documents for Zambia.")
        for doc in docs:
            print(f"File: {doc.metadata.get('source')} | Preview: {doc.page_content[:50]}...")
        logger.info("Document loader test passed.")
        return docs
    except Exception as e:
        logger.error(f"Document loader test failed: {e}")
        return []

def test_vector_store(docs):
    print("\n--- Testing Vector Store (Indexing All Documents) ---")
    try:
        store = ZedVectorStore(use_gemini=False)
        print("Vector store initialized successfully.")
        
        if docs:
            store.add_documents("zm", docs)
            print(f"Successfully indexed {len(docs)} documents for zm.")
        
        # Test search for Tax/ZRA specifically
        results = store.similarity_search("zm", "How do I register for taxes?")
        if results:
            print(f"Search result found: {results[0].page_content[:100]}...")
        logger.info("Vector store test passed.")
    except Exception as e:
        logger.error(f"Vector store test failed: {e}")

if __name__ == "__main__":
    test_configurations()
    docs = test_document_loader()
    test_vector_store(docs)
