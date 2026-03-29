from src.evaluation.metrics import simple_accuracy


def test_simple_accuracy_handles_zero_total() -> None:
    assert simple_accuracy(0, 0) == 0.0
