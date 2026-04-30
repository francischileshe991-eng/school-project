import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag.pipeline import generate_reply

def test():
    query = "Ndani angakhale membala wa NHIMA?"
    country = "zm"
    # language=None to trigger detection
    
    print(f"Asking: {query}")
    answer, sources = generate_reply(query, country)
    print(f"\nBOT: {answer}")
    print(f"Sources: {sources}")

if __name__ == "__main__":
    test()
