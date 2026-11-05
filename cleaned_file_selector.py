"""Selects and loads an existing cleaned CSV through the DataManager."""
from pathlib import Path
import pandas as pd
from data_manager import DataManager
from file_selector import FileSelector


class CleanedFileSelector(FileSelector):
    """Lets the user pick a cleaned CSV; listing and validation are delegated to DataManager."""

    def __init__(self, data_source: DataManager):
        super().__init__(
            empty_message="No cleaned CSV files found in the 'cleaned' directory.",
            list_heading="Available cleaned CSV files:",
            prompt="\nEnter cleaned CSV filename (or type 'back' to return): ",
        )
        self.__data_source = data_source

    def _list_files(self) -> list[str]:
        """Returns the names of the cleaned CSV files known to the DataManager."""
        return self.__data_source.get_available_cleaned_files()

    def _load(self, filename: str) -> tuple[pd.DataFrame, Path]:
        """Returns (cleaned_df, path).

        DataManager raises FileNotFoundError, ValueError or EmptyDataError for invalid
        files; select() catches those and asks the user again.
        """
        return self.__data_source.load_cleaned_file(filename)