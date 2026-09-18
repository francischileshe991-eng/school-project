#!/usr/bin/env python3
"""
Language detection component for multilingual support.
Enhanced with high-precision lexical and morphological detection for Zambian and Zimbabwean languages.
Strictly guarantees output is within settings.SUPPORTED_LANGUAGES ('en', 'bem', 'ny', 'sn').
"""

import re
from typing import Optional, Dict, Tuple
from langdetect import detect, detect_langs, DetectorFactory
from src.core.logger import logger
from src.configs.settings import settings

DetectorFactory.seed = 0

# 1. Distinctive English Functional & Civic Vocabulary
ENGLISH_INDICATORS = {
    "the", "what", "how", "when", "where", "who", "why", "which",
    "can", "could", "is", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "have", "has", "had", "to", "for", "in", "on",
    "at", "by", "from", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "of",
    "apply", "application", "get", "requirements", "fees", "cost",
    "register", "registration", "passport", "license", "licence",
    "tariffs", "electricity", "water", "card", "school", "university",
    "bursary", "loan", "loans", "court", "rights", "tax", "child",
    "children", "age", "years", "free", "money", "fraud", "report",
    "police", "first", "time", "green", "residential", "customers",
    "explain", "statutory", "official", "limit", "allowed", "mandatory",
    "i", "you", "he", "she", "we", "they", "my", "your", "our", "their"
}

# 2. Distinctive icibemba Lexical Markers (Conversational & Inflected)
BEMBA_KEYWORDS = {
    "shani", "finshi", "cinshi", "ninani", "kwi", "lilali", "pantunshi", "mulandunshi",
    "mwapoleni", "mukwai", "natotela", "fye", "kabili", "nomba", "mailo", "lelo",
    "amalaiti", "malaiti", "umufundo", "imbuto", "ubumi", "ing'anda", "ulupwa",
    "napoka", "bapoka", "ndipoka", "poka",
    "napempula", "bapempula", "pempula",
    "nailemba", "bailemba", "lembesha", "kulembesha", "kwingila",
    "balefwaya", "alefwaya", "ndifwaya", "tulefwaya", "fwaya", "ukufwaya",
    "banjelele", "ingileni", "njebeleni", "njeba", "sosa", "landa",
    "balebomba", "tulebomba", "bomba", "ukubomba",
    "naya", "balaya", "kuya", "ukuya",
    "mwaiche", "mukalamba", "icikwati", "isukulu", "ishuko",
    "indalama", "impapulo", "icitupa", "akalembera", "tabakwata", "nshikwete",
    "mwalai", "nga", "fyo", "apo", "cino", "nabo", "naci", "shikulu",
    "bana", "ume", "ukunda", "ukwishiba", "ukucita", "ukulanda", "pano",
    "kuno", "ukutotela", "twatwala", "umulimo", "inkama", "ifintu", "ichalo",
    "icalo", "ukwata", "ukufumya", "ukusunga", "ukulomba", "ukwaisa",
    "umushi", "ukusambila", "ukusumina", "ukusoneka", "cabe", "echi", "elyo",
    "ukusanga", "ukukwacha", "ubuntu", "umutwe", "nangu", "kwati"
}

# 3. Distinctive chiNyanja / Chewa Lexical Markers
NYANJA_KEYWORDS = {
    "kodi", "bwanji", "ndani", "chani", "chifukwa", "chiyani", "liti", "chonde", "moni",
    "muli bwanji", "zikomo", "kuchokera", "misonkho", "musonko", "katemera", "posachedwa",
    "ndikufuna", "akufuna", "tifuna", "kufuna", "ndikufunsa", "funsa",
    "ndingatenge", "kutenga", "ndingapeze", "kupeza", "ndingachite", "kuchita",
    "ndingapemphe", "kupempha", "ndingalipire", "kulipira", "malipiro",
    "zitheka", "tingathe", "zofunikira", "kulembetsa", "kukhala",
    "munthu", "anthu", "banja", "makolo", "dziko", "yankho", "kuyanjana",
    "dzulo", "usana", "usiku", "chimodzi", "ziwiri", "zitatu", "zinayi", "zisanu",
    "chikhalidwe", "mwai", "mphatso", "litapi", "ngati", "sikuti", "koma", "kapena",
    "mwanalume", "mwamuna", "mkazi", "ana", "achikondi", "ndipeza", "ndichita",
    "ndikhulupirira", "chingelezi", "chilankhulo", "maganizo", "buku", "skulu",
    "mphamvu", "ngongole", "banka", "chimalipiro", "ningalipire", "chipatala",
    "dokotala", "mankhwala", "madzi", "ntchito", "galimoto", "lero", "mawa",
    "dzuka", "masiku", "nditumiza", "ndapita", "ndabwera", "ndikugwira",
    "funso", "kunja", "mkati", "palibe", "mwina", "mwini", "amini"
}

