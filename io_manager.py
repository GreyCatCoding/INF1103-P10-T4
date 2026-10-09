# =============================================================
# LIBRARIES & DIRECTORY SETUP
# =============================================================
from pathlib import Path  # Standard library for object-oriented filesystem paths
import re  # Regular expressions library for text manipulation and cleaning
import pandas as pd  # Data manipulation library for loading, transforming, and saving CSV/JSON

BASE_DIR = Path(__file__).resolve().parent # Define the root directory relative to where this script is located
UNCLEANED_DIR = BASE_DIR / "uncleaned" # Directory for Uncleaned CSV files
CLEANED_DIR = BASE_DIR / "cleaned" # Directory for Cleaned CSV and JSON files

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
    "fk": "fuck",
    "btw": "by the way",
    "idk": "i do not know",
    "omg": "oh my god",
    "ur": "your",
    "r": "are",
    "u": "you",
    "rfc": "request for comments",
}

# Pre-compile slang pattern
sorted_slang = sorted(SLANG_DICT.keys(), key=len, reverse=True)
SLANG_PATTERN = re.compile(
    r"\b(" + "|".join(map(re.escape, sorted_slang)) + r")\b",
    flags=re.IGNORECASE,
)

# Compile remaining regex patterns once for performance
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
EMAIL_PATTERN = re.compile(r"\S+@\S+")
PUNCT_PATTERN = re.compile(r"[^a-zA-Z\s]")
WHITESPACE_PATTERN = re.compile(r"\s+")


# -------------------------------------------------------------
# Text Cleaning & Standardization
# -------------------------------------------------------------
def clean_text(text):
    if not isinstance(text, str) or not text.strip():
        return ""

    text = text.lower()  # 1. Lowercase
    text = URL_PATTERN.sub("", text)  # 2. Remove URLs
    text = EMAIL_PATTERN.sub("", text)  # 3. Remove emails
    text = SLANG_PATTERN.sub(lambda m: SLANG_DICT[m.group(0)], text)  # 4. Expand slang
    text = PUNCT_PATTERN.sub("", text)  # 5. Remove punctuation & special chars
    text = WHITESPACE_PATTERN.sub(" ", text).strip()  # 6. Normalize spacing

    return text


# =============================================================
# USER INPUT & FILE SELECTION
# =============================================================
def get_input_file() -> Path:
    """Scans the 'uncleaned' directory, displays available CSV files,
    and prompts the user to select one (case-insensitive, auto-appends .csv extension)."""
    UNCLEANED_DIR.mkdir(exist_ok=True, parents=True)                        # Ensure the input directory exists before trying to scan it
    csv_files = sorted(p.name for p in UNCLEANED_DIR.glob("*.csv"))         # Collect all .csv files in the directory and sort them alphabetically

    # Raise an explicit error if no CSV files are found to process
    if not csv_files:
        raise FileNotFoundError("No CSV files found in the 'uncleaned' folder.")
    print("Available uncleaned CSV files:")                                 # Display the list of available files to the user
    for file in csv_files:
        print(f"- {file}")
    file_map = {f.casefold(): f for f in csv_files}                         # Build a lookup map where lowercase filenames point to actual filenames for case-insensitive matching

    # Loop until the user provides a valid filename
    while True:
        filename = input("\nEnter CSV filename: ").strip()
        # Automatically append .csv extension if the user omitted it
        if not filename.endswith(".csv"):
            filename += ".csv"
        selected = file_map.get(filename.casefold())                        # Check if user input matches any file in our lookup map
        if selected:
            return UNCLEANED_DIR / selected                                 # Return absolute Path object

        print(f"'{filename}' not found. Available: {', '.join(csv_files)}") # Warn user and show available options if match fails


# -------------------------------------------------------------
# CSV & JSON PROCESSING
# -------------------------------------------------------------
def process_csv(input_path, output_path=None):
    """Read input CSV, clean comments, and save output as both CSV and JSON."""
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_path is None:
        csv_output_path = CLEANED_DIR / f"{input_path.stem}_cleaned.csv"   # Explicit CSV output path
        json_output_path = CLEANED_DIR / f"{input_path.stem}_cleaned.json" # Generated JSON output path
    else:
        csv_output_path = Path(output_path)                               # Explicit path conversion
        json_output_path = csv_output_path.with_suffix(".json")           # Derive JSON path from custom output path

    df = pd.read_csv(input_path)
    if "comments" not in df.columns:
        raise ValueError("The CSV must contain a 'comments' column.")

    df["original_comments"] = df["comments"].fillna("")
    df["processed_comments"] = df["original_comments"].apply(clean_text)
    df = df[["User ID", "original_comments", "processed_comments", "timestamp"]]

    # Export to CSV and JSON
    df.to_csv(csv_output_path, index=False)                                # Updated variable name
    df.to_json(json_output_path, orient="records", indent=4)               # Exports DataFrame to formatted JSON

    return df, csv_output_path, json_output_path                           # Returns both file paths for confirmation


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

    separator = (
        "+-" + "-+-".join("-" * widths[column] for column in columns) + "-+"
    )
    print(separator)
    print(
        "| "
        + " | ".join(column.ljust(widths[column]) for column in columns)
        + " |"
    )
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
                )
                or [""]
            )

        row_height = max(len(lines) for lines in wrapped_cells)
        for line_index in range(row_height):
            cells = [
                (
                    lines[line_index] if line_index < len(lines) else ""
                ).ljust(widths[column])
                for column, lines in zip(columns, wrapped_cells)
            ]
            print("| " + " | ".join(cells) + " |")
    print(separator)


# -------------------------------------------------------------
# WORKFLOW
# -------------------------------------------------------------
def run_input_workflow():
    """Ask for a CSV filename, process it, and save output as CSV & JSON."""
    input_file = get_input_file()
    print(f"\nUsing input file: {input_file}")

    CLEANED_DIR.mkdir(exist_ok=True, parents=True)

    print("\nProcessing...")
    raw_df = pd.read_csv(input_file)
    cleaned_df, csv_path, json_path = process_csv(input_file)              # Unpacks new json_path return value

    print("\nUncleaned:")
    print_wrapped_table(raw_df[["User ID", "comments", "timestamp"]].head(5))

    print("\nCleaned:")
    print(f"Saved CSV to: {csv_path}")                                    # Updated label to specify CSV
    print(f"Saved JSON to: {json_path}")                                  # Displays location of newly created JSON file

    cleaned_preview = pd.read_csv(csv_path)                               # csv_path variable
    cleaned_preview = cleaned_preview[["User ID", "original_comments", "processed_comments", "timestamp"]]
    print_wrapped_table(cleaned_preview.head(5))
    return cleaned_df

if __name__ == "__main__":
    run_input_workflow()