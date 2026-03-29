#!/usr/bin/env python3
"""
Tokenizer component for multilingual support and context management.
"""

from typing import List
import tiktoken
from src.core.logger import logger
from src.configs.settings import settings

class ZedTokenizer:
    """Handles tokenization and token counting for different models."""

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        try:
            self.encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            logger.warning(f"Model {model_name} not found in tiktoken. Falling back to cl100k_base.")
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Returns the number of tokens in a string."""
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def get_tokens(self, text: str) -> List[int]:
        """Encodes text into a list of token IDs."""
        if not text:
            return []
        return self.encoding.encode(text)

    def decode_tokens(self, tokens: List[int]) -> str:
        """Decodes a list of token IDs back into a string."""
        if not tokens:
            return ""
        return self.encoding.decode(tokens)

    def truncate_text(self, text: str, max_tokens: int) -> str:
        """Truncates text to a maximum number of tokens."""
        tokens = self.get_tokens(text)
        if len(tokens) <= max_tokens:
            return text
        return self.decode_tokens(tokens[:max_tokens])

    def split_by_tokens(self, text: str, chunk_size: int) -> List[str]:
        """Splits text into chunks based on token count."""
        tokens = self.get_tokens(text)
        chunks = []
        for i in range(0, len(tokens), chunk_size):
            chunks.append(self.decode_tokens(tokens[i:i + chunk_size]))
        return chunks

# Global instance for easy access
zed_tokenizer = ZedTokenizer()

def count_tokens(text: str) -> int:
    """Functional wrapper for counting tokens."""
    return zed_tokenizer.count_tokens(text)
