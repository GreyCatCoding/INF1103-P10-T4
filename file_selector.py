from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

class FileSelector(ABC):
    """Abstract base class implementing the template method pattern 
    for listing, prompting, and loading CSV files safely."""

    def __init__(self, empty_message: str, list_heading: str, prompt: str):
        self._empty_message = empty_message
        self._list_heading = list_heading
        self._prompt = prompt

    def select(self) -> tuple[pd.DataFrame, Path] | None:
        """Template method that manages the interactive terminal selection loop."""
        while True:
            files = self._list_files()
            if not files:
                print(f"\n{self._empty_message}")
                return None

            print(f"\n{self._list_heading}")
            for file in files:
                print(f"- {file}")

            filename = input(f"\n{self._prompt}").strip()
            if filename.lower() == "back":
                return None

            try:
                result = self._load(filename)
                if result is not None:
                    return result
            except Exception as e:
                print(f"\n[Error] {e}")

    @abstractmethod
    def _list_files(self) -> list[str]:
        """Abstract method to retrieve available filenames."""
        pass

    @abstractmethod
    def _load(self, filename: str) -> tuple[pd.DataFrame, Path] | None:
        """Abstract method to load and validate a selected file."""
        pass