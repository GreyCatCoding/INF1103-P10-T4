"""Abstract base class for choosing a CSV file from a list and loading it."""
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

class FileSelector(ABC):

    def __init__(self, empty_message: str, list_heading: str, prompt: str):
        self._empty_message = empty_message  # Shown when there are no files to choose from
        self._list_heading = list_heading    # Heading shown above the file list
        self._prompt = prompt                # Text shown when asking for a filename

    def select(self) -> tuple[pd.DataFrame, Path] | None:
        """Lists the files, asks the user to pick one and loads it.

        Returns (df, path) on success, or None if there are no files or the user types 'back'.
        Keeps asking until a valid file is chosen.
        """
        notice = ""  # Error text from the previous attempt, shown above the next prompt

        while True:
            files = self._list_files()
            if not files:
                input(f"\n{self._empty_message}\nPress Enter to return...")
                return None

            listing = "\n".join(f"- {file}" for file in files)
            answer = input(f"{notice}\n{self._list_heading}\n{listing}\n{self._prompt}").strip()

            if answer.lower() == "back":
                return None

            try:
                result = self._load(answer)
            except (FileNotFoundError, ValueError, pd.errors.EmptyDataError) as error:
                notice = f"\n[Error] {error}\nPlease select a valid CSV file.\n"
                continue

            if result is not None:
                return result

    @abstractmethod
    def _list_files(self) -> list[str]:
        """Returns the names of the files the user can choose from."""

    @abstractmethod
    def _load(self, filename: str) -> tuple[pd.DataFrame, Path] | None:
        """Validates and loads the chosen file.

        Returns (df, path). Raises FileNotFoundError or ValueError (with a user-friendly
        message) if the file cannot be used; select() shows that message and asks again.
        """