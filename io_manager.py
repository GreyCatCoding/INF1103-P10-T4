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

# Pre-compile slang pattern
sorted_slang = sorted(SLANG_DICT.keys(), key=len, reverse=True)
SLANG_PATTERN = re.compile(
    r'\b(' + '|'.join(map(re.escape, sorted_slang)) + r')\b', 
    flags=re.IGNORECASE
)
