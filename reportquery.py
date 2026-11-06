"""Filters a table of moderation reports by category and priority."""
import pandas as pd


class ReportQuery:
    """Finds the reports that match the filters a user asked for."""

    def filter(self, df: pd.DataFrame, category: str | None = None, action: str | None = None) -> pd.DataFrame:
        """Returns the rows that match every filter given; a filter left as None is skipped.

        Matching ignores upper and lower case. action is matched against the priority column.
        """
        # A file that never finished moderation has no category/priority columns; return no matches instead of crashing
        if "category" not in df.columns or "priority" not in df.columns:
            return df.iloc[0:0]

        filtered_df = df.copy()

        if category:
            # Stored categories use underscores, so "self harm" must become "self_harm"
            wanted_category = category.strip().lower().replace(" ", "_")
            filtered_df = self.__filter_by(filtered_df, "category", wanted_category)

        if action:
            wanted_priority = action.strip().lower()
            filtered_df = self.__filter_by(filtered_df, "priority", wanted_priority)

        return filtered_df

    def __filter_by(self, df: pd.DataFrame, column: str, value: str) -> pd.DataFrame:
        """Returns the rows whose lowercased column value equals value."""
        column_values = df[column].astype(str).str.lower()
        return df[column_values == value]
