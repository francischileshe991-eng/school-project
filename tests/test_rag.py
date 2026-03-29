from src.rag.pipeline import generate_reply


def test_generate_reply_returns_answer_and_sources() -> None:
    answer, sources = generate_reply("How do I apply for a passport?", "zm", "en")
    assert isinstance(answer, str)
    assert isinstance(sources, list)
    assert all(isinstance(source, str) for source in sources)
