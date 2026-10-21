#!/usr/bin/env python3
"""
Local Translation service using Meta's NLLB-200 model.
Enhanced with phrase caching, short text handling, and keyword protection.
"""

import re
from typing import Optional
from src.core.logger import logger
from src.configs.settings import settings

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
    "CDF",
    "WDC",
    "ZICTA",
    "RTSA",
    "NAPSA",
    "PACRA",
    "HELSB",
    "TEVETA",
    "FISP",
    "FRA",
    "Zambia",
    "Zimbabwe",
    "Zambian",
    "Zimbabwean",
    "Bemba",
    "Nyanja",
    "Shona",
]

TYPOGRAPHY_MAP = {
    "\u2018": "'",   # Left single quotation mark
    "\u2019": "'",   # Right single quotation mark / typographic apostrophe
    "\u02BC": "'",   # Modifier letter apostrophe
    "\u02BB": "'",   # Modifier letter turned comma
    "\u201C": '"',   # Left double quotation mark
    "\u201D": '"',   # Right double quotation mark
    "\u2013": "-",   # En dash
    "\u2014": "--",  # Em dash
    "\u00A0": " ",   # Non-breaking space
    "\uFFFD": "",    # Unicode replacement character
}


def normalize_typography(text: Optional[str]) -> str:
    """Normalizes typographic curly quotes and smart apostrophes to standard ASCII equivalents.
    
    Prevents replacement character artifacts (e.g. 'Nzopanda') in Windows terminal environments
    (CP1252/CP437) and ensures clean UTF-8 passthrough across Web, Console, and WhatsApp.
    """
    if not text:
        return text or ""
    out = text
    for old, new in TYPOGRAPHY_MAP.items():
        out = out.replace(old, new)
    return out


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

    def _translate_with_gemini(self, text: str, source: str, target: str) -> Optional[str]:
        """Translates text using Google Gemini API with multi-model fallback."""
        api_key = getattr(settings, "GOOGLE_API_KEY", None)
        if not api_key or "your_" in api_key.lower():
            return None

        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=30000))
        except Exception as e:
            logger.warning(f"Translator: Google GenAI client initialization failed: {e}")
            return None

        lang_names = {
            "en": "English",
            "bem": "Bemba (Icibemba)",
            "ny": "Nyanja / Chichewa",
            "sn": "Shona (ChiShona)",
        }
        source_name = lang_names.get(source, source)
        target_name = lang_names.get(target, target)

        # Cultural and dialect guidance for contemporary Southern African communication
        dialect_guidance = ""
        if target == "bem":
            dialect_guidance = (
                "Dialect Guidance for Bemba (Icibemba):\n"
                "- Use natural, contemporary Zambian Bemba as spoken everyday in Zambia (Copperbelt and Lusaka).\n"
                "- Avoid archaic, classical, or missionary/biblical vocabulary (e.g., do NOT use 'amatekeleo', use clear modern terms like 'ifyo mwingalomba', 'konkeni ishi nshila', 'ifilefwaikwa', 'ifyo mulingile ukulipila').\n"
                "- Use respectful, polite phrasing (e.g., 'mwingakonka', 'kabiyeni', 'lipileni') suitable for public civic guidance.\n"
                "- Keep common modern civic and digital terms natural (e.g., 'portal', 'website', 'online', 'passport', 'kopi', 'mapeji') rather than attempting awkward archaic coinages.\n"
            )
        elif target == "ny":
            dialect_guidance = (
                "Dialect Guidance for Nyanja (Chinyanja / Chichewa):\n"
                "- Use natural, contemporary Zambian Nyanja as spoken in Lusaka and Eastern Province.\n"
                "- Use clear, respectful civic phrasing (e.g., 'zofunika', 'mmene mungalipilire', 'pitani').\n"
                "- Keep common modern civic and digital terms natural.\n"
            )
        elif target == "sn":
            dialect_guidance = (
                "Dialect Guidance for Shona (ChiShona):\n"
                "- Use natural, contemporary ChiShona as spoken in Zimbabwe.\n"
                "- Maintain polite, clear civic phrasing.\n"
            )

        prompt = (
            f"You are an expert Southern African translator specializing in contemporary Zambian and Zimbabwean civic communication.\n"
            f"Translate the following text faithfully and fluently from {source_name} into {target_name}.\n\n"
            f"{dialect_guidance}\n"
            f"Strict Rules:\n"
            f"1. Output ONLY the translated text. Do not include introductory notes, explanations, or quotes.\n"
            f"2. Keep institutional acronyms, government bodies, currency, and proper nouns verbatim "
            f"(e.g., NRC, ZRA, NHIMA, ECZ, RTSA, PACRA, ZESCO, UNZA, Zambia, Zimbabwe, Kwacha, K500).\n"
            f"3. Preserve all markdown formatting, bullet points, numbers, and paragraph structure.\n\n"
            f"Text to Translate:\n{text}"
        )

        models_to_try = [
            getattr(settings, "GEMINI_MODEL", "gemini-3.8-flash"),
            getattr(settings, "GEMINI_FALLBACK_MODEL", "gemini-flash-lite-latest"),
        ]
        # Deduplicate while preserving order, max 2 attempts
        seen = set()
        deduped = [m for m in models_to_try if not (m in seen or seen.add(m))][:2]

        for model in deduped:
            try:
                resp = client.models.generate_content(model=model, contents=prompt)
                if resp and resp.text:
                    out = resp.text.strip()
                    if out.startswith("```") and out.endswith("```"):
                        lines = out.splitlines()
                        if len(lines) >= 2:
                            out = "\n".join(lines[1:-1]).strip()
                    return out
            except Exception as e:
                logger.debug(f"Translator: Gemini model {model} translation attempt failed: {e}")
                continue

        logger.warning("Translator: All Gemini model translation attempts failed, falling back to Groq.")
        return None

    def _translate_with_groq(self, text: str, source: str, target: str) -> Optional[str]:
        """Translates text using Groq's fast inference API as a fallback to Gemini."""
        api_key = getattr(settings, "GROQ_API_KEY", None)
        if not api_key or "your_" in api_key.lower():
            return None

        lang_names = {
            "en": "English",
            "bem": "Bemba (Icibemba) as spoken in Zambia",
            "ny": "Nyanja / Chichewa as spoken in Zambia",
            "sn": "Shona (ChiShona) as spoken in Zimbabwe",
        }
        source_name = lang_names.get(source, source)
        target_name = lang_names.get(target, target)

        prompt = (
            f"You are an expert Southern African translator. "
            f"Translate the following text faithfully from {source_name} into {target_name}.\n"
            f"Rules: Output ONLY the translated text. No notes, no explanations. "
            f"Keep institutional acronyms (NRC, ZRA, NHIMA, ZESCO, UNZA, ECZ, RTSA, PACRA, Kwacha) verbatim. "
            f"Preserve all markdown formatting and paragraph structure.\n\n"
            f"Text to translate:\n{text}"
        )

        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage

            groq_model = getattr(settings, "GROQ_MODEL", "qwen/qwen3.8-27b")
            llm = ChatOpenAI(
                model=groq_model,
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
                temperature=0.1,
                timeout=20.0,
                max_retries=1,
            )
            result = llm.invoke([HumanMessage(content=prompt)])
            out = result.content.strip() if result and result.content else None
            if out:
                logger.info(f"Translator: Translated via Groq ({source} -> {target})")
                return out
        except Exception as e:
            logger.warning(f"Translator: Groq translation failed: {e}")

        return None

    def translate(self, text: str, source: str = "en", target: str = "en") -> str:
        """Translates text between supported languages with enhanced handling."""
        if not text or not text.strip() or source == target:
            return text

        text_clean = text.strip()

        # Fast path 1: Instant Greetings cache
        if self._is_greeting(text_clean, source):
            cache_key = (source, target)
            if cache_key in GREETINGS_CACHE:
                return GREETINGS_CACHE[cache_key]

        # Fast path 2: Google Gemini cloud translation if configured
        provider = getattr(settings, "TRANSLATION_PROVIDER", "gemini").lower()
        if provider == "gemini":
            gemini_result = self._translate_with_gemini(text_clean, source, target)
            if gemini_result:
                logger.info(f"Translator: Translated via Gemini ({source} -> {target})")
                return normalize_typography(gemini_result)
            # Gemini failed — try Groq as cloud fallback before NLLB
            groq_result = self._translate_with_groq(text_clean, source, target)
            if groq_result:
                return normalize_typography(groq_result)

        if provider == "groq":
            groq_result = self._translate_with_groq(text_clean, source, target)
            if groq_result:
                return normalize_typography(groq_result)

        # Fallback path: Local NLLB-200 Neural Machine Translation
        protected_text, placeholder_map = self._protect_keywords(text_clean)

        src_lang = self.code_map.get(source, "eng_Latn")
        tgt_lang = self.code_map.get(target, "eng_Latn")

        pipe = self._get_pipeline()
        if not pipe:
            return normalize_typography(text)

        try:
            result = pipe(
                protected_text,
                src_lang=src_lang,
                tgt_lang=tgt_lang,
                max_length=1024,
            )
            translated_text = result[0]["translation_text"]

            translated_text = self._restore_keywords(translated_text, placeholder_map)

            logger.debug(f"Translated via NLLB: '{text_clean[:50]}' -> '{translated_text[:50]}'")
            return normalize_typography(translated_text)
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return normalize_typography(text)

    def translate_to_english(self, text: str, source: str) -> str:
        return self.translate(text, source=source, target="en")

    def translate_from_english(self, text: str, target: str) -> str:
        return self.translate(text, source="en", target=target)


zed_translator = ZedTranslator()


def translate_text(text: str, source: str = "en", target: str = "en") -> str:
    return zed_translator.translate(text, source=source, target=target)
