#import necessary libraries
import pandas as pd

# Load dataset and filling missing comments with empty strings
df = pd.read_csv('test_processed.csv')
df['comments'] = df['comments'].fillna('')

# Displaying the first few rows of the DataFrame to verify loading and preprocessing
print(df.head())