#!/usr/bin/env python3
"""
Test script for the Local NLLB-200 Translator.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.multilingual.translator import translate_text
from src.core.logger import setup_logger

# Setup logger
logger = setup_logger('test_nllb')

def test_local_translations():
    logger.info("Starting Local NLLB-200 Translation Tests...")
    
    test_cases = [
        # English to Local
        ("Hello, how are you?", "en", "ny"),
        ("The University of Zambia is in Lusaka.", "en", "bem"),
        ("You can pay your taxes online.", "en", "sn"),
        
        # Local to English
        ("Muli bwanji?", "ny", "en"),
        ("Nshila nshi ya kulipililamo imisonko?", "bem", "en"),
    ]
    
    for text, src, tgt in test_cases:
        print(f"\n[{src.upper()} -> {tgt.upper()}]")
        print(f"Original: {text}")
        try:
            translated = translate_text(text, source=src, target=tgt)
            print(f"Result:   {translated}")
        except Exception as e:
            print(f"Error:    {e}")

if __name__ == "__main__":
    test_local_translations()
