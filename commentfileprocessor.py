"""Cleans a raw comments CSV and saves the result as a cleaned CSV and JSON."""
from pathlib import Path

import pandas as pd
from textcleaner import TextCleaner

BASE_DIR = Path(__file__).resolve().parent

CLEANED_DIR = BASE_DIR / "cleaned"  # Default folder for cleaned CSV and JSON files

# Csv columns for cleaned output and saving
CLEANED_CSV_COLUMNS = ["User ID", "username", "original_comments", "processed_comments", "timestamp"]
# Json columns for cleaned output and saving
CLEANED_JSON_COLUMNS = ["User ID", "username", "processed_comments"]

class CommentFileProcessor:
    """Reads a raw comments CSV, cleans every comment and saves CSV and JSON copies."""

    def __init__(self, output_dir: Path = CLEANED_DIR):

        self.__output_dir = Path(output_dir)
        self.__cleaner = TextCleaner() # composition: this processor creates and owns its cleaner

    