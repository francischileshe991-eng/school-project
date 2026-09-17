import pytest
from src.evaluation.metrics import (
    simple_accuracy,
    retrieval_hit_rate,
    retrieval_precision,
    answer_keyword_recall,
    compute_evaluation_summary,
)


def test_simple_accuracy() -> None:
    assert simple_accuracy(0, 0) == 0.0
    assert simple_accuracy(8, 10) == 0.8


def test_retrieval_hit_rate() -> None:
    expected = ["zesco_tariffs_2024.txt"]
    retrieved = ["data/raw/zm/utilities/zesco_tariffs_2024.txt", "data/raw/zm/general_info.txt"]
    assert retrieval_hit_rate(retrieved, expected) == 1.0

    retrieved_miss = ["data/raw/zm/general_info.txt"]
    assert retrieval_hit_rate(retrieved_miss, expected) == 0.0


def test_retrieval_precision() -> None:
    expected = ["zesco_tariffs_2024.txt"]
    retrieved = ["data/raw/zm/utilities/zesco_tariffs_2024.txt", "data/raw/zm/general_info.txt"]
    # 1 out of 2 is relevant
    assert retrieval_precision(retrieved, expected) == 0.5


def test_answer_keyword_recall() -> None:
    response = "The ZESCO lifeline tariff is K0.35 per kWh for consumption up to 100 units."
    keywords = ["0.35", "lifeline", "zesco"]
    assert answer_keyword_recall(response, keywords) == 1.0

    partial_keywords = ["0.35", "water"]
    assert answer_keyword_recall(response, partial_keywords) == 0.5


def test_compute_evaluation_summary() -> None:
    sample_results = [
        {
            "id": "Q1",
            "country": "zm",
            "domain": "utilities",
            "language": "en",
            "hit_rate": 1.0,
            "precision": 1.0,
            "keyword_recall": 1.0,
            "latency_ms": 200,
        },
        {
            "id": "Q2",
            "country": "zm",
            "domain": "health",
            "language": "ny",
            "hit_rate": 1.0,
            "precision": 0.5,
            "keyword_recall": 0.5,
            "latency_ms": 300,
        },
    ]
    summary = compute_evaluation_summary(sample_results)
    assert summary["total_evaluated"] == 2
    assert summary["overall"]["hit_rate"] == 1.0
    assert summary["overall"]["precision"] == 0.75
    assert summary["overall"]["keyword_recall"] == 0.75
    assert summary["overall"]["avg_latency_ms"] == 250.0
