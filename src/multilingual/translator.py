#!/usr/bin/env python3
"""
Local Translation service using Meta's NLLB-200 model.
Phase 5: High-quality local translation for African languages.
"""

from typing import Optional
from src.core.logger import logger
from src.configs.settings import settings

# Attempt to load transformers only when needed to save memory
_pipeline = None

class ZedTranslator:
    """Handles local translation using NLLB-200."""

    def __init__(self):
        # Map our simple codes to NLLB-200 long codes
        self.code_map = {
            "en": "eng_Latn",
            "bem": "bem_Latn",
            "ny": "nya_Latn",
            "sn": "sna_Latn"
        }
        self.model_name = "facebook/nllb-200-distilled-600M"

    def _get_pipeline(self):
        """Lazy initialization of the translation pipeline."""
        global _pipeline
        if _pipeline is None:
            try:
                from transformers import pipeline
                import torch
                
                logger.info(f"Translator: Loading {self.model_name} (this may take a while)...")
                device = 0 if torch.cuda.is_available() else -1
                _pipeline = pipeline(
                    "translation", 
                    model=self.model_name, 
                    device=device
                )
                logger.info("Translator: Model loaded successfully.")
            except Exception as e:
                logger.error(f"Translator: Failed to load NLLB model: {e}")
                return None
        return _pipeline

    def translate(self, text: str, source: str = 'en', target: str = 'en') -> str:
        """Translates text between supported languages."""
        if not text or not text.strip() or source == target:
            return text

        # Map to NLLB codes
        src_lang = self.code_map.get(source, "eng_Latn")
        tgt_lang = self.code_map.get(target, "eng_Latn")

        pipe = self._get_pipeline()
        if not pipe:
            return text # Fallback to original text

        try:
            result = pipe(text, src_lang=src_lang, tgt_lang=tgt_lang)
            translated_text = result[0]['translation_text']
            logger.debug(f"Translated: '{text[:30]}...' -> '{translated_text[:30]}...'")
            return translated_text
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    def translate_to_english(self, text: str, source: str) -> str:
        return self.translate(text, source=source, target='en')

    def translate_from_english(self, text: str, target: str) -> str:
        return self.translate(text, source='en', target=target)

# Global instance
zed_translator = ZedTranslator()

def translate_text(text: str, source: str = 'en', target: str = 'en') -> str:
    return zed_translator.translate(text, source=source, target=target)
