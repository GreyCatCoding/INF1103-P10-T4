import pandas as pd

class ConsoleView:
    """Handles all terminal outputs, separating display responsibilities from business logic."""

    def print_table(self, df: pd.DataFrame, max_width: int = 36) -> None:
        """Prints a neatly formatted ASCII representation of a DataFrame."""
        if df.empty:
            print("No records to display.")
            return
            
        with pd.option_context("display.max_colwidth", max_width, "display.width", 1000):
            print(df.to_string(index=False))

    def print_detailed_records(self, df: pd.DataFrame) -> None:
        """Prints each record as a clean, structured detail card in the terminal."""
        if df.empty:
            print("No records found.")
            return

        separator = "=" * 80
        sub_separator = "-" * 80

        for idx, row in df.iterrows():
            print(separator)
            print(f"ID: {row.get('User ID', 'N/A')} | User: {row.get('username', 'N/A')} | Priority: {row.get('priority', 'N/A')} | Category: {row.get('category', 'N/A')}")
            print(sub_separator)
            print(f"Comment            : {row.get('comment', 'N/A')}")
            
            if "category_description" in row and row["category_description"]:
                print(f"Category Desc      : {row['category_description']}")
            if "recommended_action" in row and row["recommended_action"]:
                print(f"Recommended Action : {row['recommended_action']}")
            if "ai_reason" in row and row["ai_reason"]:
                print(f"AI Reason          : {row['ai_reason']}")
        print(separator)

    def print_summary(self, summary: dict) -> None:
        """Prints a formatted summary card of moderation statistics using a pre-calculated dictionary."""
        if summary.get("total_records", 0) == 0:
            print("\n--- Summary Statistics ---\nNo data available to summarize.")
            return

        separator = "=" * 55
        print("\n" + separator)
        print("           MODERATION DATASET SUMMARY")
        print(separator)
        print(f" Total Comments Analyzed : {summary['total_records']}")
        print(f" Pending Human Review    : {summary['human_review_count']}")

        print("\n --- Counts by Priority ---")
        for priority, count in summary.get("priority_counts", {}).items():
            p_label = priority if priority else "Unassigned"
            print(f"   • {p_label:<10} : {count}")

        print("\n --- Counts by Category ---")
        for category, count in summary.get("category_counts", {}).items():
            c_label = category if category else "Uncategorized"
            print(f"   • {c_label:<15} : {count}")
        print(separator + "\n")

    def show_progress(self, done: int, total: int, elapsed_seconds: float) -> None:
        """Displays a progress bar like [########------------] 4 of 10 comments | 03:05"""
        width = 20

        # Calculate progress bar
        filled = int(width * done / total) if total else 0

        # e.g. "########------------"
        bar = "#" * filled + "-" * (width - filled)
        minutes, seconds = divmod(int(elapsed_seconds), 60)

        print(f"\r[{bar}] {done} of {total} comments | {minutes:02d}:{seconds:02d} | Ctrl+C to stop ",
              end="", flush=True)        