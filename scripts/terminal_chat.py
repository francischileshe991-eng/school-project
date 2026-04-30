#!/usr/bin/env python3
"""
Terminal Chat Utility for Zedchatbot.
Allows direct interaction with the RAG pipeline without the web server.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag.pipeline import generate_reply
from src.core.logger import logger

def main():
    print("="*50)
    print("ZEDCHATBOT TERMINAL DEBUGGER")
    print("="*50)
    print("Type 'exit' to quit.")
    
    country = "zm"
    language = "en"
    
    while True:
        query = input("\nYou: ")
        if query.lower() in ['exit', 'quit']:
            break
            
        if not query.strip():
            continue

        print("Zedchatbot is thinking...")
        
        try:
            # We will call the retriever directly here to see the scores
            from src.rag.pipeline import get_pipeline
            pipe_instance = get_pipeline()
            
            # Show what the retriever is doing
            results = pipe_instance.vector_store.similarity_search_with_relevance(country, query, k=3)
            
            print("\n--- DEBUG: RETRIEVAL SCORES ---")
            for doc, score in results:
                print(f"Score: {score:.4f} | File: {doc.metadata.get('source')} | Preview: {doc.page_content[:50]}...")
            print("-" * 30)

            # Now get the real answer
            answer, sources = pipe_instance.generate_reply(query, country, language)
            
            print(f"\nBOT: {answer}")
            if sources:
                print(f"DEBUG (Sources): {', '.join(sources)}")
        except Exception as e:
            print(f"\nERROR: {e}")

if __name__ == "__main__":
    # Suppress excessive logging for clean terminal view
    import logging
    logging.getLogger('zedchatbot').setLevel(logging.WARNING)
    
    main()
