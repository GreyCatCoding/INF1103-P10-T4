"""Cleans a raw comments CSV and saves the result as a cleaned CSV and JSON."""
from pathlib import Path

import pandas as pd
from textcleaner import TextCleaner

BASE_DIR = Path(__file__).resolve().parent
CLEANED_DIR = BASE_DIR / "cleaned"  # Default folder for cleaned CSV and JSON files


class CommentFileProcessor:
    """Reads a raw comments CSV, cleans every comment and saves CSV and JSON copies."""

    # Csv columns for cleaned output save
    __CLEANED_CSV_COLUMNS = ["User ID", "username", "original_comments", "processed_comments", "timestamp"]
    # Json columns for cleaned output and save
    __CLEANED_JSON_COLUMNS = ["User ID", "username", "processed_comments"]


    def __init__(self, output_dir: Path = CLEANED_DIR):
        self.__output_dir = Path(output_dir)
        self.__cleaner = TextCleaner() 

    def process(self, input_path: Path, output_path: Path | None = None) -> tuple[pd.DataFrame, Path, Path]:
        """Cleans the 'comments' column of input_path and saves the results.

        Returns (cleaned_df, csv_path, json_path).
        Raises ValueError if the CSV has no 'comments' column.
        """
        input_path = Path(input_path)
        self.__output_dir.mkdir(parents=True, exist_ok=True)

        if output_path:
            csv_output = Path(output_path)
        else:
            csv_output = self.__output_dir / f"{input_path.stem}_cleaned.csv"
        json_output = csv_output.with_suffix(".json")  # JSON is saved next to the CSV with the same name

        df = pd.read_csv(input_path)
        if "comments" not in df.columns:
            raise ValueError("The CSV must contain a 'comments' column.")

        # Empty comments become "" so the cleaner never receives NaN
        df["original_comments"] = df["comments"].fillna("")
        df["processed_comments"] = df["original_comments"].apply(self.__cleaner.clean) # referencing the method in textcleaner.py class

        cleaned_df = self.__keep_columns(df, self.__CLEANED_CSV_COLUMNS)
        cleaned_df.to_csv(csv_output, index=False)

        json_df = self.__keep_columns(cleaned_df, __CLEANED_JSON_COLUMNS)
        json_df.to_json(json_output, orient="records", indent=4)

        return cleaned_df, csv_output, json_output

    def __keep_columns(self, df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
            """Returns only the listed columns that exist in df, in the listed order."""
            present_columns = []
            for column in columns:
                if column in df.columns:
                    present_columns.append(column)
            return df[present_columns]