"""Tests for CsvReportStore. They use a temporary folder, so the real 'cleaned' folder is never touched."""
import pandas as pd
import pytest

from csvreportstore import CsvReportStore
from reportstore import ReportStore



@pytest.fixture
def store(tmp_path):
    # tmp_path is a temporary folder that pytest creates for each test
    # The 'cleaned' subfolder does not exist yet, so the store must create it when needed
    return CsvReportStore(tmp_path / "cleaned")


@pytest.fixture
def report_df():
    # A small sample table to save and load
    return pd.DataFrame({
        "username": ["amy", "ben"],
        "category": ["spam", "hate"],
        "priority": ["P3", "P1"],
    })


# =============================================================
# INTERFACE
# =============================================================
def test_csv_store_is_a_report_store(store):
    # Code written for the ReportStore interface must be able to use this class (Liskov Substitution)
    assert isinstance(store, ReportStore)


# =============================================================
# SAVING AND LOADING
# =============================================================
def test_save_then_load_returns_same_data(store, report_df):
    store.save(report_df, "report.csv")

    loaded_df = store.load("report.csv")

    # Nothing should be lost or changed by writing to a file and reading it back
    assert loaded_df.equals(report_df)


def test_load_adds_csv_extension(store, report_df):
    store.save(report_df, "report.csv")

    # A user may type the name without .csv, and it should still find the file
    loaded_df = store.load("report")

    assert len(loaded_df) == 2


def test_load_turns_blank_cells_into_empty_strings(store):
    # None is written to the CSV as a blank cell
    store.save(pd.DataFrame({"username": ["amy", None]}), "report.csv")

    loaded_df = store.load("report.csv")

    # pandas reads a blank cell as NaN, so load must replace it with ""
    assert loaded_df["username"].tolist() == ["amy", ""]


# =============================================================
# LISTING REPORTS
# =============================================================
def test_list_reports_is_sorted_and_only_csv(store, report_df, tmp_path):
    # Saved out of order, to prove the result gets sorted
    store.save(report_df, "b.csv")
    store.save(report_df, "a.csv")
    # A non-CSV file in the same folder must not appear in the list
    (tmp_path / "cleaned" / "notes.json").write_text("{}")

    assert store.list_reports() == ["a.csv", "b.csv"]


def test_list_reports_on_missing_folder_is_empty(store):
    # Nothing has been saved, so the folder does not exist yet; this should not crash
    assert store.list_reports() == []


# =============================================================
# SAVE FAILURES AND SAFETY
# =============================================================
def test_save_stays_inside_the_folder(store, report_df, tmp_path):
    # "../" would normally mean the parent folder
    store.save(report_df, "../outside.csv")

    # The store drops the "../", so the file stays inside its own folder
    assert (tmp_path / "cleaned" / "outside.csv").exists()
    assert not (tmp_path / "outside.csv").exists()


def test_save_to_locked_file_raises_permission_error(store, report_df, monkeypatch):
    # Pretends the file is open in another program, such as Excel, which is hard to set up for real
    def fail_to_save(self, *args, **kwargs):
        raise PermissionError

    # monkeypatch swaps to_csv for the fake above, for this test only
    monkeypatch.setattr(pd.DataFrame, "to_csv", fail_to_save)

    # The store logs the error and re-raises it, so the IO Manager can tell the user
    with pytest.raises(PermissionError):
        store.save(report_df, "report.csv")


# =============================================================
# LOAD FAILURES
# =============================================================
# The IO Manager catches these errors and asks the user to choose another file,
# so each bad file must raise an error instead of returning bad data.
def test_load_missing_file_raises(store):
    # pytest.raises passes only if the code inside raises this error
    with pytest.raises(FileNotFoundError):
        store.load("missing.csv")


def test_load_empty_file_raises(store, tmp_path):
    folder = tmp_path / "cleaned"
    folder.mkdir()
    # Creates a 0-byte file, which __validate rejects
    (folder / "empty.csv").write_text("")

    with pytest.raises(ValueError):
        store.load("empty.csv")


def test_load_corrupt_file_raises(store, tmp_path):
    folder = tmp_path / "cleaned"
    folder.mkdir()
    # The header has 2 columns but the last row has 4, so pandas cannot read it
    (folder / "corrupt.csv").write_text('a,b\n1,2\n3,4,5,6\n')

    # pandas raises ParserError here, which is a type of ValueError
    with pytest.raises(ValueError):
        store.load("corrupt.csv")
