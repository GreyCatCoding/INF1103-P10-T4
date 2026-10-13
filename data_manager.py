# we need to have the following in json file, ID, Username, Comments, Categories, Actions
# we need to have save() function to save the json file into csv (Glenden)
# we need to have load() function to load the csv file (Glenden)
# we need to have query() function to filter the data based on categories and actions (Brian)
# we need to have error handling for file not found, invalid data, etc. (Brian)
# provide the data with datatype like int, str, list, etc. (Brian)
import pandas as pd
import csv
import json
import os



# Columns to display in the DataFrame 
DISPLAY_COLUMNS = ["User ID", "username", "comment", "category", "priority"]


def to_dataframe(reports: list) -> pd.DataFrame:
    # Converts the logic manager's list of report dicts into a DataFrame for display and filtering
    return pd.DataFrame(reports).reindex(columns=DISPLAY_COLUMNS).fillna("")

def save_reports(df: pd.DataFrame, csv_filepath: str) -> None:
    #Saves the DataFrame to a CSV file.
    df.to_csv(csv_filepath, index=False)


def load_reports(csv_filepath: str) -> pd.DataFrame:
#Loads a previously saved CSV into a DataFrame.
    if not os.path.exists(csv_filepath):
        raise FileNotFoundError(f"The CSV file '{csv_filepath}' was not found.")
    return pd.read_csv(csv_filepath).fillna("")

def query(df, category=None, action=None):

#Filters the DataFrame based on category and/or action.
#Case-insensitive and matches exact string or partial matches.

    filtered_df = df.copy()

    if category:
# Normalize the category string for comparison
        choice_of_category = category.strip().lower().replace(" ", "_")
        filtered_df = filtered_df[filtered_df["category"].astype(str).str.lower() == choice_of_category] # filter by category as a normalized string

    if action:
        filtered_df = filtered_df[filtered_df["priority"].astype(str).str.lower() == action.strip().lower()]


    return filtered_df