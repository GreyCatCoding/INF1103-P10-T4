"""Manages moderation reports by coordinating storage, table building, summaries, and queries."""
from pathlib import Path
import pandas as pd

from data_manager.reportquery import ReportQuery
from data_manager.reportstore import ReportStore
from data_manager.reportsummary import ReportSummary
from data_manager.reporttablebuilder import ReportTableBuilder


class DataManager:
    """Coordinates reporting operations by delegating to specialized store, build, summary, and query components."""

    def __init__(self, store: ReportStore) -> None:
        """Initializes DataManager with a ReportStore (aggregation) and composes its internal helper components."""
        self.__store = store
        self.__table_builder = ReportTableBuilder()
        self.__summary = ReportSummary()
        self.__query = ReportQuery()

    def build_table(self, reports: list[dict]) -> pd.DataFrame:
        """Turns raw report dictionaries into a standardized DataFrame."""
        return self.__table_builder.build(reports)

    def save_report(self, df: pd.DataFrame, name: str | Path) -> None:
        """Saves a report DataFrame through the configured store."""
        self.__store.save(df, name)

    def list_reports(self) -> list[str]:
        """Lists all saved report names from the store."""
        return self.__store.list_reports()

    def load_report(self, name: str | Path) -> pd.DataFrame:
        """Loads a named report DataFrame from the store."""
        return self.__store.load(name)

    def get_summary(self, df: pd.DataFrame) -> dict:
        """Calculates summary statistics and counts for a report table."""
        return self.__summary.calculate(df)

    def filter_reports(self, df: pd.DataFrame, category: str | None = None, action: str | None = None) -> pd.DataFrame:
        """Filters a report table by category and/or priority action."""
        return self.__query.filter(df, category=category, action=action)
    
    # === UPDATE & DELETE METHODS ===
    def update_record(self, report_name: str, user_id: str, updated_data: dict) -> None:
        """Delegates row updates to the configured report store."""
        self.__store.update_row(report_name, user_id, updated_data)

    def delete_record(self, report_name: str, user_id: str) -> None:
        """Delegates row deletion to the configured report store."""
        self.__store.delete_row(report_name, user_id)