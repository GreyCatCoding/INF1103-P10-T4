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

# Example Usage:
# Load your JSON data
df = pd.read_json("data_manager_test.json") #For testing purposes, will update as we go

def save(json_filepath: str, csv_filepath: str) -> None:
    """
    Saves data from a JSON file into a CSV file.
    Args:
        json_filepath (str): Path to the source JSON file.
        csv_filepath (str): Path to the destination CSV file.
    Raises:
        FileNotFoundError: If the JSON file does not exist.
        ValueError: If the JSON data is invalid or empty.
    """
    if not os.path.exists(json_filepath):
        raise FileNotFoundError(f"The JSON file '{json_filepath}' was not found.")
    
    with open(json_filepath, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        
    if not isinstance(data, list):
        raise ValueError("Invalid data format: JSON root must be a list of records.")
        
    if not data:
        raise ValueError("The JSON file is empty. No data to save.")

    # Extract CSV headers from the keys of the first dictionary
    fieldnames = list(data[0].keys())

    # Write data to CSV file
    with open(csv_filepath, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def load(csv_filepath: str) -> list:
    """
    Loads data from a CSV file into a list of dictionaries with proper data types.
    Args:
        csv_filepath (str): Path to the source CSV file.
    Returns:
        list: A list of dictionaries representing the records.
    Raises:
        FileNotFoundError: If the CSV file does not exist.
    """
    if not os.path.exists(csv_filepath):
        raise FileNotFoundError(f"The CSV file '{csv_filepath}' was not found.")

    data = []
    with open(csv_filepath, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            # Convert specific fields to their proper data types
            if "User ID" in row:
                row["User ID"] = int(row["User ID"])
            
            data.append(row)
            
    return data

def query(df, category=None, action=None):
    """
    Filters the DataFrame based on category and/or action.
    Case-insensitive and matches exact string or partial matches.
    """
    filtered_df = df.copy()
    
    if category:
        filtered_df = filtered_df[
            filtered_df['Categories'].str.lower() == category.strip().lower()
        ]
        
    if action:
        filtered_df = filtered_df[
            filtered_df['Actions'].str.lower() == action.strip().lower()
        ]
        
    return filtered_df

# print("=== Data Filter System ===")
# print("Leave a field blank and press Enter to skip filtering by that criteria.\n")
    
# cat_input = input("Enter Category (e.g., harassment, spam, hate, violent, sexual, self harm): ").strip()
# act_input = input("Enter Action (e.g., P1, P2, P3, P4): ").strip()
    
# category = cat_input if cat_input else None
# action = act_input if act_input else None
    
# results = query(df, category=category, action=action)
    
# print("\n--- Filter Results ---")
# if results.empty:
#     print("No matching records found.")
# else:
#     print(results.to_string(index=False))
