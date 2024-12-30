import pandas as pd
import openpyxl

def categorize_excel(input_file: str, output_file: str, categories: dict, separate_sheets: bool = True):
    """
    Categorize data in an Excel file.

    Args:
        input_file (str): Path to the input Excel file.
        output_file (str): Path to save the categorized Excel file.
        categories (dict): Dictionary with category names as keys and lists of keywords as values.
        separate_sheets (bool): If True, separate data into different sheets by category.
                               If False, add a 'Category' column to the original data.
    """
    # Read the input Excel file
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Ensure the file has the necessary structure
    if "Name" not in df.columns:
        print("The input file must have a 'Name' column.")
        return

    # Add a category column
    df["Category"] = "Other"  # Default category
    for category, keywords in categories.items():
        mask = df["Name"].str.contains('|'.join(keywords), case=False, na=False)
        df.loc[mask, "Category"] = category

    if separate_sheets:
        # Separate data into different sheets
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            for category in categories.keys():
                category_df = df[df["Category"] == category]
                category_df.to_excel(writer, sheet_name=category, index=False)
            # Add "Other" category sheet if exists
            other_df = df[df["Category"] == "Other"]
            if not other_df.empty:
                other_df.to_excel(writer, sheet_name="Other", index=False)
        print(f"Data categorized and saved in separate sheets to {output_file}.")
    else:
        # Save the updated data with the 'Category' column
        df.to_excel(output_file, index=False)
        print(f"Data categorized with 'Category' column and saved to {output_file}.")

# Example usage
categories = {
    "Hospital": ["hospital"],
    "Pharmacy": ["pharmacy"],
    "Medical Store": ["medical store", "store"],
    "Doctor": ["doctor"],
}

categorize_excel(
    input_file="Seperated Data.xlsx",
    output_file="categorized_data.xlsx",
    categories=categories,
    separate_sheets=True  # Change to False to add a category column instead
)
