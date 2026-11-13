"""Tests for IOManager's console menu.

"""
import pandas as pd
import pytest

from data_manager.data_manager import DataManager
from data_manager.reportstore import ReportStore
from io_manager.commentfileprocessor import CommentFileProcessor
from io_manager.io_manager import IOManager


class FakeStore(ReportStore):
    """A pretend store that keeps reports in a dictionary instead of files or MongoDB."""

    def __init__(self, saved_reports: dict):
        self.saved_reports = saved_reports   # report name -> DataFrame

    def list_reports(self):
        return sorted(self.saved_reports)

    def load(self, name):
        if name not in self.saved_reports:
            raise FileNotFoundError(f"Report '{name}' does not exist.")
        return self.saved_reports[name]

    def save(self, df, name):
        self.saved_reports[name] = df

    def update_row(self, report_name, row_id, updated_data):
        pass

    def delete_row(self, report_name, row_id):
        pass


def run_menu(monkeypatch, capsys, io_manager, answers, process_callback=None):
    """Runs the main menu with the given answers and returns everything shown on screen."""
    remaining_answers = iter(answers)

    def fake_input(prompt=""):
        print(prompt)   # Show the prompt, like the real input() does
        answer = next(remaining_answers, None)
        if answer is None:
            raise AssertionError("The menu asked for more input than the test gave")
        return answer

    monkeypatch.setattr("builtins.input", fake_input)
    io_manager.main_menu(process_callback=process_callback)
    return capsys.readouterr().out


# =============================================================
# FIXTURES
# =============================================================
@pytest.fixture
def report_df():
    """A small moderated report with realistic values."""
    return pd.DataFrame({
        "User ID": [0, 9],
        "username": ["amy", "glenn"],
        "comment": ["yo ja rule is more succesful then you ll ever be", "please visit for more info"],
        "category": ["harassment", "spam"],
        "priority": ["P3", "P3"],
        "recommended_action": ["Warn user and/or prompt human review", "Warn user and/or prompt human review"],
    })


@pytest.fixture
def uncleaned_dir(tmp_path, monkeypatch):
    """An empty temporary 'uncleaned' folder, used instead of the real one."""
    folder = tmp_path / "uncleaned"
    folder.mkdir()
    monkeypatch.setattr("io_manager.io_manager.UNCLEANED_DIR", folder)
    return folder


@pytest.fixture
def cleaned_dir(tmp_path, monkeypatch):
    """Makes the cleaning step save into a temporary folder, not the real 'cleaned' folder."""
    folder = tmp_path / "cleaned"
    monkeypatch.setattr(
        "io_manager.io_manager.CommentFileProcessor",
        lambda: CommentFileProcessor(output_dir=folder),
    )
    return folder


@pytest.fixture
def comments_csv(uncleaned_dir):
    """A valid raw comments file in the temporary 'uncleaned' folder."""
    path = uncleaned_dir / "comments.csv"
    pd.DataFrame({
        "User ID": [0, 1],
        "username": ["amy", "ben"],
        "comments": ["u r gr8 :)", "the title is fine as it is in my opinion"],
    }).to_csv(path, index=False)
    return path


def make_io_manager(saved_reports=None):
    """Builds an IOManager whose DataManager uses the fake store."""
    if saved_reports is None:
        saved_reports = {}
    return IOManager(DataManager(FakeStore(saved_reports)))


# =============================================================
# MAIN MENU
# =============================================================
def test_invalid_menu_choice_shows_an_error(monkeypatch, capsys):
    """An unknown choice prints an error, then the menu asks again."""
    output = run_menu(monkeypatch, capsys, make_io_manager(), ["7", "3"])

    assert "Invalid choice" in output


# =============================================================
# OPTION 1: cleanse a new file
# =============================================================
def test_cleanse_with_no_files_says_so(monkeypatch, capsys, uncleaned_dir):
    """With an empty 'uncleaned' folder, option 1 says so and returns to the menu."""
    # Option 1, press Enter, exit
    output = run_menu(monkeypatch, capsys, make_io_manager(), ["1", "", "3"])

    assert "No CSV files found" in output


