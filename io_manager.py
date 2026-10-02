#import necessary libraries
from datetime import datetime # For handling date and time 
from pathlib import Path # For handling file paths
import re # Regular expressions for data cleansing
import pandas as pd # For Data manipulation and analysis library
import textwrap


BASE_DIR = Path(__file__).resolve().parent
UNCLEANED_DIR = BASE_DIR / "uncleaned"
CLEANED_DIR = BASE_DIR / "cleaned"

# -------------------------------------------------------------
# FILE HANDLING
# -------------------------------------------------------------
def ensure_csv(file_path: Path, columns=None):
    """Create the CSV file if it does not already exist."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if columns is None:
        columns = ["User ID", "comments", "timestamp"]
    if not file_path.exists():
        pd.DataFrame(columns=columns).to_csv(file_path, index=False)
    return file_path


# -------------------------------------------------------------
# SLANG DICTIONARY & REGEX SETUP
# -------------------------------------------------------------
SLANG_DICT = {
    "lol": "laugh out loud",
    "sybau": "shut your bitch ass up",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "tbh": "to be honest",
    "smh": "shaking my head",
    "afk": "away from keyboard",
    "btw": "by the way",
    "idk": "i do not know",
    "omg": "oh my god",
    "ur": "your",
    "r": "are",
    "u": "you",
    "rfc": "request for comments"
}

# Pre-compile slang pattern
sorted_slang = sorted(SLANG_DICT.keys(), key=len, reverse=True)
SLANG_PATTERN = re.compile(
    r'\b(' + '|'.join(map(re.escape, sorted_slang)) + r')\b', 
    flags=re.IGNORECASE
)

# Compile remaining regex patterns once for performance
URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')
EMAIL_PATTERN = re.compile(r'\S+@\S+')
PUNCT_PATTERN = re.compile(r'[^a-zA-Z\s]')
WHITESPACE_PATTERN = re.compile(r'\s+')

# -------------------------------------------------------------
# Text Cleaning & Standardization
# -------------------------------------------------------------
def clean_text(text):
    if not isinstance(text, str) or not text.strip():
        return ""
    
    text = text.lower()                                                # 1. Lowercase
    text = URL_PATTERN.sub('', text)                                  # 2. Remove URLs
    text = EMAIL_PATTERN.sub('', text)                                # 3. Remove emails
    text = SLANG_PATTERN.sub(lambda m: SLANG_DICT[m.group(0)], text)  # 4. Expand slang
    text = PUNCT_PATTERN.sub('', text)                                # 5. Remove punctuation & special chars
    text = WHITESPACE_PATTERN.sub(' ', text).strip()                  # 6. Normalize spacing
    
    return text


# -------------------------------------------------------------
# FILE NAME INPUT
# -------------------------------------------------------------
def list_available_csv_files():
    """Display all CSV files in the uncleaned directory that can be selected."""
    UNCLEANED_DIR.mkdir(exist_ok=True, parents=True)
    csv_files = sorted(p.name for p in UNCLEANED_DIR.glob("*.csv"))
    if not csv_files:
        print("No CSV files found in the uncleaned folder.")
        return []

    print("Available uncleaned CSV files:")
    for file_name in csv_files:
        print(f"- {file_name}")
    return csv_files


def get_input_file():
    """Ask the user to choose an existing CSV from the uncleaned directory."""
    csv_files = list_available_csv_files()
    if not csv_files:
        raise FileNotFoundError("No CSV files are available in the uncleaned folder.")

    filename = input("\nEnter CSV filename: ").strip()

    if not filename.lower().endswith(".csv"):
        filename += ".csv"

    if filename not in csv_files:
        raise ValueError(f"Select one of the listed CSV files: {', '.join(csv_files)}")

    return UNCLEANED_DIR / filename


# -------------------------------------------------------------
# CSV PROCESSING
# -------------------------------------------------------------
def process_csv(input_path, output_path=None):
    """Read the chosen input CSV, clean comments, and save them to a fresh cleaned CSV."""
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_path is None:
        output_path = CLEANED_DIR / f"{input_path.stem}_cleaned.csv"

    df = pd.read_csv(input_path)
    if "comments" not in df.columns:
        raise ValueError("The CSV must contain a 'comments' column.")

    df["original_comments"] = df["comments"].fillna("")
    df["processed_comments"] = df["original_comments"].apply(clean_text)
    df = df[["User ID", "original_comments", "processed_comments", "timestamp"]]
    df.to_csv(output_path, index=False)

    return df, output_path


def print_wrapped_table(dataframe):
    """Print a compact table with long comment values wrapped within their columns."""
    columns = list(dataframe.columns)
    widths = {}
    for column in columns:
        if column in {"comments", "original_comments", "processed_comments"}:
            widths[column] = 36
        else:
            values = dataframe[column].fillna("").astype(str)
            widest_value = max((len(value) for value in values), default=0)
            widths[column] = max(len(column), min(widest_value, 24))

    separator = "+-" + "-+-".join("-" * widths[column] for column in columns) + "-+"
    print(separator)
    print("| " + " | ".join(column.ljust(widths[column]) for column in columns) + " |")
    print(separator)

    for row in dataframe.itertuples(index=False, name=None):
        wrapped_cells = []
        for column, value in zip(columns, row):
            value = "" if pd.isna(value) else str(value)
            wrapped_cells.append(
                textwrap.wrap(
                    value,
                    width=widths[column],
                    break_long_words=True,
                    break_on_hyphens=False,
                ) or [""]
            )

        row_height = max(len(lines) for lines in wrapped_cells)
        for line_index in range(row_height):
            cells = [
                (lines[line_index] if line_index < len(lines) else "").ljust(widths[column])
                for column, lines in zip(columns, wrapped_cells)
            ]
            print("| " + " | ".join(cells) + " |")
    print(separator)

# -------------------------------------------------------------
# WORKFLOW
# -------------------------------------------------------------

def run_input_workflow():
    """Ask for a CSV filename, process it, and show the cleaned file contents."""
    input_file = get_input_file()
    print(f"\nUsing input file: {input_file}")

    CLEANED_DIR.mkdir(exist_ok=True, parents=True)

    print("\nProcessing...")
    raw_df = pd.read_csv(input_file)
    cleaned_df, output_path = process_csv(input_file)

    print("\nUncleaned:")
    print_wrapped_table(raw_df[["User ID", "comments", "timestamp"]].head(5))

    print("\nCleaned:")
    print(f"Saved to {output_path}")

    cleaned_preview = pd.read_csv(output_path)
    cleaned_preview = cleaned_preview[["User ID", "original_comments", "processed_comments", "timestamp"]]
    print_wrapped_table(cleaned_preview.head(5))
    return cleaned_df


if __name__ == "__main__":
    run_input_workflow()