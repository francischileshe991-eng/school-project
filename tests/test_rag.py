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


def test_generate_reply_returns_answer_and_sources() -> None:
    answer, sources = generate_reply("How do I apply for a passport?", "zm", "en")
    assert isinstance(answer, str)
    assert isinstance(sources, list)
    assert all(isinstance(source, str) for source in sources)

