#import necessary libraries
from datetime import datetime # For handling date and time 
from pathlib import Path # For handling file paths
import re # Regular expressions for data cleansing
import contractions # Add on Library to expand contractions in text
import pandas as pd # For Data manipulation and analysis library

OUTPUT_FILE = Path(__file__).with_name("user_input_records.csv")

# Load dataset and filling missing comments with empty strings
df = pd.read_csv('test_processed.csv')
df['comments'] = df['comments'].fillna('')

# Displaying the first few rows of the DataFrame to verify loading and preprocessing
print(df.head())

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

# -------------------------------------------------------------
# USER ID
# -------------------------------------------------------------

def _next_user_id(file_path=OUTPUT_FILE):
    if not file_path.exists() or file_path.stat().st_size == 0:
        return "00000"

    existing = pd.read_csv(file_path)

    if "User ID" not in existing:
        return "00000"

    numeric_ids = pd.to_numeric(
        existing["User ID"],
        errors="coerce"
    ).dropna()

    return f"{int(numeric_ids.max()) + 1 if not numeric_ids.empty else 0:05d}"

# -------------------------------------------------------------
# COLLECT INPUT
# -------------------------------------------------------------

def collect_input(file_path=OUTPUT_FILE):
    """Collect a non-empty comment and generate its ID and timestamp."""
    while True:
        try:
            comment = input("Enter comment: ")
        except (EOFError, KeyboardInterrupt):
            print("Input cancelled.")
            return None

        comment = " ".join(comment.split())
        if comment:
            return {
                "User ID": _next_user_id(file_path),
                "comments": comment,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        print("Comment cannot be empty. Please try again.")

# -------------------------------------------------------------
# WORKFLOW
# -------------------------------------------------------------

def run_input_workflow():

    record = collect_input()

    if record is not None:
        print("\nInput accepted:")
        print(f"User ID: {record['User ID']}")
        print(f"Timestamp: {record['timestamp']}")
        print(f"Original Comment: {record['comments']}")

    return record


if __name__ == "__main__":
    run_input_workflow()