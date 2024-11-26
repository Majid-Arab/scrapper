import pandas as pd
from geopy.geocoders import Nominatim

def address_to_coordinates(city, area, store_name):
    address = f"{store_name}, {area}, {city}"
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None

# Read store data from Excel
excel_file_path = 'path/to/your/excel/file.xlsx'  # Replace with the actual path
store_data = pd.read_excel(excel_file_path)

# Create empty lists to store results
latitudes = []
longitudes = []

# Iterate over rows in the store data
for index, row in store_data.iterrows():
    city = row['City']  # Replace 'City' with the actual column name in your Excel sheet
    area = row['Area']  # Replace 'Area' with the actual column name in your Excel sheet
    store_name = row['StoreName']  # Replace 'StoreName' with the actual column name in your Excel sheet
    
    # Call the function to get coordinates
    coordinates = address_to_coordinates(city, area, store_name)
    
    if coordinates:
        # Store the coordinates in the respective lists
        latitudes.append(coordinates[0])
        longitudes.append(coordinates[1])
    else:
        # Handle cases where coordinates are not found
        latitudes.append(None)
        longitudes.append(None)

# Add latitude and longitude columns to the original store data
store_data['Latitude'] = latitudes
store_data['Longitude'] = longitudes

# Save the updated store data to a new Excel file
output_excel_path = 'path/to/your/output/file.xlsx'  # Replace with the desired output path
store_data.to_excel(output_excel_path, index=False)
