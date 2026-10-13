# =============================================================
# LIBRARIES & DIRECTORY SETUP
# =============================================================
from pathlib import Path
import pandas as pd

# Define CLEANED_DIR relative to the script location
BASE_DIR = Path(__file__).resolve().parent
CLEANED_DIR = BASE_DIR / "cleaned"

# Columns to display in the DataFrame 
DISPLAY_COLUMNS = ["User ID", "username", "comment", "category", "category_description", "priority", "recommended_action", "ai_reason"]

# =============================================================
# DATA VALIDATION & FILE LOADING
# =============================================================
def validate_csv_structure(file_path: Path) -> None:
    """Validates that a CSV file exists, is non-empty, and contains readable data.
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is 0 bytes or contains no readable rows/headers.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File '{file_path.name}' does not exist.")

    if file_path.stat().st_size == 0:
        raise ValueError(f"The file '{file_path.name}' is empty (0 bytes).")

    df_preview = pd.read_csv(file_path, nrows=1)
    if df_preview.empty and len(df_preview.columns) == 0:
        raise ValueError(f"The file '{file_path.name}' contains no readable data.")


def get_available_cleaned_files() -> list[str]:
    """Scans the 'cleaned' directory and returns a sorted list of CSV filenames.
    Returns:
        list[str]: Alphabetically sorted list of .csv filenames.
    """
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)
    return sorted(p.name for p in CLEANED_DIR.glob("*.csv"))


def load_cleaned_file(filename: str) -> tuple[pd.DataFrame, Path]:
    """Resolves and loads a CSV file from the 'cleaned' directory.
    Args:
        filename (str): The filename provided by the user.
    Returns:
        tuple[pd.DataFrame, Path]: Loaded DataFrame and its resolved absolute Path. 
    Raises:
        FileNotFoundError: If the file is not found.
        ValueError: If the file fails structural validation.
    """
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)

    if not filename.endswith(".csv"):
        filename += ".csv"

    file_path = CLEANED_DIR / filename
    validate_csv_structure(file_path)

    df = pd.read_csv(file_path).fillna("")
    return df, file_path


# =============================================================
# DATAFRAME, SUMMARY METRICS & PERSISTENCE MANAGEMENT
# =============================================================
def to_dataframe(reports: list[dict]) -> pd.DataFrame:
    """Converts a list of report dictionaries from Logic_Manager into a standardized DataFrame.
    Args:
        reports (list[dict]): Raw records processed by the logic layer.
    Returns:
        pd.DataFrame: Reindexed and sanitized DataFrame ready for storage/display.
    """
    return pd.DataFrame(reports).reindex(columns=DISPLAY_COLUMNS).fillna("")

def get_summary_metrics(df: pd.DataFrame) -> dict:
    """Calculates summary statistics for a moderation DataFrame.
    Args:
        df (pd.DataFrame): The moderation DataFrame.
    Returns:
        dict: A structured dictionary containing overall counts, priority 
              breakdowns, category breakdowns, and human review requirements.
    """
    if df.empty:
        return {
            "total_records": 0,
            "priority_counts": {},
            "category_counts": {},
            "human_review_count": 0,
        }

    # Count total records
    total_records = len(df)

    # Priority counts (e.g., P1, P2, P3, P4)
    priority_counts = df["priority"].value_counts().to_dict() if "priority" in df.columns else {}

    # Category counts (e.g., harassment, sexual, hate)
    category_counts = df["category"].value_counts().to_dict() if "category" in df.columns else {}

    # Human review flag count (checks recommended_action or ai_reason for keywords)
    human_review_count = 0
    if "recommended_action" in df.columns:
        human_review_count = df["recommended_action"].astype(str).str.contains(
            r"human|review|moderator", case=False, regex=True
        ).sum()

    return {
        "total_records": total_records,
        "priority_counts": priority_counts,
        "category_counts": category_counts,
        "human_review_count": int(human_review_count),
    }


def save_reports(df: pd.DataFrame, file_target: str | Path) -> Path:
    """Saves or overwrites a DataFrame to a CSV file inside the 'cleaned' directory.
    
    Args:
        df (pd.DataFrame): The DataFrame to save.
        file_target (str | Path): Path or filename target.
        
    Returns:
        Path: Absolute path of the saved CSV file.
    """
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)
    path_obj = Path(file_target)

    # Output to 'cleaned' folder if relative path given
    output_path = CLEANED_DIR / path_obj.name if not path_obj.is_absolute() else path_obj

    if output_path.suffix != ".csv":
        output_path = output_path.with_suffix(".csv")

    df.to_csv(output_path, index=False)
    return output_path


# =============================================================
# DATA FILTERING & QUERY SYSTEM
# =============================================================
def query(
    df: pd.DataFrame, 
    category: str | None = None, 
    action: str | None = None
) -> pd.DataFrame:
    """Filters a DataFrame based on Category OR Action (priority).
    
    Args:
        df (pd.DataFrame): The target DataFrame to filter.
        category (str | None): Category filter term (e.g., 'harassment', 'spam').
        action (str | None): Action/Priority filter term (e.g., 'P1', 'P2').
        
    Returns:
        pd.DataFrame: A new DataFrame containing only matching records.
    """
    filtered_df = df.copy()

    if category:
        choice_of_category = category.strip().lower().replace(" ", "_")
        filtered_df = filtered_df[
            filtered_df["category"].astype(str).str.lower() == choice_of_category
        ]

    if action:
        filtered_df = filtered_df[
            filtered_df["priority"].astype(str).str.lower() == action.strip().lower()
        ]

    return filtered_df