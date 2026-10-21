#!/usr/bin/env python3
"""
Greeting handling for Zedchatbot.

A greeting (e.g. "hi", "muli bwanji", "mwapoleni") is not a knowledge query.
Without special handling it runs through retrieval, and the generator ends up
listing whichever documents happened to rank highest — making the assistant look
as though it only covers a couple of topics. This module detects greetings and
returns a fixed, domain-neutral welcome instead.
"""

import re
from typing import Dict, Optional

# Words that, on their own or together, constitute a greeting per language.
GREETING_WORDS: Dict[str, set] = {
    "en": {"hello", "hi", "hie", "hey", "greetings", "yo", "sup"},
    "bem": {"mwapoleni", "muli", "shani", "moni", "ngapo", "napo", "fyo"},
    "ny": {"muli", "bwanji", "moni", "mwauka", "mwauka", "zoona"},
    "sn": {"mhoro", "mhoroi", "makadii", "mangwanani", "masikati", "manheru"},
}

# Harmless filler words that may accompany a greeting.
FILLER_WORDS = {"there", "again", "zed", "zedchatbot", "bot", "please", "plz", "enyu", "bho"}

# Multi-word English greetings ("how are you") are matched as phrases.
GREETING_PHRASES = (
    "how are you",
    "how are you doing",
    "how are you today",
    "good morning",
    "good afternoon",
    "good evening",
    "nice to meet you",
    "hello there",
    "hi there",
)

# Fixed, domain-neutral welcome covering every service area the assistant supports.
# Local-language text deliberately keeps the statutory acronyms verbatim.
GREETING_REPLIES: Dict[str, str] = {
    "en": (
        "Hello! I am Zedchatbot, your community information assistant for Zambia "
        "and Zimbabwe. You can ask me about:\n\n"
        "- Identity & civic services: NRC, passport, PACRA, NAPSA\n"
        "- Tax: ZRA / TPIN\n"
        "- Education: UNZA, CBU, ECZ results, HELSB student loans, TEVETA\n"
        "- Utilities: ZESCO electricity, LWSC / NWASCO water\n"
        "- Health: NHIMA insurance, clinics, disease guidance\n"
        "- Agriculture and community funding: FISP, CDF\n\n"
        "What would you like to know today?"
    ),
    "bem": (
        "Mwapoleni! Nine Zedchatbot, umwafwi wa fya boma ku Zambia ne Zimbabwe. "
        "Kuti namwafwa pa fya boma (NRC, passport, PACRA, NAPSA), pa misonkho (ZRA/TPIN), "
        "pa fya kusambilila (UNZA, CBU, ECZ, HELSB), pa menshi ne amagetsi (ZESCO, LWSC), "
        "pa bumi (NHIMA ne chipatala), pa bulimi (FISP) ne CDF.\n\n"
        "Ni finshi mufwaya ukwishiba lelo?"
    ),
    "ny": (
        "Muli bwanji! Ine ndine Zedchatbot, wothandizira pa nkhani za boma ku Zambia ndi Zimbabwe. "
        "Mungafunsa za zikalata za boma (NRC, passport, PACRA, NAPSA), misonkho (ZRA/TPIN), "
        "maphunziro (UNZA, CBU, ECZ, HELSB), madzi ndi magetsi (ZESCO, LWSC), "
        "zaumoyo (NHIMA ndi chipatala), ulimi (FISP) ndi CDF.\n\n"
        "Kodi mufuna kudziwa chiyani lero?"
    ),
    "sn": (
        "Mhoro! Ini ndini Zedchatbot, mubatsiri wezve mabasa ehurumende mu Zambia ne Zimbabwe. "
        "Unogona kubvunza nezve zvikwangwani zvehurumende (NRC, passport, PACRA, NAPSA), "
        "mutero (ZRA/TPIN), dzidzo (UNZA, CBU, ECZ, HELSB), mvura nemagetsi (ZESCO, LWSC), "
        "hutano (NHIMA nechipatara), kurima (FISP) ne CDF.\n\n"
        "Chii chaunoda kuziva nhasi?"
    ),
}


def is_greeting(text: Optional[str], lang: str = "en") -> bool:
    """Return True when the whole message is just a greeting or salutation.

    The check is deliberately conservative: every word must belong to the greeting
    vocabulary (plus a few fillers), so a real question such as
    "What are the ZESCO tariffs?" is never mistaken for a greeting.
    """
    if not text or not text.strip():
        return False

    clean = re.sub(r"[^a-z\s']", " ", text.lower())
    words = clean.split()
    if not words or len(words) > 4:
        return False

    joined = " ".join(words)
    if any(joined == phrase or joined.startswith(phrase + " ") for phrase in GREETING_PHRASES):
        return True

    # A greeting must be made up entirely of greeting words/fillers...
    allowed = set(FILLER_WORDS)
    for vocabulary in GREETING_WORDS.values():
        allowed |= vocabulary
    if not all(word in allowed for word in words):
        return False

    # ...and include at least one actual greeting word (guards against filler-only input).
    return any(word in GREETING_WORDS.get(lang, set()) for word in words) or any(
        word in vocabulary for vocabulary in GREETING_WORDS.values() for word in words
    )


def greeting_reply(lang: Optional[str] = None) -> str:
    """Return the generic welcome message for the given language."""
    return GREETING_REPLIES.get((lang or "en").lower(), GREETING_REPLIES["en"])
