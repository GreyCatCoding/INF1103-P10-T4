"""Selects and loads a raw (uncleaned) comments CSV from the 'uncleaned' folder."""
from pathlib import Path
import pandas as pd
from file_selector import FileSelector

BASE_DIR = Path(__file__).resolve().parent
UNCLEANED_DIR = BASE_DIR / "uncleaned"  # Default folder for uncleaned CSV files

REQUIRED_COLUMNS = ["username", "comments"]


class UncleanedFileSelector(FileSelector):
    """Lets the user pick a raw CSV that has the required 'username' and 'comments' columns."""

    def __init__(self, directory: Path = UNCLEANED_DIR):
        super().__init__(
            empty_message="No CSV files found in the 'uncleaned' directory.",
            list_heading="Available uncleaned CSV files:",
            prompt="\nEnter CSV filename (or type 'back' to return): ",
        )
        self.__directory = Path(directory)

    def _list_files(self) -> list[str]:
        """Returns the sorted names of all CSV files in the uncleaned directory."""
        self.__directory.mkdir(exist_ok=True, parents=True)
        return sorted(path.name for path in self.__directory.glob("*.csv"))

    def _load(self, filename: str) -> tuple[pd.DataFrame, Path]:
        """Finds the file, checks its columns and returns (raw_df, path).

        Raises FileNotFoundError if the file is not in the folder and ValueError if it is
        empty, unreadable or missing a required column.
        """
        if not filename.endswith(".csv"):
            filename += ".csv"

        selected = self.__find_case_insensitive(filename)
        if selected is None:
            raise FileNotFoundError(f"'{filename}' not found in 'uncleaned/'.")

        selected_path = self.__directory / selected

        try:
            columns = list(pd.read_csv(selected_path, nrows=1).columns)
            missing = [f"'{column}'" for column in REQUIRED_COLUMNS if column not in columns]
            if missing:
                raise ValueError(f"'{selected}' is missing required column(s): {', '.join(missing)}")

            raw_df = pd.read_csv(selected_path)
        except pd.errors.EmptyDataError:
            raise ValueError(f"'{selected}' is empty.")
        except ValueError:
            raise
        except Exception as error:
            raise ValueError(f"Failed to read '{selected}': {error}")

        return raw_df, selected_path

    def __find_case_insensitive(self, filename: str) -> str | None:
        """Returns the real file name matching filename ignoring case, or None if there is none."""
        for existing in self._list_files():
            if existing.casefold() == filename.casefold():
                return existing
        return None