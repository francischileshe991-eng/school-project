#!/usr/bin/env python3
"""
Evaluation metrics module for Zedchatbot.
Implements quantitative metrics for Information Retrieval and RAG generation quality:
- Retrieval Hit Rate (Recall@K)
- Retrieval Precision
- Answer Keyword Grounding / Recall
- Response Latency
- Cross-Domain & Multilingual Performance Aggregation
"""

from typing import Any, Dict, List, Optional


def simple_accuracy(correct: int, total: int) -> float:
    """Legacy accuracy function."""
    if total <= 0:
        return 0.0
    return correct / total


def retrieval_hit_rate(
    retrieved_sources: List[str], expected_sources: List[str]
) -> float:
    """
    Returns 1.0 if at least one expected source is present in retrieved sources, else 0.0.
    """
    if not expected_sources:
        return 1.0
    if not retrieved_sources:
        return 0.0

    retrieved_lower = [s.lower() for s in retrieved_sources]
    for exp in expected_sources:
        exp_lower = exp.lower()
        if any(exp_lower in r for r in retrieved_lower):
            return 1.0
    return 0.0


def retrieval_precision(
    retrieved_sources: List[str], expected_sources: List[str]
) -> float:
    """
    Calculates precision: fraction of retrieved documents that are relevant.
    """
    if not retrieved_sources:
        return 0.0
    if not expected_sources:
        return 1.0

    hits = 0
    for r in retrieved_sources:
        r_lower = r.lower()
        if any(exp.lower() in r_lower for exp in expected_sources):
            hits += 1
    return hits / len(retrieved_sources)


def answer_keyword_recall(
    response_text: str, expected_keywords: List[str]
) -> float:
    """
    Checks what fraction of expected key factual terms appear in the generated answer.
    """
    if not expected_keywords:
        return 1.0
    if not response_text:
        return 0.0

    resp_lower = response_text.lower()
    matches = sum(1 for kw in expected_keywords if kw.lower() in resp_lower)
    return matches / len(expected_keywords)


def compute_evaluation_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes aggregated performance metrics overall, by country, by domain, and by language.
    """
    if not results:
        return {"total_evaluated": 0}

    total = len(results)
    avg_hit_rate = sum(r.get("hit_rate", 0.0) for r in results) / total
    avg_precision = sum(r.get("precision", 0.0) for r in results) / total
    avg_keyword_recall = sum(r.get("keyword_recall", 0.0) for r in results) / total
    avg_latency = sum(r.get("latency_ms", 0) for r in results) / total

    # Grouping helpers
    def group_metrics(key: str) -> Dict[str, Dict[str, float]]:
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in results:
            val = r.get(key, "unknown")
            groups.setdefault(val, []).append(r)

        summary = {}
        for val, items in groups.items():
            n = len(items)
            summary[val] = {
                "count": n,
                "hit_rate": round(sum(x.get("hit_rate", 0.0) for x in items) / n, 4),
                "precision": round(sum(x.get("precision", 0.0) for x in items) / n, 4),
                "keyword_recall": round(
                    sum(x.get("keyword_recall", 0.0) for x in items) / n, 4
                ),
                "avg_latency_ms": round(
                    sum(x.get("latency_ms", 0) for x in items) / n, 2
                ),
            }
        return summary

    return {
        "total_evaluated": total,
        "overall": {
            "hit_rate": round(avg_hit_rate, 4),
            "precision": round(avg_precision, 4),
            "keyword_recall": round(avg_keyword_recall, 4),
            "avg_latency_ms": round(avg_latency, 2),
        },
        "by_country": group_metrics("country"),
        "by_domain": group_metrics("domain"),
        "by_language": group_metrics("language"),
    }
