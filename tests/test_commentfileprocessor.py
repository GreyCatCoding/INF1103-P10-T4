"""Tests for CommentFileProcessor: reading a raw CSV, cleaning it and saving the results.

"""
import json

import pandas as pd
import pytest

from io_manager.commentfileprocessor import CommentFileProcessor


@pytest.fixture
def raw_csv(tmp_path):
    """Creates a small raw comments CSV and returns its path."""
    csv_path = tmp_path / "comments.csv"

    raw_data = pd.DataFrame({
        "User ID": [1, 2, 3],
        "username": ["amy", "ben", "cal"],
        "comments": ["u r LATE", "Check www.spam.com", None],  # None makes an empty cell
        "timestamp": ["2026-11-01 10:00", "2026-11-01 10:05", "2026-11-01 10:10"],
        "country": ["SG", "MY", "TH"],  # Extra column that should not be kept
    })
    raw_data.to_csv(csv_path, index=False)

    return csv_path


@pytest.fixture
def processor(tmp_path):
    """Creates a processor that saves its files in a temporary folder."""
    return CommentFileProcessor(output_dir=tmp_path / "cleaned")


# ---------- Cleaning the comments ----------

def test_cleans_every_comment(processor, raw_csv):
    # process() returns three values, so we unpack them into three variables
    cleaned_df, csv_path, json_path = processor.process(raw_csv)

    # Row 3 was empty in the CSV, so its cleaned comment is ""
    expected_comments = ["you are late", "check", ""]
    assert cleaned_df["processed_comments"].tolist() == expected_comments


def test_keeps_the_original_comments(processor, raw_csv):
    cleaned_df, csv_path, json_path = processor.process(raw_csv)

    # The AI uses the cleaned text, but the original text is kept for reference
    expected_comments = ["u r LATE", "Check www.spam.com", ""]
    assert cleaned_df["original_comments"].tolist() == expected_comments


# ---------- Choosing the columns ----------

def test_keeps_only_the_cleaned_csv_columns(processor, raw_csv):
    cleaned_df, csv_path, json_path = processor.process(raw_csv)

    # "comments" and "country" are gone, and the columns are in this exact order
    expected_columns = ["User ID", "username", "original_comments", "processed_comments", "timestamp"]
    assert list(cleaned_df.columns) == expected_columns


def test_skips_optional_columns_that_are_missing(processor, tmp_path):
    # This CSV has no "User ID" or "timestamp" column
    small_csv = tmp_path / "small.csv"
    pd.DataFrame({"username": ["amy"], "comments": ["hello"]}).to_csv(small_csv, index=False)

    cleaned_df, csv_path, json_path = processor.process(small_csv)

    # __keep_columns only keeps columns that exist, so this should not crash
    assert list(cleaned_df.columns) == ["username", "original_comments", "processed_comments"]


# ---------- Saving the files ----------

def test_saves_csv_and_json_with_default_names(processor, raw_csv):
    cleaned_df, csv_path, json_path = processor.process(raw_csv)

    # The names come from the input file: comments.csv -> comments_cleaned.csv
    assert csv_path.name == "comments_cleaned.csv"
    assert json_path.name == "comments_cleaned.json"

    # .exists() checks that the files were really created on disk
    assert csv_path.exists()
    assert json_path.exists()


def test_can_choose_the_output_path(processor, raw_csv, tmp_path):
    chosen_path = tmp_path / "my_results.csv"

    cleaned_df, csv_path, json_path = processor.process(raw_csv, output_path=chosen_path)

    # The JSON file uses the same name as the CSV file
    assert csv_path == chosen_path
    assert json_path == tmp_path / "my_results.json"


def test_saved_csv_contains_the_cleaned_comments(processor, raw_csv):
    cleaned_df, csv_path, json_path = processor.process(raw_csv)

    # Open the saved file to check what was written to disk
    saved_df = pd.read_csv(csv_path)

    assert saved_df["processed_comments"][0] == "you are late"


def test_saved_json_contains_only_three_fields(processor, raw_csv):
    cleaned_df, csv_path, json_path = processor.process(raw_csv)

    # The JSON file becomes a list with one dictionary per row
    records = json.loads(json_path.read_text())

    assert list(records[0].keys()) == ["User ID", "username", "processed_comments"]
    assert records[0]["processed_comments"] == "you are late"


# ---------- Invalid input ----------

def test_missing_comments_column_raises_value_error(processor, tmp_path):
    bad_csv = tmp_path / "bad.csv"
    pd.DataFrame({"username": ["amy"]}).to_csv(bad_csv, index=False)

    # This test passes only if the indented line raises a ValueError
    with pytest.raises(ValueError):
        processor.process(bad_csv)
