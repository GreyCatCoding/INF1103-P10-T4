"""Tests for ReportTableBuilder, which gives every report table the same fixed columns."""
from data_manager.reporttablebuilder import ReportTableBuilder


def test_build_uses_standard_columns_and_drops_extras():
    """A report with missing and extra fields still produces the standard table."""
    # 'unused_field' is not a standard column, and most standard columns are missing
    reports = [{"username": "amy", "priority": "P1", "unused_field": "x"}]

    df = ReportTableBuilder().build(reports)

    # Exact order matters: the extra field is gone and every standard column is present
    assert list(df.columns) == ["User ID", "username", "comment", "category", "category_description", "priority", "recommended_action", "ai_reason"]
    # Values that were supplied are kept
    assert df.loc[0, "username"] == "amy"
    # A missing field becomes "" rather than NaN, so it displays and saves as a blank cell
    assert df.loc[0, "comment"] == ""


def test_build_with_no_reports_gives_empty_table_with_columns():
    """No reports gives a table with no rows that still has its columns."""
    df = ReportTableBuilder().build([])

    assert df.empty
    # The columns must still exist, so code that reads them, such as ReportQuery, does not fail
    assert "priority" in df.columns
