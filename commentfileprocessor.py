"""Cleans a raw comments CSV and saves the result as a cleaned CSV and JSON."""
from pathlib import Path

import pandas as pd
from textcleaner import TextCleaner

BASE_DIR = Path(__file__).resolve().parent
CLEANED_DIR = BASE_DIR / "cleaned"  # Default folder for cleaned CSV and JSON files

# Csv columns for cleaned output save
CLEANED_CSV_COLUMNS = ["User ID", "username", "original_comments", "processed_comments", "timestamp"]
# Json columns for cleaned output and save
CLEANED_JSON_COLUMNS = ["User ID", "username", "processed_comments"]


class CommentFileProcessor:
    """Reads a raw comments CSV, cleans every comment and saves CSV and JSON copies."""

    def __init__(self, output_dir: Path = CLEANED_DIR):



        self.__output_dir = Path(output_dir)
        self.__cleaner = TextCleaner() 

    def __keep_columns(self, df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
            """Returns only the listed columns that exist in df, in the listed order."""
            present_columns = []
            for column in columns:
                if column in df.columns:
                    present_columns.append(column)
            return df[present_columns]