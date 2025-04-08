import pandas as pd
import os

# Load the CSV file
input_file = "Islamabad.csv"  # Replace with your CSV file path
output_folder = "categorized_csvs"
os.makedirs(output_folder, exist_ok=True)

# Read the CSV
df = pd.read_csv(input_file)

# Check if 'SearchKeyword' column exists
if "SearchKeyword" not in df.columns:
    raise ValueError("Column 'SearchKeyword' not found in the CSV file.")

# Define keyword groups
keyword_groups = {
    "hospital_related": [
        "Abortion Clinic", "Acupuncture Clinic", "Acupuncturist", "Addiction Treatment Center",
        "Adult Day Care Center", "Blood Bank", "Centres", "Chemist", "Chiropractor", "Clanic",
        "Clenic", "Clinic", "Dentist", "Dialysis Center", "Dispan(sary)", "Dispen(sary)", "Doctor",
        "Dr", "Dr.", "Emergency Room", "Eye Care", "FinalHealth", "Hakeem", "Health", "Hospetal",
        "Hospital", "Mental Health Clinic", "Pathologist", "Physical Therapist", "Psychologist",
        "Rehabilitation Center", "Skin Care", "Optometrist", "Laboratory", "Veterinarian"
    ],
    "pharmacy_related": [
        "Dawa", "Dawakhan", "Dawakhana", "Homeo", "Khan", "Madical", "Madico", "Madicos", "Matab",
        "Medical Center", "Medical Store", "Medical Supplies Store", "Medical", "Medicine", "Medico",
        "Medicos", "Optician", "Pharmacy", "Pharmecy", "Shop", "Store", "Stores", "StoresPharmacy"
    ]
}

# Convert SearchKeyword column to lowercase for easier matching
df["SearchKeyword_lower"] = df["SearchKeyword"].str.lower()

# Filter data based on hospital-related keywords
hospital_keywords_lower = [keyword.lower() for keyword in keyword_groups["hospital_related"]]
hospital_df = df[df["SearchKeyword_lower"].isin(hospital_keywords_lower)]

# Filter data based on pharmacy-related keywords
pharmacy_keywords_lower = [keyword.lower() for keyword in keyword_groups["pharmacy_related"]]
pharmacy_df = df[df["SearchKeyword_lower"].isin(pharmacy_keywords_lower)]

# Save hospital-related data to a CSV file
if not hospital_df.empty:
    hospital_output_path = os.path.join(output_folder, "hospital_related.csv")
    hospital_df.to_csv(hospital_output_path, index=False)
    print(f"Saved: {hospital_output_path}")

# Save pharmacy-related data to a CSV file
if not pharmacy_df.empty:
    pharmacy_output_path = os.path.join(output_folder, "pharmacy_related.csv")
    pharmacy_df.to_csv(pharmacy_output_path, index=False)
    print(f"Saved: {pharmacy_output_path}")

print("Categorization complete!")