# 4. Distinctive chiShona Lexical Markers
SHONA_KEYWORDS = {
    "sei", "ko", "chii", "ndiani", "rini", "seiko", "mhoro", "mhoroi", "makadii",
    "makadii henyu", "ndiri", "ndiri bho", "ndiri nani", "ndatenda", "zvikuru",
    "chitupa", "mutero", "musha", "mabasa", "vana", "baba", "amai", "mukadzi",
    "murume", "chikoro", "chipatara", "nguva", "mazuva", "mangwanani", "masikati",
    "manheru", "zvakanaka", "zvino", "pamusoro", "ndinoda", "vanoda", "tinoda",
    "ndinokumbira", "kumbira", "ndingawana", "kuwana", "ndinganyorera", "kunyora",
    "ndingaite", "kuita", "ndinogona", "zvinoita", "zvinhu", "kana", "iko",
    "mushandi", "tete", "mwana", "gore", "mwedzi", "ndinovimba", "ndapota",
    "zvine", "zvinopa", "hana", "mbira", "ngoma", "hanzi", "zvinoda", "zvayo",
    "zvedu", "zvaro", "zvangu", "ndanga", "ndakagara", "ndakanga", "ndichava",
    "zvandinoda", "tsime", "mupfungwa", "gwara", "kugara", "vamwe", "vese",
    "vari", "vanenge", "chimwe", "maviri", "matatu", "mana", "shanu", "enda",
    "dzoka", "svondo", "chishanu", "mari"
}

# 5. Idiomatic & Salutation Phrases
KNOWN_BEMBA_PHRASES = [
    "mwapoleni", "shani", "ngapo", "napo fyo", "fyo shani", "bana ba",
    "umuleti", "nakulila", "shikulu", "ngakwai", "natotela", "mukwai",
    "pa kuti", "kuti napoka", "kuti nailemba", "kuti napempula"
]

KNOWN_NYANJA_PHRASES = [
    "muli bwanji", "ndikufuna", "kodi", "yankho", "chikhalidwe", "kuyanjana",
    "lero", "mawa", "kwai", "ndani angakhale", "zikomo", "chonde",
    "kodi ndingatenge", "ndingapemphe", "ndingalipire", "ndingapeze"
]

KNOWN_SHONA_PHRASES = [
    "mhoro", "mhoroi", "makadii", "makadii henyu", "ndiri bho", "ndiri nani",
    "zvinhu zviri sei", "ndinokumbira rubatsiro", "ndatenda zvikuru",
    "mangwanani", "masikati", "manheru", "ndingawana sei", "ndinganyorera sei"
]

# Morphological Regex Patterns for Bantu Prefix Signatures
BEMBA_PREFIX_RE = re.compile(r"^(bale|tule|nde|nshi|taba|ala|mwa|ici|ifi|umu|imi|ubu)[a-z]{3,}")
NYANJA_PREFIX_RE = re.compile(r"^(ndiku|tiku|akufu|ndinga|tinga|adzakha|chi|zi|ma)[a-z]{3,}")
SHONA_PREFIX_RE = re.compile(r"^(ndino|tino|vano|ndiri|zviri|zvin)[a-z]{3,}")


