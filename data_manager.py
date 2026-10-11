# we need to have the following in json file, ID, Username, Comments, Categories, Actions
# we need to have save() function to save the json file into csv (Glenden)
# we need to have load() function to load the csv file (Glenden)
# we need to have query() function to filter the data based on categories and actions (Brian)
# we need to have error handling for file not found, invalid data, etc. (Brian)
# provide the data with datatype like int, str, list, etc. (Brian)

import csv
import json
import os

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
