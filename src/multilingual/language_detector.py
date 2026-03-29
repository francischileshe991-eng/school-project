#!/usr/bin/env python3
"""
Language detection component for multilingual support.
"""

from typing import Optional
from langdetect import detect, detect_langs, DetectorFactory
from src.core.logger import logger
from src.configs.settings import settings

# Set seed for deterministic language detection results
DetectorFactory.seed = 0

class LanguageDetector:
    """Handles detection of user input language."""

    def __init__(self):
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.default_language = settings.DEFAULT_LANGUAGE

    def detect_language(self, text: str) -> str:
        """
        Detects the language of the given text.
        Returns the language code (e.g., 'en', 'bem', 'ny').
        """
        if not text or not text.strip():
            return self.default_language

        try:
            # langdetect returns ISO 639-1 codes (e.g., 'en', 'pt', 'es')
            lang_code = detect(text)
            
            # If detected as English, return immediately
            if lang_code == 'en':
                return 'en'
            
            # Otherwise, return the detected code (even if not in our supported list)
            # This allows the pipeline to decide if it needs further translation
            return lang_code

        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return self.default_language

    def get_confidence_scores(self, text: str):
        """Returns a list of detected languages with their confidence scores."""
        try:
            return detect_langs(text)
        except Exception as e:
            logger.error(f"Failed to get language confidence scores: {e}")
            return []

# Global instance for easy access
language_detector = LanguageDetector()

def detect_language(text: str) -> str:
    """Functional wrapper for language detection."""
    return language_detector.detect_language(text)
