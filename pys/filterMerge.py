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

# Clinic Keyword to merge usage
# merge_csv_files("Islamabad_categorized_csvs", "merged.csv", [
#     "./Abortion Clinic, Islamabad.csv",
#     "./Acupuncture Clinic, Islamabad.csv",
#     "./Clanic, Islamabad.csv",
#     "./Clenic, Islamabad.csv",
#     "./Clinic, Islamabad.csv",
#     "./Dentist, Islamabad.csv",
#     "./Doctor, Islamabad.csv",
#     "./Dr, Islamabad.csv",
#     "./Dr., Islamabad.csv",
#     "./Mental Health Clinic, Islamabad.csv",
# ])

# Hospital Keyword to merge usage
# merge_csv_files("Islamabad_categorized_csvs", "merged.csv", [
#     "./Acupuncturist, Islamabad.csv",
#     "./Addiction Treatment Center, Islamabad.csv",
#     "./Adult Day Care Center, Islamabad.csv",
#     "./Blood Bank, Islamabad.csv",
#     "./Centres, Islamabad.csv",
#     "./Chiropractor, Islamabad.csv",
#     "./Dialysis Center, Islamabad.csv",
#     "./Dispan(sary), Islamabad.csv",
#     "./Dispen(sary), Islamabad.csv",
#     "./Emergency Room, Islamabad.csv",
#     "./Eye Care, Islamabad.csv",
#     "./FinalHealth, Islamabad.csv",
#     "./Hakeem, Islamabad.csv",
#     "./Health, Islamabad.csv",
#     "./Hospetal, Islamabad.csv",
#     "./Hospital, Islamabad.csv",
#     "./Medical Center, Islamabad.csv",
#     "./Pathologist, Islamabad.csv",
#     "./Physical Therapist, Islamabad.csv",
#     "./Psychologist, Islamabad.csv",
#     "./Rehabilitation Center, Islamabad.csv",
#     "./Skin Care, Islamabad.csv",
#     "./Optometrist, Islamabad.csv",
#     "./Laboratory, Islamabad.csv",
#     "./Veterinarian, Islamabad.csv",
# ])

# Medical Store Keyword to merge usage
merge_csv_files("Islamabad_categorized_csvs", "merged.csv", [
    "./Chemist, Islamabad.csv",
    "./Dawa, Islamabad.csv",
    "./Dawakhan, Islamabad.csv",
    "./Dawakhana, Islamabad.csv",
    "./Homeo, Islamabad.csv",
    "./Khan, Islamabad.csv",
    "./Madical, Islamabad.csv",
    "./Madico, Islamabad.csv",
    "./Madicos, Islamabad.csv",
    "./Matab, Islamabad.csv",
    "./Medical Store, Islamabad.csv",
    "./Medical Supplies Store, Islamabad.csv",
    "./Medical, Islamabad.csv",
    "./Medicine, Islamabad.csv",
    "./Medico, Islamabad.csv",
    "./Medicos, Islamabad.csv",
    "./Optician, Islamabad.csv",
    "./Pharmacy, Islamabad.csv",
    "./Pharmecy, Islamabad.csv",
    "./Shop, Islamabad.csv",
    "./Store, Islamabad.csv",
    "./Stores, Islamabad.csv",
    "./StoresPharmacy, Islamabad.csv",
])