# we need to have the following in json file, ID, Username, Comments, Categories, Actions
# we need to have save() function to save the json file into csv (Glenden)
# we need to have load() function to load the csv file (Glenden)
# we need to have query() function to filter the data based on categories and actions (Brian)
# we need to have error handling for file not found, invalid data, etc. (Brian)
from pathlib import Path
import pandas as pd

# Define CLEANED_DIR relative to the script location
BASE_DIR = Path(__file__).resolve().parent
CLEANED_DIR = BASE_DIR / "cleaned"

# Columns to display in the DataFrame 
DISPLAY_COLUMNS = ["User ID", "username", "comment", "category", "category_description", "priority", "recommended_action", "ai_reason"]

def validate_csv_structure(file_path: Path) -> None:
    """Validates that a CSV file exists and is not empty.
    Raises ValueError or FileNotFoundError if invalid."""
    if not file_path.exists():
        raise FileNotFoundError(f"File '{file_path.name}' does not exist.")

    if file_path.stat().st_size == 0:
        raise ValueError(f"The file '{file_path.name}' is empty (0 bytes).")

    df_preview = pd.read_csv(file_path, nrows=1)
    if df_preview.empty and len(df_preview.columns) == 0:
        raise ValueError(f"The file '{file_path.name}' contains no readable data.")

def get_available_cleaned_files() -> list[str]:
    """Returns a sorted list of available cleaned CSV filenames."""
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)
    return sorted(p.name for p in CLEANED_DIR.glob("*.csv"))

def load_cleaned_file(filename: str) -> tuple[pd.DataFrame, Path]:
    """Resolves and loads a cleaned CSV file by filename.
    Raises FileNotFoundError or ValueError on invalid inputs."""
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)

    if not filename.endswith(".csv"):
        filename += ".csv"

    file_path = CLEANED_DIR / filename
    validate_csv_structure(file_path)

    df = pd.read_csv(file_path).fillna("")
    return df, file_path

def to_dataframe(reports: list) -> pd.DataFrame:
    """Converts a list of report dicts into a formatted DataFrame."""
    return pd.DataFrame(reports).reindex(columns=DISPLAY_COLUMNS).fillna("")

def save_reports(df: pd.DataFrame, file_target: str | Path) -> Path:
    """Saves or overwrites a DataFrame as a CSV file in the 'cleaned' directory."""
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)
    path_obj = Path(file_target)

    output_path = CLEANED_DIR / path_obj.name if not path_obj.is_absolute() else path_obj

    if output_path.suffix != ".csv":
        output_path = output_path.with_suffix(".csv")

    df.to_csv(output_path, index=False)
    return output_path

def query(df: pd.DataFrame, category: str = None, action: str = None) -> pd.DataFrame:
    """Filters the DataFrame by category OR action/priority."""
    filtered_df = df.copy()

    if category:
        choice_of_category = category.strip().lower().replace(" ", "_")
        filtered_df = filtered_df[filtered_df["category"].astype(str).str.lower() == choice_of_category]

    if action:
        filtered_df = filtered_df[filtered_df["priority"].astype(str).str.lower() == action.strip().lower()]

    return filtered_df