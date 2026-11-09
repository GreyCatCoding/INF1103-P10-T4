"""The contract every report storage type must follow (CSV now, MongoDB later)."""
from abc import ABC, abstractmethod

import pandas as pd


class ReportStore(ABC):
    """Interface: anything that can list, load and save moderation reports."""

    @abstractmethod
    def list_reports(self) -> list[str]:
        """Returns the names of all saved reports, sorted alphabetically."""
        pass

    @abstractmethod
    def load(self, name: str) -> pd.DataFrame:
        """Returns the named report as a DataFrame.
        Raises FileNotFoundError if it does not exist, or ValueError if it is unreadable.
        """
        pass

    @abstractmethod
    def save(self, df: pd.DataFrame, name: str) -> None:
        """Saves df under the given name, replacing any report with that name."""
        pass
    
    @abstractmethod
    def update_row(self, report_name: str, row_id: str, updated_data: dict) -> None:
        """Updates a specific row within a specific report based on its unique User ID."""
        pass

    @abstractmethod
    def delete_row(self, report_name: str, row_id: str) -> None:
        """Deletes a specific row within a specific report based on its unique User ID."""
        pass
