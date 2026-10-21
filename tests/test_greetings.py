import pytest
from src.multilingual.greetings import GREETING_REPLIES, greeting_reply, is_greeting


@pytest.mark.parametrize(
    "text",
    [
        "hi",
        "Hi",
        "hello",
        "Hello there",
        "hey",
        "how are you",
        "good morning",
        "muli bwanji",
        "Mwapoleni",
        "mwapoleni shani",
        "mhoro",
        "moni",
    ],
)
def test_greetings_are_detected(text: str) -> None:
    assert is_greeting(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "What are the 2026 ZESCO electricity tariffs?",
        "How do I apply for a National Registration Card (NRC)?",
        "How do I contribute to NHIMA health insurance?",
        "Ndingapemphe bwanji ngongole ya maphunziro ku HELSB?",
        "Kodi ndalama za NHIMA zochotsa pa mwezi ndi zingati?",
        "Who is eligible to apply for the HELSB student loan in Zambia?",
        "Mwapoleni, kuti napoka shani NRC?",
        "How do I check my ZIMSEC results online?",
        "What are the requirements for applying to UNZA?",
        "How do farmers apply for FISP fertilizer and seed?",
    ],
)
def test_real_questions_are_not_treated_as_greetings(text: str) -> None:
    assert is_greeting(text) is False


def test_greeting_reply_covers_all_domains_and_falls_back_to_english() -> None:
    reply = greeting_reply("en")
    for topic in ("NRC", "ZESCO", "NHIMA", "HELSB", "FISP", "CDF", "ECZ", "UNZA"):
        assert topic in reply

    # An unknown/None language falls back to English rather than crashing.
    assert greeting_reply(None) == GREETING_REPLIES["en"]
    assert greeting_reply("xx") == GREETING_REPLIES["en"]


@pytest.mark.parametrize("lang,marker", [("ny", "Muli bwanji"), ("bem", "Mwapoleni"), ("sn", "Mhoro")])
def test_greeting_reply_is_localised(lang: str, marker: str) -> None:
    assert greeting_reply(lang).startswith(marker)


def test_pipeline_returns_generic_greeting_without_retrieval() -> None:
    from unittest.mock import patch

    from src.rag.pipeline import RAGPipeline

    # Deliberately build the pipeline without retrievers/generator: if the greeting
    # fast-path did not short-circuit, this would raise AttributeError on retrieval.
    pipe = RAGPipeline.__new__(RAGPipeline)

    with patch("src.rag.pipeline.greeting_reply", return_value="WELCOME") as mock_reply:
        answer, sources = pipe.generate_reply(message="muli bwanji", country="zm", language="auto")

    mock_reply.assert_called_once()
    assert answer == "WELCOME"
    assert sources == []



def test_greeting_replies_cover_every_supported_language() -> None:
    for lang in ("en", "bem", "ny", "sn"):
        reply = greeting_reply(lang)
        assert isinstance(reply, str) and len(reply) > 40
        # Institutional acronyms must pass through untranslated in every language.
        assert "NRC" in reply and "NHIMA" in reply and "ZESCO" in reply
    assert greeting_reply("xx") == GREETING_REPLIES["en"]
