"""Turns moderation report dictionaries into a table with fixed columns."""
import pandas as pd


class ReportTableBuilder:
    """Builds the standard report table used for saving and display."""

    __DISPLAY_COLUMNS = ["User ID", "username", "comment", "category", "category_description", "priority", "recommended_action", "ai_reason"]

    def build(self, reports: list[dict]) -> pd.DataFrame:
        """Returns reports as a DataFrame with the standard columns, with blank cells as ""."""
        df = pd.DataFrame(reports)
        df = df.reindex(columns=self.__DISPLAY_COLUMNS)
        return df.fillna("")
