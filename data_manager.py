# we need to have the following in json file, ID, Username, Comments, Categories, Actions
# we need to have save() function to save the json file into csv (Glenden)
# we need to have load() function to load the csv file (Glenden)
# we need to have query() function to filter the data based on categories and actions (Brian)
# we need to have error handling for file not found, invalid data, etc. (Brian)
from pathlib import Path
import pandas as pd
import os

# Define CLEANED_DIR relative to the script location
BASE_DIR = Path(__file__).resolve().parent
CLEANED_DIR = BASE_DIR / "cleaned"

# Columns to display in the DataFrame 
DISPLAY_COLUMNS = ["User ID", "username", "comment", "category", "category_description", "priority", "recommended_action", "ai_reason"]


def to_dataframe(reports: list) -> pd.DataFrame:
    # Converts the logic manager's list of report dicts into a DataFrame for display and filtering
    return pd.DataFrame(reports).reindex(columns=DISPLAY_COLUMNS).fillna("")

def save_reports(df: pd.DataFrame, file_target: str | Path) -> Path:
    """Saves or overwrites the DataFrame in the 'cleaned' directory.
    Accepts either a filename/stem (e.g., 'data_cleaned.csv' or 'data') 
    or a full file path.
    """
    CLEANED_DIR.mkdir(exist_ok=True, parents=True)
    
    path_obj = Path(file_target)
    
    # If a plain filename (or relative path) is given, save it inside CLEANED_DIR
    if not path_obj.is_absolute():
        output_path = CLEANED_DIR / path_obj.name
    else:
        output_path = path_obj

    # Ensure .csv extension
    if output_path.suffix != ".csv":
        output_path = output_path.with_suffix(".csv")

    df.to_csv(output_path, index=False)
    return output_path

def load_reports(csv_filepath: str) -> pd.DataFrame:
#Loads a previously saved CSV into a DataFrame.
    if not os.path.exists(csv_filepath):
        raise FileNotFoundError(f"The CSV file '{csv_filepath}' was not found.")
    return pd.read_csv(csv_filepath).fillna("")

def query(df, category=None, action=None):
    filtered_df = df.copy()
    if category: # Normalize the category string for comparison
        choice_of_category = category.strip().lower().replace(" ", "_")
        filtered_df = filtered_df[filtered_df["category"].astype(str).str.lower() == choice_of_category] # filter by category as a normalized string

    if action:
        filtered_df = filtered_df[filtered_df["priority"].astype(str).str.lower() == action.strip().lower()]


    return filtered_df


