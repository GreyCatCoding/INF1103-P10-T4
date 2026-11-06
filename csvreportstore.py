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

    def load(self, name: str | Path) -> pd.DataFrame:
        """Returns the named CSV as a DataFrame, with blank cells as "".

        Raises FileNotFoundError if the file is missing, or ValueError if it is
        empty or corrupt (pandas' read errors are also ValueErrors).
        """
        file_path = self.__path_for(name)
        self.__validate(file_path)
        df = pd.read_csv(file_path)
        return df.fillna("")

    def save(self, df: pd.DataFrame, name: str | Path) -> None:
        """Writes df to the named CSV, replacing any existing file."""
        file_path = self.__path_for(name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            df.to_csv(file_path, index=False)
        except PermissionError:
            logging.error("Permission denied: '%s' is currently open in another program (e.g., Excel).", file_path.name)
            raise

    def __path_for(self, name: str | Path) -> Path:
        """Returns the file's path, respecting absolute paths or falling back to the default folder."""
        path_obj = Path(name)
        
        # If an absolute path (or explicit path with directories like tmp_path) is passed, use it directly
        if path_obj.is_absolute() or path_obj.parent != Path('.'):
            filename = path_obj.name
            if not filename.endswith(".csv"):
                filename += ".csv"
            return path_obj.parent / filename
            
        # Otherwise, treat it as a standard filename inside self.__folder
        filename = path_obj.name
        if not filename.endswith(".csv"):
            filename += ".csv"
        return self.__folder / filename

    def __validate(self, file_path: Path) -> None:
        """Raises an error if the file is missing or has no content."""
        if not file_path.exists():
            raise FileNotFoundError(f"File '{file_path.name}' does not exist.")
        if file_path.stat().st_size == 0:
            raise ValueError(f"The file '{file_path.name}' is empty (0 bytes).")