class LanguageDetector:
    """Robust, highly accurate language detector for English, Bemba, Nyanja, and Shona."""

    def __init__(self):
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.default_language = settings.DEFAULT_LANGUAGE

    def _score_text(self, text: str, lang: str) -> Tuple[int, int]:
        """Returns (word_matches, phrase_matches) for a specific language."""
        text_lower = text.lower()
        words = set(re.findall(r"[a-z']+", text_lower))

        keywords_map = {
            "bem": BEMBA_KEYWORDS,
            "ny": NYANJA_KEYWORDS,
            "sn": SHONA_KEYWORDS,
        }
        phrases_map = {
            "bem": KNOWN_BEMBA_PHRASES,
            "ny": KNOWN_NYANJA_PHRASES,
            "sn": KNOWN_SHONA_PHRASES,
        }

        word_matches = len(words & keywords_map.get(lang, set()))
        phrase_matches = sum(2 for p in phrases_map.get(lang, []) if p in text_lower)
        return word_matches, phrase_matches

    def detect_language(self, text: str) -> str:
        """
        Detects language strictly returning one of settings.SUPPORTED_LANGUAGES ('en', 'bem', 'ny', 'sn').
        Combines English indicator matching, African keyword scoring, and Bantu morphological analysis.
        """
        if not text or not text.strip():
            return self.default_language

        clean = text.lower().strip()

        # Strip country routing prefix if present
        clean = re.sub(r"^(!zw|zw:|\[zw\]|!zm|zm:|\[zm\])\s*", "", clean)

        words = re.findall(r"[a-z']+", clean)
        if not words:
            return self.default_language

        # 1. Evaluate English Indicators
        en_matches = sum(1 for w in words if w in ENGLISH_INDICATORS)
        en_ratio = en_matches / len(words)

        # 2. Evaluate African Language Keywords & Phrases
        bem_word, bem_phrase = self._score_text(clean, "bem")
        ny_word, ny_phrase = self._score_text(clean, "ny")
        sn_word, sn_phrase = self._score_text(clean, "sn")

        bem_score = (bem_word * 2) + bem_phrase
        ny_score = (ny_word * 2) + ny_phrase
        sn_score = (sn_word * 2) + sn_phrase

        # 3. Morphological Affix Analysis
        for w in words:
            if BEMBA_PREFIX_RE.match(w):
                bem_score += 1
            if NYANJA_PREFIX_RE.match(w):
                ny_score += 1
            if SHONA_PREFIX_RE.match(w):
                sn_score += 1

        # 4. Disambiguation for Shared Terms ("kuti", "zambia", etc.)
        if "kuti" in words:
            if any(w.startswith("na") or w.startswith("bale") or w == "shani" or "pa kuti" in clean for w in words):
                bem_score += 2
            elif any(w.startswith("ndi") or w == "bwanji" or w == "kodi" for w in words):
                ny_score += 2

        # 5. English Primary Gate
        max_african = max(bem_score, ny_score, sn_score)
        if en_matches >= 2 and en_ratio >= 0.35 and max_african <= 1:
            return "en"
        if en_matches >= 3 and en_matches > max_african:
            return "en"

        # 6. African Language Selection
        scores = {"bem": bem_score, "ny": ny_score, "sn": sn_score}
        best_african = max(scores, key=lambda k: scores[k])

        if scores[best_african] > 0:
            # Handle Bemba vs Nyanja close tie decisively
            if scores["bem"] == scores["ny"] and scores["bem"] > 0:
                if "shani" in clean or "finshi" in clean or "napoka" in clean or "mwapoleni" in clean:
                    return "bem"
                if "bwanji" in clean or "kodi" in clean or "ndingatenge" in clean or "zikomo" in clean:
                    return "ny"
                return "bem"  # Default to Bemba as primary Zambian lingua franca
            return best_african

        # 7. Fallback to statistical langdetect (guaranteeing supported language)
        try:
            detected = detect(clean)
            if detected == "en":
                return "en"
            if detected in self.supported_languages:
                return detected
        except Exception:
            pass

        return self.default_language

    def get_confidence_scores(self, text: str) -> Dict:
        """Returns structured confidence scores for evaluation inspection."""
        clean = text.lower().strip()
        words = set(re.findall(r"[a-z']+", clean))
        try:
            langdetect_scores = {str(l).split(":")[0]: l.prob for l in detect_langs(clean)}
        except Exception:
            langdetect_scores = {}

        return {
            "langdetect": langdetect_scores,
            "keyword": {
                "en": sum(1 for w in words if w in ENGLISH_INDICATORS),
                "bem": self._score_text(clean, "bem"),
                "ny": self._score_text(clean, "ny"),
                "sn": self._score_text(clean, "sn"),
            }
        }


# Global singleton
language_detector = LanguageDetector()


def detect_language(text: str) -> str:
    """Functional wrapper for language detection."""
    return language_detector.detect_language(text)
