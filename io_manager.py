# =============================================================
# LIBRARIES & DIRECTORY SETUP
# =============================================================
from pathlib import Path  # Standard library for object-oriented filesystem paths
import re  # Regular expressions library for text manipulation and cleaning
import pandas as pd  # Data manipulation library for loading, transforming, and saving CSV/JSON
import data_manager

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
URL_EMAIL_PUNCT = re.compile(r"https?://\S+|www\.\S+|\S+@\S+|[^a-zA-Z0-9$*@!\s]")      # Combined pre-compiled regex to clear URLs, email addresses, and punctuation, keeping letters, digits and $*@! used in disguised words
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
def get_input_file() -> Path | None:
    """Scans 'uncleaned' directory, displays available CSV files, and prompts selection."""
    UNCLEANED_DIR.mkdir(exist_ok=True, parents=True)

    while True:
        csv_files = sorted(p.name for p in UNCLEANED_DIR.glob("*.csv"))

        if not csv_files:
            print("\nNo CSV files found in the 'uncleaned' directory.")
            return None

        print("\nAvailable uncleaned CSV files:")
        for file in csv_files:
            print(f"- {file}")

        file_map = {f.casefold(): f for f in csv_files}

        filename = input("\nEnter CSV filename (or type 'back' to return): ").strip()
        if filename.lower() == "back":
            return None

        if not filename.endswith(".csv"):
            filename += ".csv"

        selected = file_map.get(filename.casefold())

        if not selected:
            print(f"\n[Error] '{filename}' not found in 'uncleaned/'. Please try again.")
            continue

        selected_path = UNCLEANED_DIR / selected

        # Inline column check for raw CSVs
        try:
            df_preview = pd.read_csv(selected_path, nrows=1)
            cols = [c.lower() for c in df_preview.columns]

            has_username = "username" in cols
            has_comments = "comments" in cols or "comment" in cols

            if not has_username or not has_comments:
                missing = []
                if not has_username: missing.append("'username'")
                if not has_comments: missing.append("'comments' (or 'comment')")
                print(f"\n[Error] '{selected}' is missing required column(s): {', '.join(missing)}")
                print("Please select a valid CSV file.\n")
                continue

            return selected_path

        except pd.errors.EmptyDataError:
            print(f"\n[Error] '{selected}' is empty. Please select a valid CSV file.\n")
            continue
        except Exception as e:
            print(f"\n[Error] Failed to read '{selected}': {e}\n")
            continue

def get_cleaned_file() -> tuple[pd.DataFrame, Path] | tuple[None, None]:
    """Scans 'cleaned' directory, handles user input selection, 
    and catches validation faults when loading."""
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)

    while True:
        csv_files = sorted(p.name for p in CLEANED_DIR.glob("*.csv"))

        if not csv_files:
            print("\nNo cleaned CSV files found in the 'cleaned' directory.")
            return None, None

        print("\nAvailable cleaned CSV files:")
        for file in csv_files:
            print(f"- {file}")

        filename = input("\nEnter cleaned CSV filename (or type 'back' to return): ").strip()
        if filename.lower() == "back":
            return None, None

        try:
            # Calls data_manager to validate and load the file safely
            cleaned_df, cleaned_path = data_manager.load_cleaned_file(filename)
            return cleaned_df, cleaned_path

        except (FileNotFoundError, ValueError, pd.errors.EmptyDataError) as e:
            print(f"\n[Error] {e}")
            print("Please select a valid, non-empty cleaned CSV file.\n")
            continue
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
        else CLEANED_DIR / f"{input_path.stem}_cleaned.csv")                    # Use specified output path or generate default path using input file name stem
    json_output = csv_output.with_suffix(".json")                               # Automatically derive the matching JSON path from the CSV output path
    df = pd.read_csv(input_path)                                                # Read source CSV file into a pandas DataFrame
    # Validate that required target column exists
    if "comments" not in df.columns:
        raise ValueError("The CSV must contain a 'comments' column.")
    df["original_comments"] = df["comments"].fillna("")                         # Fill NaN values with empty strings to avoid errors during text manipulation
    df["processed_comments"] = df["original_comments"].apply(clean_text)        # Apply the clean_text function to every comment row

    expected_cols = ["User ID","username","original_comments","processed_comments","timestamp",]     # Define columns to keep for the main DataFrame and CSV export
    df = df[[c for c in expected_cols if c in df.columns]]
    df.to_csv(csv_output, index=False)                                          # Export complete cleaned DataFrame to CSV

    # Define specific subset of columns required for JSON export
    json_cols = ["User ID", "username", "processed_comments"]
    json_df = df[[c for c in json_cols if c in df.columns]]
    json_df.to_json(json_output, orient="records", indent=4)                    # Export filtered DataFrame to JSON formatted as an array of record objects

    return (df,csv_output,json_output,)                                         # Return structured data frame along with saved file paths

# =============================================================
# TERMINAL TABLE DISPLAY
# =============================================================
def print_table(df: pd.DataFrame, max_width: int = 36):
    """Prints a neatly formatted ASCII representation of a DataFrame to the console
    using pandas built-in option controls without requiring manual table drawing loops."""
    # Set temporary display options for column width and total output width
    with pd.option_context("display.max_colwidth", max_width, "display.width", 1000):
        print(df.to_string(index=False))  # Convert DataFrame to clean string without index numbers
        
