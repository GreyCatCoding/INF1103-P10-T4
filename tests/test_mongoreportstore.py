"""Tests for MongoReportStore.

this test file creates a separate 'moderation_test' database,
the actual app's own database is never touched.

Each test empties the test collection when it STARTS, so the documents from
the last test stay behind. You can view them in the VS Code MongoDB extension
under moderation_test > reports.

If MongoDB is not running, the tests are skipped instead of failing.
"""
import os
from pathlib import Path

import pandas as pd
import pytest
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from data_manager.mongoreportstore import MongoReportStore
from data_manager.reportstore import ReportStore

load_dotenv()  

MONGO_URI = os.getenv("MONGO_URI")
TEST_DB_NAME = "moderation_test"  # Never use the database for the actual application


# =============================================================
# FIXTURES (shared setup that pytest passes into each test)
# =============================================================
@pytest.fixture
def collection():
    """An empty 'reports' collection in the test database."""
    # Give up after 2 seconds if MongoDB is not running
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    try:
        client.admin.command("ping")
    except PyMongoError:
        pytest.skip("MongoDB is not running, so the MongoDB tests were skipped")

    reports_collection = client[TEST_DB_NAME]["reports"]
    reports_collection.delete_many({})  # Start every test with no documents

    yield reports_collection  # The test runs here

    client.close()


@pytest.fixture
def store(collection):
    """Assume a variable 'store' that uses the collection"""
    return MongoReportStore(collection)


@pytest.fixture
def report_df():
    """Checks if the report DataFrame has the expected structure."""
    return pd.DataFrame({
        "User ID": [0, 9, 1],
        "username": ["amy", "glenn", "jame"],
        "comment": [
            "yo ja rule is more succesful then you ll ever be",
            "please visit for more info",
            "the title is fine as it is in my opinion",
        ],
        "category": ["harassment", "spam", "none"],
        "category_description": [
            "Insults, threats or mockery aimed at a specific person",
            "Scams, get-rich-quick offers or unsolicited promotion",
            "No harmful content detected",
        ],
        "priority": ["P3", "P3", "P4"],
        "recommended_action": [
            "Warn user and/or prompt human review",
            "Warn user and/or prompt human review",
            "Monitor user",
        ],
        "ai_reason": [
            "Direct insult aimed at a specific individual",
            "Generic promotional request to visit for more info, typical of spam.",
            "Neutral statement expressing an opinion",
        ],
    })


# =============================================================
# INTERFACE
# =============================================================
def test_mongo_store_is_a_report_store(store):
    """MongoReportStore can be used anywhere a ReportStore is expected."""
    assert isinstance(store, ReportStore)


# =============================================================
# CREATE: save()
# =============================================================
def test_save_creates_one_document_per_row(store, collection, report_df):
    """Each row of the report becomes one MongoDB document."""
    store.save(report_df, "sample.csv")

    # 3 rows in the table, so 3 documents with this report_name
    assert collection.count_documents({"report_name": "sample.csv"}) == 3

    # Look at one document exactly as MongoDB stores it
    glenn = collection.find_one({"username": "glenn"})
    assert glenn["comment"] == "please visit for more info"
    assert glenn["report_name"] == "sample.csv"  # Added by save()
    assert "_id" in glenn                         # Added by MongoDB


def test_save_keeps_only_the_filename(store, collection, report_df):
    """The pipeline passes a full path, but only the filename is stored."""
    full_path = Path("C:/project/cleaned/sample_uncleaned_cleaned.csv")

    store.save(report_df, full_path)

    assert collection.count_documents({"report_name": "sample_uncleaned_cleaned.csv"}) == 3


def test_save_adds_csv_to_the_name(store, collection, report_df):
    """'sample' and 'sample.csv' are treated as the same report."""
    store.save(report_df, "sample")

    assert collection.count_documents({"report_name": "sample.csv"}) == 3


def test_saving_twice_replaces_the_report(store, collection, report_df):
    """Saving under the same name replaces the old rows instead of adding more."""
    store.save(report_df, "sample.csv")
    store.save(report_df, "sample.csv")

    # Still 3, not 6, because save() deletes the old rows first
    assert collection.count_documents({"report_name": "sample.csv"}) == 3


def test_save_leaves_other_reports_alone(store, collection, report_df):
    """Replacing one report must not delete another report's rows."""
    store.save(report_df, "first.csv")
    store.save(report_df.head(1), "second.csv")

    store.save(report_df.head(2), "second.csv")  # Replace only "second.csv"

    assert collection.count_documents({"report_name": "first.csv"}) == 3
    assert collection.count_documents({"report_name": "second.csv"}) == 2


def test_save_empty_table_stores_nothing(store, collection):
    """An empty table saves no documents and does not crash."""
    # pymongo raises an error for insert_many([]), so save() must skip it
    store.save(pd.DataFrame(), "empty.csv")

    assert collection.count_documents({"report_name": "empty.csv"}) == 0


# =============================================================
# READ: list_reports()
# =============================================================
def test_list_reports_gives_each_name_once_sorted(store, report_df):
    """Each report name appears once, in alphabetical order."""
    # Saved out of order, to prove the list gets sorted
    store.save(report_df, "b.csv")
    store.save(report_df, "a.csv")

    # Each report has 3 documents, but each name is listed only once
    assert store.list_reports() == ["a.csv", "b.csv"]


def test_list_reports_when_nothing_saved(store):
    """An empty database gives an empty list."""
    assert store.list_reports() == []


# =============================================================
# READ: load()
# =============================================================
def test_load_returns_what_was_saved(store, report_df):
    """Loading gives back the same table that was saved."""
    store.save(report_df, "sample.csv")

    loaded_df = store.load("sample.csv")

    # Same columns, order and values: _id and report_name are not returned
    assert loaded_df.equals(report_df)


def test_load_keeps_the_saved_row_order(store, report_df):
    """Rows come back in the order they were saved (risk order), not sorted by User ID."""
    store.save(report_df, "sample.csv")

    loaded_df = store.load("sample.csv")

    assert loaded_df["User ID"].tolist() == [0, 9, 1]


def test_load_works_without_csv_in_the_name(store, report_df):
    """A user can type the report name with or without .csv."""
    store.save(report_df, "sample.csv")

    loaded_df = store.load("sample")

    assert len(loaded_df) == 3


def test_load_missing_report_raises(store):
    """A missing report raises FileNotFoundError, just like CsvReportStore."""
    with pytest.raises(FileNotFoundError):
        store.load("missing.csv")
