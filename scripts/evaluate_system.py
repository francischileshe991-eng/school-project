from src.evaluation.metrics import simple_accuracy


def main() -> None:
    example_score = simple_accuracy(correct=0, total=0)
    print(f"Starter accuracy value: {example_score}")
    print("System evaluation is not implemented yet.")


if __name__ == "__main__":
    main()