def test_cleanse_unknown_filename_asks_again(monkeypatch, capsys, comments_csv):
    """A filename that is not in the folder shows an error, then asks again."""
    # Option 1, wrong name, go back, exit
    output = run_menu(monkeypatch, capsys, make_io_manager(), ["1", "missing.csv", "back", "3"])

    assert "'missing.csv' not found" in output


def test_cleanse_locked_file_shows_an_error(monkeypatch, capsys, comments_csv, cleaned_dir):
    """If the cleaned CSV is open in another program (e.g. Excel), the user is told."""
    def locked_file(self, input_file):
        raise PermissionError("file is open in Excel")

    monkeypatch.setattr(CommentFileProcessor, "process", locked_file)

    output = run_menu(monkeypatch, capsys, make_io_manager(), ["1", "comments.csv", "3"])

    assert "Could not access file" in output


def test_cleanse_runs_moderation_and_shows_the_results(monkeypatch, capsys, comments_csv, cleaned_dir, report_df):
    """A valid file is cleaned, passed to moderation, and the results are shown."""
    def fake_moderation(cleaned_df, csv_path, progress):
        return report_df   # Pretend the AI moderated the comments

    # Option 1, pick the file, leave the filter menu, exit
    output = run_menu(
        monkeypatch, capsys, make_io_manager(),
        ["1", "comments.csv", "2", "3"],
        process_callback=fake_moderation,
    )

    assert "Processing comments.csv" in output
    assert "MODERATION DATASET SUMMARY" in output
    assert "glenn" in output


def test_cleanse_results_that_cannot_be_saved_show_an_error(monkeypatch, capsys, comments_csv, cleaned_dir):
    """If saving the moderated report fails because the file is locked, the user is told."""
    def locked_save(cleaned_df, csv_path, progress):
        raise PermissionError("file is open in Excel")

    output = run_menu(
        monkeypatch, capsys, make_io_manager(),
        ["1", "comments.csv", "3"],
        process_callback=locked_save,
    )

    assert "Could not save results" in output


# =============================================================
# OPTION 2: display a saved report
# =============================================================
def test_display_with_no_saved_reports_says_so(monkeypatch, capsys):
    """With nothing saved, option 2 says so and returns to the menu."""
    output = run_menu(monkeypatch, capsys, make_io_manager(), ["2", "", "3"])

    assert "No cleaned CSV files found" in output


def test_display_unknown_report_asks_again(monkeypatch, capsys, report_df):
    """A report name that does not exist shows an error, then asks again."""
    io_manager = make_io_manager({"sample.csv": report_df})

    output = run_menu(monkeypatch, capsys, io_manager, ["2", "missing.csv", "back", "3"])

    assert "Report 'missing.csv' does not exist" in output


def test_display_shows_the_chosen_report(monkeypatch, capsys, report_df):
    """Picking a saved report shows its rows and summary."""
    io_manager = make_io_manager({"sample.csv": report_df})

    output = run_menu(monkeypatch, capsys, io_manager, ["2", "sample.csv", "2", "3"])

    assert "glenn" in output
    assert "Total Comments Analyzed : 2" in output


# =============================================================
# FILTER MENU (reached after a report is displayed)
# =============================================================
def test_filter_with_both_fields_blank_shows_an_error(monkeypatch, capsys, report_df):
    """Leaving category and priority both blank is rejected, then the user is asked again."""
    io_manager = make_io_manager({"sample.csv": report_df})

    # Display, pick, start filter, blank, blank, then category 'spam' with blank priority
    answers = ["2", "sample.csv", "1", "", "", "spam", "", "2", "3"]
    output = run_menu(monkeypatch, capsys, io_manager, answers)

    assert "You must provide either a Category or an Action" in output


def test_filter_with_no_matches_says_so(monkeypatch, capsys, report_df):
    """A filter that matches nothing says no records were found."""
    io_manager = make_io_manager({"sample.csv": report_df})

    # Filter for priority P1, which no row has
    answers = ["2", "sample.csv", "1", "", "P1", "2", "3"]
    output = run_menu(monkeypatch, capsys, io_manager, answers)

    assert "No matching records found." in output
