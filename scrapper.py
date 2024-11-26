import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_medical_businesses(api_key, location, radius=5000, type_filter='hospital'):
    # Base URL for the Places API Nearby Search
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # Define the parameters for the request
    params = {
        'key': api_key,
        'location': location,  # Format: "latitude,longitude"
        'radius': radius,      # Radius in meters
        'type': type_filter    # Use other types like 'doctor', 'pharmacy', etc. if needed
    }
    
    # Make the request
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        return results
    else:
        print(f"Error: {response.status_code}, {response.json()}")
        return []

# Your API key and desired location (latitude,longitude)
api_key = os.getenv("GOOGLE_PLACES_API_KEY")  # Replace with your actual API key
location = "24.8655235,67.0583741"  # Example: New York City coordinates

# Get the first 20 medical businesses (adjust 'radius' and 'type_filter' as needed)
medical_businesses = get_medical_businesses(api_key, location)

# Extract relevant details and save to a DataFrame
business_data = []
for business in medical_businesses:
    name = business.get('name')
    latitude = business.get('geometry', {}).get('location', {}).get('lat')
    longitude = business.get('geometry', {}).get('location', {}).get('lng')
    category = ", ".join(business.get('types', []))
    status = business.get('business_status', 'UNKNOWN')  # Status may include OPERATIONAL, CLOSED_TEMPORARILY, etc.
    
    business_data.append({
        'Name': name,
        'Latitude': latitude,
        'Longitude': longitude,
        'Category': category,
        'Status': status
    })

# Save to Excel
df = pd.DataFrame(business_data)
output_path = 'medical_businesses.xlsx'  # Desired output file path
df.to_excel(output_path, index=False, engine='openpyxl')

print(f"Data saved to {output_path}")
