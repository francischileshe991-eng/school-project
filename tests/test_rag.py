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

