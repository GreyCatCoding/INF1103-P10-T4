from pathlib import Path
import pandas as pd
from file_selector import FileSelector


class UncleanedFileSelector(FileSelector):
    """Handles discovery, case-insensitive lookup, column validation, 
    and loading of raw uncleaned CSV files."""

    def __init__(self, directory: Path):
        super().__init__(
            empty_message="No CSV files found in the 'uncleaned' directory.",
            list_heading="Available uncleaned CSV files:",
            prompt="Enter CSV filename (or type 'back' to return): "
        )
        self.__directory = Path(directory)

    def _list_files(self) -> list[str]:
        self.__directory.mkdir(exist_ok=True, parents=True)
        return sorted(p.name for p in self.__directory.glob("*.csv"))

    def __find_case_insensitive(self, filename: str) -> str | None:
        """Performs case-insensitive matching for user input filenames."""
        if not filename.endswith(".csv"):
            filename += ".csv"
        csv_files = self._list_files()
        file_map = {f.casefold(): f for f in csv_files}
        return file_map.get(filename.casefold())

    def _load(self, filename: str) -> tuple[pd.DataFrame, Path] | None:
        matched_filename = self.__find_case_insensitive(filename)
        if not matched_filename:
            print(f"\n[Error] '{filename}' not found in 'uncleaned/'. Please try again.")
            return None

        selected_path = self.__directory / matched_filename

        try:
            # Inline column check for raw CSVs (requires 'username' and 'comments')
            df_preview = pd.read_csv(selected_path, nrows=1)
            cols = list(df_preview.columns)

            has_username = "username" in cols
            has_comments = "comments" in cols

            if not has_username or not has_comments:
                missing = []
                if not has_username: missing.append("'username'")
                if not has_comments: missing.append("'comments'")
                print(f"\n[Error] '{matched_filename}' is missing required column(s): {', '.join(missing)}")
                print("Please select a valid CSV file.\n")
                return None

            # Load and return the full dataframe and path tuple
            df = pd.read_csv(selected_path)
            return df, selected_path

        except pd.errors.EmptyDataError:
            print(f"\n[Error] '{matched_filename}' is empty. Please select a valid CSV file.\n")
            return None
        except Exception as e:
            print(f"\n[Error] Failed to read '{matched_filename}': {e}\n")
            return None
