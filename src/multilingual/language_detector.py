#!/usr/bin/env python3
"""
Language detection component for multilingual support.
Enhanced with keyword-based detection for Zambian and Zimbabwean languages.
"""

from typing import Optional, Dict, Tuple
from langdetect import detect, detect_langs, DetectorFactory
from src.core.logger import logger
from src.configs.settings import settings

DetectorFactory.seed = 0


NYANJA_KEYWORDS = {
    "kodi",
    "ndi",
    "kwa",
    "mu",
    "pa",
    "ndikufuna",
    "ndikuchenjeza",
    "muli",
    "bwanji",
    "yankho",
    "chikhalidwe",
    "muno",
    "kuno",
    "chichewa",
    "zambia",
    "mwai",
    "mphatso",
    "kuyanjana",
    "kulembetsa",
    "kumene",
    "litapi",
    "ngati",
    "sikuti",
    "koma",
    "kapena",
    "mwanalume",
    "mwamuna",
    "mkazi",
    "ana",
    "achikondi",
    "ndipeza",
    "ndichita",
    "ndikhulupirira",
    "chingelezi",
    "chilankhulo",
    "maganizo",
    "buku",
    "skulu",
    "mphamvu",
    "ngongole",
    "banka",
    "chimalipiro",
    "musonko",
    "misonkho",
    "ningalipire",
    "kulipira",
    "malipiro",
    "boma",
    "chipatala",
    "dokotala",
    "mankhwala",
    "chisulo",
    "madzi",
    "ntchito",
    "galimoto",
    "bulu",
    "ng'oma",
    "modzi",
    "ziwiri",
    "tatu",
    "china",
    "zilimawiro",
    "chikondi",
    "luso",
    "lero",
    "mawa",
    "dzuka",
    "usana",
    "masiku",
    "ache",
    "awiri",
    "ndani",
    "chani",
    "yani",
    "angani",
    "kuti",
    "nditumiza",
    "ndapita",
    "ndabwera",
    "ndikugwira",
    "ndikulendra",
    "ndikulota",
    "mfiti",
    "nkhoswe",
    "senge",
    "mbuzo",
    "funso",
    "chikondi",
    "tsiku",
    "mulungu",
    "jula",
    "fuchi",
    "kavala",
    "kuya",
    "kunja",
    "mkati",
    "pali",
    "palibe",
    "Mwina",
    "Mwini",
    "Amini",
}

BEMBA_KEYWORDS = {
    "shani",
    "muli",
    "shiko",
    "fyo",
    "apo",
    "cino",
    "ula",
    "ile",
    "ngapo",
    "nacapo",
    "nabo",
    "naci",
    "shikulu",
    "bana",
    "ume",
    "ukunda",
    "ukwingata",
    "ukwishiba",
    "ukucita",
    "ukulanda",
    "mu mfumu",
    "pano",
    "kuno",
    "ukutotela",
    "ukukaka",
    "mwapoleni",
    "twatwala",
    "ngwandemi",
    "buku",
    "ishiku",
    "umulo",
    "ipikulupu",
    "ukufwaya",
    "ukufwilako",
    "ngakwai",
    "namikongole",
    "umulimo",
    "inkama",
    "ifintu",
    "ichalo",
    "umusankwa",
    "icalo",
    "ukwata",
    "ukufumya",
    "ukusunga",
    "ukulomba",
    "ukwaisa",
    "ukusoka",
    "ukufundisha",
    "amalawi",
    "amakuni",
    "ebuleti",
    "ichipata",
    "umushi",
    "inkonoka",
    "ichinsunsu",
    "ukusonkola",
    "ukukamata",
    "ukusambila",
    "ukusumina",
    "ukusoneka",
    "ukusonkota",
    "fila",
    "fiko",
    "cabe",
    "mwalai",
    "kabili",
    "nokuti",
    "fye",
    "lelo",
    "mailo",
    "echi",
    "elyo",
    "konko",
    "nakulila",
    "ukusanga",
    "ukusendama",
    "ukukopa",
    "ukukwacha",
    "icaputika",
    "ikalamba",
    "ilombe",
    "iponga",
    "isingleso",
    "umutwe",
    "intu",
    "ubuntu",
    "umulunga",
    "ukunda",
}

SHONA_KEYWORDS = {
    "mhoro",
    "mhoroi",
    "ndiri",
    "sei",
    "zvinhu",
    "kana",
    "kuti",
    "iko",
    "zvino",
    "mazuva",
    "nguva",
    "vanhu",
    "mushandi",
    "mufariri",
    "hedu",
    "tete",
    "amai",
    "baba",
    "mwana",
    "mabasa",
    "gore",
    "mwedzi",
    "masiku",
    "kuno",
    "kunze",
    "zvemuno",
    "zvinoita",
    "ndinovimba",
    "ndapota",
    "zvine",
    "zvinopa",
    "hana",
    "mbira",
    "ngoma",
    "musha",
    "hanzi",
    "zvinoda",
    "zvayo",
    "zvedu",
    "zvaro",
    "zvangu",
    "zvakanaka",
    "ndanga",
    "ndakagara",
    "ndakanga",
    "ndichava",
    "zvandinoda",
    "denda",
    "tsime",
    "mupfungwa",
    "gwara",
    "kugara",
    "vamwe",
    "vese",
    "vari",
    "vanenge",
    "chimwe",
    "maviri",
    "matatu",
    "mana",
    "shanu",
    "enda",
    "dzoka",
    "svondo",
    "chishanu",
    "mutero",
    "chikoro",
    "mari",
    "chipatara",
}

