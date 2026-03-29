#!/usr/bin/env python3
"""
Test script for multilingual components (Detection, Translation, Tokenizer)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.multilingual.language_detector import detect_language, language_detector
from src.multilingual.translator import translate_text, zed_translator
from src.multilingual.tokenizer import count_tokens, zed_tokenizer
from src.core.logger import setup_logger

# Setup logger
logger = setup_logger('test_multilingual')

def test_language_detection():
    logger.info("\n--- Testing Language Detection ---")
    
    test_cases = [
        ("How do I pay my taxes in Zambia?", "en"),
        ("Nshila nshi ya kulipililamo imisonko mu Zambia?", "bem"), # Bemba
        ("Ndingalipira bwanji misonkho ku Zambia?", "ny"),      # Nyanja
        ("Ndinobhadhara sei mitero muZambia?", "sho"),           # Shona (Zimbabwe)
    ]
    
    for text, expected in test_cases:
        detected = detect_language(text)
        logger.info(f"Input: '{text[:50]}...'")
        logger.info(f"Detected: {detected} (Expected: {expected})")
        
        # Test confidence scores
        scores = language_detector.get_confidence_scores(text)
        logger.info(f"Confidence: {scores}")

def test_translation():
    logger.info("\n--- Testing Translation ---")
    
    # Translate from Bemba to English
    bemba_text = "Nshila nshi ya kulipililamo imisonko mu Zambia?"
    translated_en = translate_text(bemba_text, source='auto', target='en')
    logger.info(f"Bemba: {bemba_text}")
    logger.info(f"To English: {translated_en}")
    
    # Translate from English to Nyanja
    en_text = "The National Registration Card is a vital document."
    translated_ny = translate_text(en_text, source='en', target='ny')
    logger.info(f"English: {en_text}")
    logger.info(f"To Nyanja: {translated_ny}")

def test_tokenizer():
    logger.info("\n--- Testing Tokenizer ---")
    
    text = "Zambia is a beautiful country in Southern Africa with a rich culture."
    token_count = count_tokens(text)
    logger.info(f"Text: '{text}'")
    logger.info(f"Token Count: {token_count}")
    
    # Test truncation
    truncated = zed_tokenizer.truncate_text(text, max_tokens=5)
    logger.info(f"Truncated (5 tokens): '{truncated}'")

def main():
    logger.info("Starting Multilingual Component Tests...")
    
    try:
        test_language_detection()
        test_translation()
        test_tokenizer()
        logger.info("\nAll multilingual tests completed successfully!")
    except Exception as e:
        logger.error(f"Multilingual tests failed: {e}")
        raise

if __name__ == "__main__":
    main()
