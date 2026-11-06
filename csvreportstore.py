"""Stores moderation reports as CSV files in a folder."""
import logging
from pathlib import Path

import pandas as pd
from reportstore import ReportStore

BASE_DIR = Path(__file__).resolve().parent
CLEANED_DIR = BASE_DIR / "cleaned"  # Default folder for saved reports


class CsvReportStore(ReportStore):
    """Saves and loads reports as CSV files inside one folder."""

    def __init__(self, folder: Path = CLEANED_DIR):
        self.__folder = Path(folder)

    def list_reports(self) -> list[str]:
        """Returns the CSV filenames in the folder, sorted alphabetically."""
        self.__folder.mkdir(parents=True, exist_ok=True)
        filenames = []
        for path in self.__folder.glob("*.csv"):
            filenames.append(path.name)
        return sorted(filenames)

    