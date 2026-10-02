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
    text = contractions.fix(text)                                     # 4. Expand contractions (e.g., don't -> do not)
    text = SLANG_PATTERN.sub(lambda m: SLANG_DICT[m.group(0)], text)  # 5. Expand slang
    text = PUNCT_PATTERN.sub('', text)                                # 6. Remove punctuation & special chars
    text = WHITESPACE_PATTERN.sub(' ', text).strip()                  # 7. Normalize spacing
    
    return text

# Apply preprocessing
df['processed_comments'] = df['comments'].apply(clean_text)

# Save processed data
df.to_csv('cleaned_data.csv', index=False)
print("Data processed successfully! Output saved to cleaned_data.csv")

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
        print(f"Processed Comment: {clean_text(record['comments'])}")

    return record


if __name__ == "__main__":
    run_input_workflow()