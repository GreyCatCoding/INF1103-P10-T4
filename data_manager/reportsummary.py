"""Calculates summary statistics for a table of moderation reports."""
import pandas as pd


class ReportSummary:
    """Counts reports overall, by priority, by category and by human review need."""

    __HUMAN_REVIEW_PATTERN = r"human|review|moderator"

    def calculate(self, df: pd.DataFrame) -> dict:
        """Returns total_records, priority_counts, category_counts and human_review_count."""
        return {
            "total_records": len(df),
            "priority_counts": self.__get_counts(df, "priority"),
            "category_counts": self.__get_counts(df, "category"),
            "human_review_count": self.__count_human_reviews(df),
        }

    def __get_counts(self, df: pd.DataFrame, column: str) -> dict:
        """Returns how many times each value appears in the column, or {} if it is missing."""
        if column not in df.columns:
            return {}
        return df[column].value_counts().to_dict()

    def __count_human_reviews(self, df: pd.DataFrame) -> int:
        """Returns how many recommended actions mention a human review."""
        if "recommended_action" not in df.columns:
            return 0
        actions = df["recommended_action"].astype(str)
        matches = actions.str.contains(self.__HUMAN_REVIEW_PATTERN, case=False, regex=True)
        return int(matches.sum())
