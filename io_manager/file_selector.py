"""Abstract base class for choosing a CSV file from a list and loading it."""
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

class FileSelector(ABC):

    def __init__(self, empty_message: str, list_heading: str, prompt: str):
        self._empty_message = empty_message  # Shown when there are no files to choose from
        self._list_heading = list_heading    # Heading shown above the file list
        self._prompt = prompt                # Text shown when asking for a filename

    @property
    def empty_message(self) -> str:
        """Text to show when there are no files to choose from."""
        return self._empty_message

    @property
    def list_heading(self) -> str:
        """Heading to show above the list of files."""
        return self._list_heading

    @property
    def prompt(self) -> str:
        """Text to show when asking the user for a filename."""
        return self._prompt

    def get_files(self) -> list[str]:
        """Returns the names of the files the user can choose from."""
        return self._list_files()

    def select(self, filename: str) -> tuple[pd.DataFrame, Path]:
        """Validates and loads the file the user typed.

        Returns (df, path). Raises FileNotFoundError or ValueError with a
        user-friendly message if the file cannot be used.
        """
        return self._load(filename.strip())

    @abstractmethod
    def _list_files(self) -> list[str]:
        """Returns the names of the files the user can choose from."""

    @abstractmethod
    def _load(self, filename: str) -> tuple[pd.DataFrame, Path]:
        """Validates and loads the chosen file, returning (df, path)."""