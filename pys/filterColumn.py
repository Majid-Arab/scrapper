import pandas as pd
import os

# Load the CSV file
input_file = "Islamabad.csv"  # Replace with your CSV file path
output_folder = "categorized_csvs"

# Create the output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Read the CSV file
df = pd.read_csv(input_file)

# Check if 'SearchKeyword' column exists
if "SearchKeyword" not in df.columns:
    raise ValueError("Column 'SearchKeyword' not found in the CSV file.")

# Group by 'SearchKeyword' and save each group as a separate CSV file
for keyword, group in df.groupby("SearchKeyword"):
    filename = f"{output_folder}/{keyword}.csv"
    group.to_csv(filename, index=False)
    print(f"Saved: {filename}")

print("Categorization complete!")
