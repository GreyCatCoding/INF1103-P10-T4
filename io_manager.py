#import necessary libraries
import re # Regular expressions for data cleansing
import contractions # Add on Library to expand contractions in text
import pandas as pd # For Data manipulation and analysis library

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