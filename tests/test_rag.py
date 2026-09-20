import pytest
from langchain_core.documents import Document
from src.rag.pipeline import generate_reply
from src.rag.generator import _clean_truncate
from src.core.database import db
from src.knowledge_base.vector_store import ZedVectorStore
from src.core.exceptions import VectorStoreError


def test_clean_truncate() -> None:
    # Test text shorter than max_len
    short = "Hello world."
    assert _clean_truncate(short, 50) == "Hello world."

    # Test sentence boundary truncation
    sentence_text = "Sentence one. Sentence two. Extra words that make it longer."
    # With max_len=30, "Sentence one. Sentence two." has boundary at index 26
    res = _clean_truncate(sentence_text, 30)
    assert res.endswith(".")
    assert "Sentence one. Sentence two." in res

    # Test word boundary fallback
    word_text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7"
    res_word = _clean_truncate(word_text, 15)
    assert res_word == "Word1 Word2..."


def test_database_ping() -> None:
    assert db.ping() is True


def test_vector_store_invalid_country_validation() -> None:
    vs = ZedVectorStore.__new__(ZedVectorStore)
    vs.base_path = db.db_path.parent / "vector_store"
    with pytest.raises(VectorStoreError):
        vs._get_country_db_path("invalid_country_xyz")


from unittest.mock import patch, MagicMock


def test_generate_reply_returns_answer_and_sources() -> None:
    mock_doc = Document(
        page_content="Passports are issued by the Department of National Registration and Citizenship.",
        metadata={"source": "data/raw/zm/government/nrc_passport_guide.txt"}
    )
    with patch("src.rag.retriever.ZedRetriever.get_relevant_context", return_value=[mock_doc]), \
         patch("src.rag.generator.ZedGenerator.generate", return_value="To apply for a passport, visit the passport office."), \
         patch("src.core.database.DatabaseManager.log_interaction"):
        answer, sources = generate_reply("How do I apply for a passport?", "zm", "en")
        assert isinstance(answer, str)
        assert len(answer) > 0
        assert isinstance(sources, list)
        assert len(sources) == 1
        assert "nrc_passport_guide.txt" in sources[0]


from src.rag.generator import _is_refusal, ZedGenerator


def test_is_refusal_detection() -> None:
    # True positives: Refusal phrases
    assert _is_refusal("I do not have that official record yet.") is True
    assert _is_refusal("I don't have information about this topic.") is True
    assert _is_refusal("There is no official record of this in my database.") is True
    assert _is_refusal("The provided context does not contain any details.") is True
    assert _is_refusal("I cannot find any information regarding this query.") is True
    assert _is_refusal(None) is True
    assert _is_refusal("") is True

    # True negatives: Valid answers that mention official procedures
    valid_answer = (
        "Step 1: Visit the nearest National Registration Office in your district.\n"
        "- Bring your birth certificate or affidavit.\n"
        "- Bring a parent or chief's letter to verify identity."
    )
    assert _is_refusal(valid_answer) is False


def test_generator_refusal_retry_succeeds() -> None:
    gen = ZedGenerator.__new__(ZedGenerator)
    gen.system_prompt = "system prompt"
    gen.provider = "auto"
    gen.gemini_llm = None
    gen.ollama_llm = None
    gen.openai_llm = None

    context = "To replace a lost NRC in Zambia, obtain a police report and present your birth record."
    query = "Kufunika chiyani kuti munthu apeze NRC ina ngati wataya?"

    call_count = 0
    def mock_cascade(q, ctx, ctry, prompt_override=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return "I do not have that official record in my database yet."
        return "Step 1: Obtain a police report.\nStep 2: Visit the NRC office."

    with patch.object(gen, "_generate_with_cascade", side_effect=mock_cascade):
        result = gen.generate(query, context, "zm", "ny")
        assert call_count == 2
        assert "Step 1: Obtain a police report" in result


def test_generator_refusal_retry_falls_back_to_excerpt() -> None:
    gen = ZedGenerator.__new__(ZedGenerator)
    gen.system_prompt = "system prompt"
    gen.provider = "auto"
    gen.gemini_llm = None
    gen.ollama_llm = None
    gen.openai_llm = None

    context = "Section 4: National Registration Cards must be replaced within 30 days of loss at any district office."
    query = "Kodi nikataya NRC ndichite bwanji?"

    with patch.object(gen, "_generate_with_cascade", return_value="I don't have that official record in my database."):
        result = gen.generate(query, context, "zm", "ny")
        assert result.startswith("According to official public records:\n\n")
        assert "National Registration Cards must be replaced" in result


def test_pipeline_grounded_excerpt_preserves_english_for_nyanja() -> None:
    mock_doc = Document(
        page_content="Official statutory requirements for NRC replacement.",
        metadata={"source": "data/raw/zm/government/nrc_passport_guide.txt"}
    )
    raw_excerpt = "According to official public records:\n\nOfficial statutory requirements for NRC replacement."

    with patch("src.rag.retriever.ZedRetriever.get_relevant_context", return_value=[mock_doc]), \
         patch("src.rag.generator.ZedGenerator.generate", return_value=raw_excerpt), \
         patch("src.rag.pipeline.translate_text") as mock_translate, \
         patch("src.core.database.DatabaseManager.log_interaction"):
        answer, sources = generate_reply("Kufunika chiyani pa NRC?", "zm", "ny")
        # Translation must NOT be called for raw excerpt fallback
        mock_translate.assert_not_called()
        assert answer.startswith("According to official public records:")


