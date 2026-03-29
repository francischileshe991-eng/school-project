#!/usr/bin/env python3
"""
Comprehensive test script for the end-to-end RAG Pipeline.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag.pipeline import generate_reply
from src.core.logger import setup_logger

# Setup logger
logger = setup_logger('test_rag_pipeline')

def run_rag_test(message: str, country: str, language: str = None):
    """Helper to run a RAG query and log results clearly."""
    logger.info(f"\n>>> TESTING: '{message}' ({country.upper()}, Lang: {language or 'Auto'})")
    
    try:
        answer, sources = generate_reply(message, country, language)
        
        print("-" * 50)
        print(f"QUESTION: {message}")
        print(f"ANSWER:   {answer}")
        print(f"SOURCES:  {', '.join(sources)}")
        print("-" * 50)
        
        return answer
    except Exception as e:
        logger.error(f"RAG Test failed: {e}")
        return None

def main():
    logger.info("Starting End-to-End RAG Pipeline Tests...")

    # 1. English Test (Standard)
    run_rag_test("What is UNZA?", "zm", "en")

    # 2. Nyanja Test (Multilingual Retrieval + Back Translation)
    run_rag_test("Kodi NRC ndi chiyani?", "zm", "ny")

    # 3. Tax Query in Nyanja (ZRA Retrieval)
    run_rag_test("Ndingalipira bwanji misonkho?", "zm", "ny")

    # 4. Health Query in English (NHIMA Retrieval)
    run_rag_test("Who can join NHIMA?", "zm", "en")

    # 5. Shona Test (Zimbabwe context placeholder)
    # Note: We haven't added Zim data yet, so this tests the "No Info" fallback
    run_rag_test("Ndinobhadhara sei mitero?", "zw", "sn")

    logger.info("\nAll RAG Pipeline tests completed!")

if __name__ == "__main__":
    main()
