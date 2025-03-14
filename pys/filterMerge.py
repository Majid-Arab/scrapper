import pandas as pd
import os
from glob import glob

def merge_csv_files(input_folder, output_file, file_list=None):
    """
    Merges multiple CSV files from a given folder into a single file.
    
    Parameters:
    - input_folder (str): The folder containing CSV files.
    - output_file (str): The name of the merged output file.
    - file_list (list, optional): Specific files to merge. If None, merges all CSVs in the folder.
    
    Returns:
    - None: Saves the merged file to disk.
    """
    # If no specific files are given, merge all CSVs in the folder
    if file_list is None:
        file_list = glob(os.path.join(input_folder, "*.csv"))
    else:
        # Ensure filenames are correct without "./"
        file_list = [os.path.join(input_folder, f.lstrip("./")) for f in file_list]

    df_list = []

    # Read and merge all CSV files
    for file in file_list:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file)
                df_list.append(df)
                print(f"Loaded: {file}")
            except Exception as e:
                print(f"Error reading {file}: {e}")
        else:
            print(f"File not found: {file}")

    if not df_list:
        print("No valid files to merge. Exiting.")
        return

    merged_df = pd.concat(df_list, ignore_index=True)

    # Save the merged file
    merged_df.to_csv(output_file, index=False)
    print(f"Merged file saved as: {output_file}")

# Example usage
merge_csv_files("categorized_csvs", "merged.csv", [
    "./Chemist, Islamabad.csv",
    "./Dawa Khan, Islamabad.csv",
    "./Dawakhan, Islamabad.csv",
    "./Madical Store, Islamabad.csv",
    "./Madico, Islamabad.csv",
    "./Madicos, Islamabad.csv",
    "./Matab, Islamabad.csv",
    "./Medical Store, Islamabad.csv",
    "./Medicine Shop, Islamabad.csv",
    "./Medicine Store, Islamabad.csv",
    "./Medico, Islamabad.csv",
    "./Medicos, Islamabad.csv",
    "./Merge Medical Stores 181021, Islamabad.csv",
    "./Merge Medical Stores, Islamabad.csv",
    "./Pharmacy, Islamabad.csv",
    "./Pharmecy, Islamabad.csv",
])
