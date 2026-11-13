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
        
    def update_row(self, report_name: str, row_id: str, updated_data: dict) -> None:
        """Changes the given fields of the row with this User ID, then saves the report.

        Raises ValueError if no row has that User ID.
        """
        df = self.load(report_name)

        # True for the row whose User ID matches, False for every other row
        matching_rows = df["User ID"] == int(row_id)
        if not matching_rows.any():
            raise ValueError(f"No row found with User ID {row_id} in {report_name}")

        # Overwrite only the fields that were passed in, e.g. {"priority": "P1"}
        for column, new_value in updated_data.items():
            df.loc[matching_rows, column] = new_value

        self.save(df, report_name)

    def delete_row(self, report_name: str, row_id: str) -> None:
        """Removes the row with this User ID, then saves the report.

        Raises ValueError if no row has that User ID.
        """
        df = self.load(report_name)

        matching_rows = df["User ID"] == int(row_id)
        if not matching_rows.any():
            raise ValueError(f"No row found with User ID {row_id} in {report_name}")

        # Keep every row except the matching one (~ means "not")
        remaining_df = df[~matching_rows]
        self.save(remaining_df, report_name)

    def __path_for(self, name: str | Path) -> Path:
        """Returns the file's path, respecting absolute paths while forcing relative traversal attempts inside the folder."""
        path_obj = Path(name)
        
        # If it's an absolute path (e.g., from pytest's tmp_path), use it directly
        if path_obj.is_absolute():
            filename = path_obj.name
            if not filename.endswith(".csv"):
                filename += ".csv"
            return path_obj.parent / filename
            
        # Otherwise, sanitize relative paths (stripping '..' or other directories) 
        # so files always stay inside self.__folder as intended by test_save_stays_inside_the_folder
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