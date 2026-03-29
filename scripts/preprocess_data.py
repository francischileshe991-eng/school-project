#!/usr/bin/env python3
"""
Preprocessing script for raw data documents
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.logger import logger
from src.configs.settings import settings

try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
    from langchain_core.documents import Document
except ImportError:
    logger.error("Required LangChain libraries not found. Run 'pip install langchain-community pypdf docx2txt'")
    sys.exit(1)

def clean_text(text: str) -> str:
    """Basic text cleaning: remove multiple newlines and extra spaces."""
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    # Remove leading/trailing whitespace
    return text.strip()

def process_file(file_path: Path) -> Optional[str]:
    """Loads a file and returns its cleaned text content."""
    try:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif suffix == ".docx":
            loader = Docx2txtLoader(str(file_path))
        elif suffix == ".txt":
            loader = TextLoader(str(file_path), encoding='utf-8')
        else:
            logger.warning(f"Unsupported file type: {suffix} for {file_path}")
            return None

        docs = loader.load()
        full_text = "\n".join([doc.page_content for doc in docs])
        return clean_text(full_text)
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {e}")
        return None

def preprocess_country(country_code: str):
    """Preprocesses all raw documents for a given country."""
    raw_dir = Path("data/raw") / country_code.lower()
    processed_dir = Path("data/processed") / country_code.lower()
    
    if not raw_dir.exists():
        logger.warning(f"Raw directory not found: {raw_dir}")
        return

    processed_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Preprocessing documents for {country_code.upper()}...")

    processed_count = 0
    # Search recursively for files
    for file_path in raw_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".pdf", ".docx", ".txt"]:
            logger.info(f"Processing: {file_path.name}")
            cleaned_content = process_file(file_path)
            
            if cleaned_content:
                # Save as .txt in processed_dir
                # Use same relative path if needed, or just filename
                output_filename = file_path.stem + ".txt"
                output_path = processed_dir / output_filename
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(cleaned_content)
                processed_count += 1

    logger.info(f"Finished preprocessing {processed_count} files for {country_code.upper()}.")

def main():
    countries = settings.SUPPORTED_COUNTRIES
    logger.info(f"Starting preprocessing for countries: {countries}")
    
    for country in countries:
        preprocess_country(country)

if __name__ == "__main__":
    main()
