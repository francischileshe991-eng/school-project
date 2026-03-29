from pathlib import Path


def count_documents(raw_dir: Path) -> int:
    return sum(1 for path in raw_dir.rglob("*") if path.is_file())