def print_detailed_records(df: pd.DataFrame) -> None:
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

def display_existing_cleaned_file() -> tuple[pd.DataFrame | None, Path | None]:
    """Handles prompt loop for selecting and displaying an existing cleaned CSV."""
    while True:
        csv_files = data_manager.get_available_cleaned_files()

        if not csv_files:
            print("\nNo cleaned CSV files found in the 'cleaned' directory.")
            return None, None

        print("\nAvailable cleaned CSV files:")
        for file in csv_files:
            print(f"- {file}")

        filename = input("\nEnter cleaned CSV filename (or type 'back' to return): ").strip()
        if filename.lower() == "back":
            return None, None

        try:
            cleaned_df, cleaned_file_path = data_manager.load_cleaned_file(filename)
            print(f"\nLoading {cleaned_file_path.name}...")
            return cleaned_df, cleaned_file_path

        except (FileNotFoundError, ValueError, pd.errors.EmptyDataError) as e:
            print(f"\n[Error] {e}")
            print("Please select a valid, non-empty cleaned CSV file.\n")

def print_summary_view(df: pd.DataFrame) -> None:
    """Prints a neat, formatted summary card of moderation statistics."""
    summary = data_manager.get_summary_metrics(df)

    if summary["total_records"] == 0:
        print("\n--- Summary Statistics ---")
        print("No data available to summarize.")
        return

    separator = "=" * 55
    print("\n" + separator)
    print("           MODERATION DATASET SUMMARY")
    print(separator)
    print(f" Total Comments Analyzed : {summary['total_records']}")
    print(f" Pending Human Review    : {summary['human_review_count']}")

    print("\n --- Counts by Priority ---")
    for priority, count in summary["priority_counts"].items():
        p_label = priority if priority else "Unassigned"
        print(f"   • {p_label:<10} : {count}")

    print("\n --- Counts by Category ---")
    for category, count in summary["category_counts"].items():
        c_label = category if category else "Uncategorized"
        print(f"   • {c_label:<15} : {count}")

    print(separator + "\n")
# =============================================================
# MAIN WORKFLOW EXECUTION
# =============================================================
def run_input_workflow():
    """Coordinates file selection, cleans data, saves outputs, and prints before/after summaries."""
    input_file = get_input_file()
    
    # SAFETY CHECK: If user typed 'back', safely return None
    if input_file is None:
        return None, None

    print(f"\nProcessing {input_file.name}...")                     # processing message
    raw_df = pd.read_csv(input_file)
    cleaned_df, csv_path, json_path = process_csv(input_file)

    print("\n--- Uncleaned Data Preview (Top 5) ---")
    print_table(raw_df.head(5))
    print(f"\nSaved CSV to: {csv_path}")
    print(f"Saved JSON to: {json_path}")
    print("\n--- Cleaned Data Preview (Top 5) ---")
    print_table(cleaned_df.head(5))

    return cleaned_df, csv_path

def run_output_workflow(df: pd.DataFrame) -> None:
    """Displays the DataFrame and offers an option to start filtering or exit directly."""
    print("\nModerated DataFrame:")
    print_detailed_records(df)
    print_summary_view(df)

    while True:
        print("\n=== Filter Moderated Data ===")
        print("1.) Start Filtering")
        print("2.) Exit to Main Menu")

        choice = input("\nSelect an option (1-2): ").strip()

        if choice == "2":
            print("Exiting filter system...")
            break
        elif choice != "1":
            print("\n[Error] Invalid choice. Please enter 1 or 2.")
            continue
        while True:
            print("\n--- Filter Options ---")
            category_input = input("Enter Category (e.g., harassment, spam, hate): ").strip()
            action_input = input("Enter Action/Priority (e.g., P1, P2, P3, P4): ").strip()
            category = category_input if category_input else None
            action = action_input if action_input else None
            # Fault checking: no neither
            if category is None and action is None:
                print("\n[Error] You must provide either a Category or an Action to filter.")
                continue
            # Query execution
            results = data_manager.query(df, category=category, action=action)

            print("\n--- Filter Results ---")
            if results.empty:
                print("No matching records found.")
            else:
                print_detailed_records(results)
            break  # Return to the main filter option menu after printing results

def main_menu(process_callback=None):
    """Displays the main options menu and routes user selections."""
    while True:
        print("\n" + "=" * 40)
        print("      DATA CLEANING & MANAGEMENT MENU      ")
        print("=" * 40)
        print("1.) Cleanse New File")
        print("2.) Display Existing Cleaned File")
        print("3.) Exit")

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            cleaned_df, csv_path = run_input_workflow()
            if cleaned_df is not None:
                if process_callback:
                    final_df = process_callback(cleaned_df, csv_path)
                    run_output_workflow(final_df)
                else:
                    run_output_workflow(cleaned_df)

        elif choice == "2":
            cleaned_df, csv_path = display_existing_cleaned_file()
            if cleaned_df is not None:
                run_output_workflow(cleaned_df)

        elif choice == "3":
            print("\nExiting program. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")