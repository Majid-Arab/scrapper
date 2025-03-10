import os
import pandas as pd

def merge_csv_files(input_folder, output_file):
    # Get all CSV files from the input folder
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    
    # Initialize an empty list to hold the dataframes
    merged_data = []
    
    for file in csv_files:
        file_path = os.path.join(input_folder, file)
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Add a new column 'Category' with the file name (without .csv extension)
        df['Category'] = file.replace('.csv', '')
        
        # Append this dataframe to the list
        merged_data.append(df)
    
    # Concatenate all dataframes into one
    final_df = pd.concat(merged_data, ignore_index=True)
    
    # Write the merged dataframe to the output CSV file
    final_df.to_csv(output_file, index=False)
    print(f'Merged CSV saved to {output_file}')

# Example usage
input_folder = 'Karachi/'  # Replace with your folder path
output_file = 'Karachi.csv'  # Replace with your desired output file path

merge_csv_files(input_folder, output_file)