KNOWN_BEMBA_PHRASES = [
    "mwapoleni",
    "shani",
    "ngapo",
    "napo fyo",
    "fyo shani",
    "bana ba",
    "umuleti",
    "nakulila",
    "shikulu",
    "ngakwai",
]

KNOWN_NYANJA_PHRASES = [
    "muli bwanji",
    "ndikufuna",
    "kodi",
    "yankho",
    "chikhalidwe",
    "kuyanjana",
    "lero",
    "mawa",
    "kwai",
    "ndani angakhale",
]

KNOWN_SHONA_PHRASES = [
    "mhoro",
    "mhoroi",
    "makadii",
    "makadii henyu",
    "ndiri bho",
    "ndiri nani",
    "zvinhu zviri sei",
    "ndinokumbira rubatsiro",
    "ndatenda zvikuru",
    "mangwanani",
    "masikati",
    "manheru",
]


class LanguageDetector:
    """Handles detection of user input language with keyword-based fallback."""

    def __init__(self):
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        self.default_language = settings.DEFAULT_LANGUAGE
        self._init_keywords()

    def _init_keywords(self):
        self.keywords: Dict[str, set] = {
            "ny": NYANJA_KEYWORDS,
            "bem": BEMBA_KEYWORDS,
            "sn": SHONA_KEYWORDS,
        }
        self.phrases: Dict[str, set] = {
            "ny": KNOWN_NYANJA_PHRASES,
            "bem": KNOWN_BEMBA_PHRASES,
            "sn": KNOWN_SHONA_PHRASES,
        }

    def _score_text(self, text: str, lang: str) -> Tuple[int, int]:
        """Returns (word_matches, phrase_matches) for a language."""
        text_lower = text.lower()
        words = set(
            text_lower.replace(",", " ")
            .replace(".", " ")
            .replace("?", " ")
            .replace("!", " ")
            .split()
        )

        word_matches = len(words & self.keywords.get(lang, set()))

        phrase_matches = 0
        for phrase in self.phrases.get(lang, set()):
            if phrase in text_lower:
                phrase_matches += 2

        return word_matches, phrase_matches

    def detect_language(self, text: str) -> str:
        """Detects language with keyword-based fallback for African languages."""
        if not text or not text.strip():
            return self.default_language

        text_lower = text.lower().strip()

        if len(text_lower) <= 3:
            return self._detect_short_text(text_lower)

        try:
            detected = detect(text)
            if detected == "en":
                scores = {
                    lang: self._score_text(text, lang) for lang in ["ny", "bem", "sn"]
                }
                best_lang = max(scores, key=lambda x: scores[x][0] + scores[x][1])
                if scores[best_lang][0] + scores[best_lang][1] >= 2:
                    logger.info(
                        f"Keyword override: langdetect={detected}, but keywords suggest {best_lang}"
                    )
                    return best_lang
                return "en"

            scores = {
                lang: self._score_text(text, lang) for lang in ["ny", "bem", "sn"]
            }
            best_lang = max(scores, key=lambda x: scores[x][0] + scores[x][1])

            if scores[best_lang][0] + scores[best_lang][1] >= 2:
                logger.debug(
                    f"Detected {best_lang} via keywords (langdetect: {detected})"
                )
                return best_lang

            return detected

        except Exception as e:
            logger.warning(f"Language detection failed: {e}, falling back to keywords")
            return self._detect_by_keywords_only(text)

    def _detect_short_text(self, text: str) -> str:
        """Detects language for very short text using keywords."""
        scores = {lang: self._score_text(text, lang) for lang in ["ny", "bem", "sn"]}
        best_lang = max(scores, key=lambda x: scores[x][0] + scores[x][1])

        if scores[best_lang][0] > 0 or scores[best_lang][1] > 0:
            return best_lang

        if "en" in text or "the" in text or "is" in text or "a" in text:
            return "en"

        return self.default_language

    def _detect_by_keywords_only(self, text: str) -> str:
        """Fallback detection using only keywords."""
        scores = {lang: self._score_text(text, lang) for lang in ["ny", "bem", "sn"]}
        best_lang = max(scores, key=lambda x: scores[x][0] + scores[x][1])

        if scores[best_lang][0] + scores[best_lang][1] >= 2:
            return best_lang

        return self.default_language

    def get_confidence_scores(self, text: str):
        """Returns confidence scores for all languages."""
        try:
            langdetect_scores = {
                str(l).split(":")[0]: l.prob for l in detect_langs(text)
            }
            keyword_scores = {
                lang: self._score_text(text, lang) for lang in ["ny", "bem", "sn"]
            }
            return {"langdetect": langdetect_scores, "keyword": keyword_scores}
        except Exception as e:
            logger.error(f"Failed to get language confidence scores: {e}")
            return {}


language_detector = LanguageDetector()


def detect_language(text: str) -> str:
    """Functional wrapper for language detection."""
    return language_detector.detect_language(text)
