from pathlib import Path
import pandas as pd
from file_selector import FileSelector


class CleanedFileSelector(FileSelector):
    """Handles listing and loading of pre-existing cleaned CSV files 
    via the data manager source."""

    def __init__(self, data_source):
        super().__init__(
            empty_message="No cleaned CSV files found in the 'cleaned' directory.",
            list_heading="Available cleaned CSV files:",
            prompt="Enter cleaned CSV filename (or type 'back' to return): "
        )
        self.__data_source = data_source

    def _list_files(self) -> list[str]:
        return self.__data_source.get_available_cleaned_files()

    def _load(self, filename: str) -> tuple[pd.DataFrame, Path] | None:
        try:
            cleaned_df, cleaned_path = self.__data_source.load_cleaned_file(filename)
            print(f"\nLoading {cleaned_path.name}...")
            return cleaned_df, cleaned_path
        except (FileNotFoundError, ValueError, pd.errors.EmptyDataError) as e:
            print(f"\n[Error] {e}")
            print("Please select a valid, non-empty cleaned CSV file.\n")
            return None
