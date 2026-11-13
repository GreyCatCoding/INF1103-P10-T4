"""Tests for DataManager.

DataManager does no storing itself: it passes each job to a helper (the store,
the summary, the query). These tests check that it passes the job on correctly.
The stores themselves are tested in test_csvreportstore.py and test_mongoreportstore.py.
"""
import pandas as pd
import pytest

from data_manager.data_manager import DataManager
from data_manager.reportstore import ReportStore


class FakeStore(ReportStore):
    """A mock store that remembers every call instead of saving anything."""

    def __init__(self):
        self.calls = []                      # Each call is recorded here
        self.saved_names = ["sample.csv"]    # What list_reports() will return
        self.report_to_load = pd.DataFrame({"User ID": [1]})

    def list_reports(self):
        self.calls.append(("list_reports",))
        return self.saved_names

    def load(self, name):
        self.calls.append(("load", name))
        return self.report_to_load

    def save(self, df, name):
        self.calls.append(("save", df, name))

    def update_row(self, report_name, row_id, updated_data):
        self.calls.append(("update_row", report_name, row_id, updated_data))

    def delete_row(self, report_name, row_id):
        self.calls.append(("delete_row", report_name, row_id))


# =============================================================
# FIXTURES
# =============================================================
@pytest.fixture
def store():
    return FakeStore()


@pytest.fixture
def data_manager(store):
    return DataManager(store)


@pytest.fixture
def report_df():
    """A small moderated report with realistic values."""
    return pd.DataFrame({
        "User ID": [0, 9, 1],
        "username": ["amy", "glenn", "jame"],
        "category": ["harassment", "spam", "none"],
        "priority": ["P3", "P3", "P4"],
        "recommended_action": [
            "Warn user and/or prompt human review",
            "Warn user and/or prompt human review",
            "Monitor user",
        ],
    })


# =============================================================
# STORAGE: DataManager passes each job to the store
# =============================================================
def test_save_report_passes_the_table_and_name_to_the_store(data_manager, store, report_df):
    """save_report() hands the exact table and name to the store."""
    data_manager.save_report(report_df, "sample.csv")

    action, saved_df, saved_name = store.calls[0]
    assert action == "save"
    assert saved_df is report_df          # The very same table, not a copy
    assert saved_name == "sample.csv"


def test_load_report_returns_what_the_store_loaded(data_manager, store):
    """load_report() asks the store for the report and returns it unchanged."""
    loaded_df = data_manager.load_report("sample.csv")

    assert store.calls == [("load", "sample.csv")]
    assert loaded_df is store.report_to_load


def test_list_reports_returns_the_store_names(data_manager, store):
    """list_reports() gives back the names the store knows about."""
    assert data_manager.list_reports() == ["sample.csv"]


def test_update_record_passes_the_change_to_the_store(data_manager, store):
    """update_record() hands the report name, User ID and changes to the store."""
    data_manager.update_record("sample.csv", "9", {"priority": "P1"})

    assert store.calls == [("update_row", "sample.csv", "9", {"priority": "P1"})]


def test_delete_record_passes_the_row_to_the_store(data_manager, store):
    """delete_record() hands the report name and User ID to the store."""
    data_manager.delete_record("sample.csv", "9")

    assert store.calls == [("delete_row", "sample.csv", "9")]


# =============================================================
# SUMMARY AND FILTER: DataManager uses its helpers
# =============================================================
def test_get_summary_counts_the_report(data_manager, report_df):
    """get_summary() returns the totals for the table."""
    summary = data_manager.get_summary(report_df)

    assert summary["total_records"] == 3
    assert summary["priority_counts"] == {"P3": 2, "P4": 1}
    assert summary["human_review_count"] == 2


def test_filter_reports_keeps_only_matching_rows(data_manager, report_df):
    """filter_reports() returns only the rows in the chosen category."""
    results = data_manager.filter_reports(report_df, category="spam")

    assert results["username"].tolist() == ["glenn"]
