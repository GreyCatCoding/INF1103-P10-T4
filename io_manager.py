# =============================================================
# LIBRARIES & DIRECTORY SETUP
# =============================================================
from pathlib import Path  # Standard library for object-oriented filesystem paths
import re  # Regular expressions library for text manipulation and cleaning
import pandas as pd  # Data manipulation library for loading, transforming, and saving CSV/JSON

BASE_DIR = Path(__file__).resolve().parent # Define the root directory relative to where this script is located
UNCLEANED_DIR = BASE_DIR / "uncleaned" # Directory for Uncleaned CSV files
CLEANED_DIR = BASE_DIR / "cleaned" # Directory for Cleaned CSV and JSON files

# =============================================================
# SLANG DICTIONARY & REGEX PRE-COMPILATION
# =============================================================
SLANG_DICT = {
    "lol": "laugh out loud","sybau": "shut your bitch ass up","imo": "in my opinion","imho": "in my humble opinion",
    "tbh": "to be honest","smh": "shaking my head","fk": "fuck","btw": "by the way","idk": "i do not know","omg": "oh my god",
    "ur": "your","r": "are","u": "you","rfc": "request for comments",}
sorted_slang = sorted(SLANG_DICT.keys(), key=len, reverse=True)
SLANG_PATTERN = re.compile(r"\b(" + "|".join(map(re.escape, sorted_slang)) + r")\b",flags=re.IGNORECASE,) # Pre-compile a case-insensitive regex pattern matching any slang word surrounded by word boundaries (\b)
URL_EMAIL_PUNCT = re.compile(r"https?://\S+|www\.\S+|\S+@\S+|[^a-zA-Z\s]")      # Combined pre-compiled regex to clear URLs, email addresses, and non-alphabetic/non-whitespace characters in one pass

# =============================================================
# TEXT CLEANING & STANDARDIZATION
# =============================================================
def clean_text(text: str) -> str:
    """Standardizes comment text by converting to lowercase, expanding slang,
    stripping URLs, emails, special characters, and normalizing extra spaces."""
    # Guard clause: Return an empty string if input is not valid text or consists only of whitespace
    if not isinstance(text, str) or not text.strip():
        return ""
    text = text.lower()                                                      # Convert entire string to lowercase for uniform processing
    text = SLANG_PATTERN.sub(lambda m: SLANG_DICT[m.group(0).lower()], text) # Expand slang using SLANG_DICT; .lower() prevents KeyError if matched text was capitalized
    text = URL_EMAIL_PUNCT.sub("", text)                                     # Remove URLs, emails, punctuation, and non-alphabetical characters
    return " ".join(text.split())                                            # Split on whitespace and rejoin with a single space to collapse multiple spaces/newlines

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


# =============================================================
# CSV & JSON PROCESSING
# =============================================================
def process_csv(input_path: Path, output_path: Path = None):
    """Reads a CSV file, cleans the 'comments' column, creates both original and processed comment columns,
    and exports the result to both CSV and JSON in the 'cleaned' directory."""
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)                              # Ensure the output directory exists

    csv_output = (
        Path(output_path)
        if output_path
        else CLEANED_DIR / f"{input_path.stem}_cleaned.csv"
    )                                                                           # Use specified output path or generate default path using input file name stem

    json_output = csv_output.with_suffix(".json")                               # Automatically derive the matching JSON path from the CSV output path
    df = pd.read_csv(input_path)                                                # Read source CSV file into a pandas DataFrame
    # Validate that required target column exists
    if "comments" not in df.columns:
        raise ValueError("The CSV must contain a 'comments' column.")
    df["original_comments"] = df["comments"].fillna("")                         # Fill NaN values with empty strings to avoid errors during text manipulation
    df["processed_comments"] = df["original_comments"].apply(clean_text)        # Apply the clean_text function to every comment row

    expected_cols = ["User ID","username","original_comments","processed_comments","timestamp",]     # Define columns to keep for the main DataFrame and CSV export
    df = df[[c for c in expected_cols if c in df.columns]]
    df.to_csv(csv_output, index=False)     # Export complete cleaned DataFrame to CSV

    # Define specific subset of columns required for JSON export
    json_cols = ["User ID", "username", "processed_comments"]
    json_df = df[[c for c in json_cols if c in df.columns]]
    json_df.to_json(json_output, orient="records", indent=4) # Export filtered DataFrame to JSON formatted as an array of record objects

    return (df,csv_output,json_output,)  # Return structured data frame along with saved file paths


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