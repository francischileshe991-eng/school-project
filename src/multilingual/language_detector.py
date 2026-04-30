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
    "ndin呼应",
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
    "chGovernment",
    "chipatala",
    "dokotala",
    "mankhwala",
    "chisulo",
    "madzi",
    "ntchito",
    "galimoto",
    "bulu",
    "ng'oma",
    "dance",
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
    "，夏",
    "ache",
    "awiri",
    "ndani",
    "chani",
    "yani",
    "angani",
    "kuti",
    "bvin",
    "ム",
    "тА",
    "nditumiz",
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
    "luso",
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
    "ukufwaya",
    "ukufwilako",
    "ngakwai",
    "namikongole",
    "ifilelal",
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
    "ndiri",
    "sei",
    "zvi",
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
    "amaig",
    "akad",
    "ndak",
    "ndaka",
    "ndiri",
    "ndinovh",
    "ndinoz",
    "ndinov",
    "ndaig",
    "ndakag",
    "ndich",
    "zvandin",
    "ndichavh",
    "zvich",
    "zving",
    "ching",
    "chinga",
    "zvanga",
    "zvinhu",
    "mabasa",
    "nhing",
    "ndemo",
    "kad",
    "gore",
    "mwedzi",
    "masiku",
    "avh",
    "kuno",
    "kunze",
    "zvirm",
    "zvawak",
    "zvemuno",
    "zvakaf",
    "zvinoita",
    "ndinovimba",
    "ndokumb",
    "ndokush",
    "ndoku",
    "ndokuf",
    "zvak",
    "zvine",
    "zvinod",
    "zvinopa",
    "zvinot",
    "hanz",
    "hana",
    "mbira",
    "ngoma",
    "musha",
    "hanzi",
    "ndaura",
    "zvinoda",
    "zvayo",
    "zvek",
    "zvedu",
    "zvaro",
    "zvangu",
    "zvaw",
    "zvakan",
    "zvakash",
    "zvakaw",
    "ndanga",
    "ndakagara",
    "ndakanga",
    "ndichango",
    "ndichava",
    "zvandinoda",
    "zvichandinoda",
    "kwandak",
    "kwandai",
    "kwando",
    "zvinzwa",
    "zvinopfu",
    "zvinokwan",
    "zvinotong",
    "zvinotung",
    "denda",
    "tsime",
    "bha",
    "mupfungwa",
    "umupfungwa",
    "hwind",
    "gwar",
    "gwara",
    "kugar",
    "kugarwa",
    "kugaris",
    "vamwe",
    "vese",
    "vavi",
    "vari",
    "vanga",
    "vanenge",
    "chimwe",
    "zviny",
    "maviri",
    "matatu",
    "mana",
    "sanu",
    "fambi",
    "tor",
    "nema",
    "enda",
    "dzoka",
    "wira",
    "nguva",
    "chisi",
    "mond",
    "svondo",
    "chipiki",
    "chishanu",
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
    "，夏",
    "kwai",
    "ndani angakhale",
]

KNOWN_SHONA_PHRASES = [
    "mhoro",
    "ndiri",
    "sei",
    "zvinhu",
    "ndinovh",
    "kana",
    "kuti",
    "zvino",
    "mazuva",
    "ndaig",
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
