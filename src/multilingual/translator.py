#!/usr/bin/env python3
"""
Local Translation service using Meta's NLLB-200 model.
Enhanced with phrase caching, short text handling, and keyword protection.
"""

import re
from src.core.logger import logger

_pipeline = None

GREETINGS_CACHE = {
    ("en", "ny"): "Muli bwanji! Ndingakuyankheni bwanji lero?",
    ("en", "bem"): "Mwapoleni! Ninshi fyo?",
    ("en", "sn"): "Mhoro! Ndingakubatsirei sei?",
    ("ny", "en"): "Hello! How can I help you today?",
    ("bem", "en"): "Hello! How can I help you?",
    ("sn", "en"): "Hello! How can I help you today?",
}

GREETINGS_SOURCE = {
    "ny": [
        "muli bwanji",
        "mwina",
        "mwai",
        "ndi",
        "ndapita",
        "chichewa",
        "hello",
        "hi",
        "bwino",
    ],
    "bem": ["mwapoleni", "shani", "muli", "hello", "hi", "shikulu", "kabili", "fye"],
    "sn": ["mhoro", "ndiri", "zvinhu", "hello", "hi", "sei", "zvino"],
}

PROTECTED_KEYWORDS = [
    "NHIMA",
    "ZRA",
    "UNZA",
    "ECZ",
    "ZESCO",
    "NRC",
    "Zambia",
    "Zimbabwe",
    "Zambian",
    "Zimbabwean",
    "Bemba",
    "Nyanja",
    "Shona",
]


class ZedTranslator:
    """Handles local translation using NLLB-200 with enhanced short text handling."""

    def __init__(self):
        self.code_map = {
            "en": "eng_Latn",
            "bem": "bem_Latn",
            "ny": "nya_Latn",
            "sn": "sna_Latn",
        }
        self.model_name = "facebook/nllb-200-distilled-600M"

    def _get_pipeline(self):
        """Lazy initialization of the translation pipeline."""
        global _pipeline
        if _pipeline is None:
            try:
                from transformers import pipeline
                import torch

                logger.info(
                    f"Translator: Loading {self.model_name} (this may take a while)..."
                )
                device = 0 if torch.cuda.is_available() else -1
                _pipeline = pipeline(
                    "translation", model=self.model_name, device=device
                )
                logger.info("Translator: Model loaded successfully.")
            except ImportError as e:
                logger.error(
                    "Translator: Optional translation dependencies are missing. "
                    'Install them with pip install -e ".[translation]". '
                    f"Details: {e}"
                )
                return None
            except Exception as e:
                logger.error(f"Translator: Failed to load NLLB model: {e}")
                return None
        return _pipeline

    def _is_greeting(self, text: str, lang: str) -> bool:
        """Check if text is a greeting or short phrase."""
        text_lower = text.lower().strip()
        greeting_words = GREETINGS_SOURCE.get(lang, [])
        is_short = len(text.split()) <= 3
        has_greeting = any(gw in text_lower for gw in greeting_words)
        return is_short and has_greeting

    def _protect_keywords(self, text: str) -> tuple[str, dict]:
        """Replace protected keywords with placeholders."""
        placeholder_map = {}
        protected_text = text
        for i, kw in enumerate(PROTECTED_KEYWORDS):
            placeholder = f"[[PKW{i}]]"
            if kw.lower() in text.lower():
                protected_text = protected_text.replace(kw, placeholder)
                protected_text = protected_text.replace(kw.lower(), placeholder)
                placeholder_map[placeholder] = kw
        return protected_text, placeholder_map

    def _restore_keywords(self, text: str, placeholder_map: dict) -> str:
        """Restore protected keywords from placeholders, handling NLLB mutations."""
        result = text
        for placeholder, kw in placeholder_map.items():
            # Standard restoration
            result = result.replace(placeholder, kw)
            result = result.replace(placeholder.lower(), kw)
            
            # Robust restoration for "glitched" placeholders like PKW0n or [PKW0]
            # Strip the brackets to find the core ID
            core_id = placeholder.strip("[]")
            
            # Pattern to find the core ID even if NLLB added suffixes (like PKW0n)
            # or removed brackets (like PKW0)
            pattern = re.compile(re.escape(core_id) + r"[a-zA-Z0-9]*")
            result = pattern.sub(kw, result)
            
        return result

    def translate(self, text: str, source: str = "en", target: str = "en") -> str:
        """Translates text between supported languages with enhanced handling."""
        if not text or not text.strip() or source == target:
            return text

        text_clean = text.strip()

        if self._is_greeting(text_clean, source):
            cache_key = (source, target)
            if cache_key in GREETINGS_CACHE:
                return GREETINGS_CACHE[cache_key]

        protected_text, placeholder_map = self._protect_keywords(text_clean)

        src_lang = self.code_map.get(source, "eng_Latn")
        tgt_lang = self.code_map.get(target, "eng_Latn")

        pipe = self._get_pipeline()
        if not pipe:
            return text

        try:
            result = pipe(
                protected_text,
                src_lang=src_lang,
                tgt_lang=tgt_lang,
                max_length=1024,
            )
            translated_text = result[0]["translation_text"]

            translated_text = self._restore_keywords(translated_text, placeholder_map)

            logger.debug(f"Translated: '{text_clean[:50]}' -> '{translated_text[:50]}'")
            return translated_text
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    def translate_to_english(self, text: str, source: str) -> str:
        return self.translate(text, source=source, target="en")

    def translate_from_english(self, text: str, target: str) -> str:
        return self.translate(text, source="en", target=target)


zed_translator = ZedTranslator()


def translate_text(text: str, source: str = "en", target: str = "en") -> str:
    return zed_translator.translate(text, source=source, target=target)
