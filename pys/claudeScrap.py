import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Function to load the polygon from a shapefile
def load_polygon_from_shapefile(shapefile_path):
    gdf = gpd.read_file(shapefile_path)
    polygon = gdf.geometry.iloc[0]  # Assuming the shapefile has one polygon, adjust as needed
    return polygon

# Function to check if a point is inside the polygon
def is_within_polygon(lat, lng, polygon):
    point = Point(lng, lat)  # Create point from lat/lng
    return polygon.contains(point)  # Check if point is within the polygon

# Function to fetch places from Google Places API
def fetch_places(api_key, location, radius=2000, type_filter='hospital', raw_response=False):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'key': api_key,
        'location': f"{location[0]},{location[1]}",
        'radius': radius,
        'type': type_filter,
    }
    response = requests.get(base_url, params=params)
    
    if raw_response:
        return response.text
    
    if response.status_code == 200:
        data = response.json()
        print("API Response Status:", data.get('status'))
        print("Error Message:", data.get('error_message', 'No error message'))
        return data.get('results', [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Function to save places to a CSV file
def save_to_csv(data, output_file):
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data saved to {output_file}")

# List of medical-related types to search
medical_types = [
    'hospital', 
    'doctor', 
    'pharmacy', 
    'dentist', 
    'medical_clinic', 
    'physiotherapist'
]

# Main function to scrape businesses within a polygon
def scrape_medical_businesses(api_key, shapefile_path, grid_points, output_file):
    polygon = load_polygon_from_shapefile(shapefile_path)
    unique_places = {}  # Use a dictionary to store places by unique `place_id`
    visited_points = set()
    unique_places = {}
    for place in places:
        key = (place.get('name').lower(), place.get('geometry', {}).get('location', {}).get('lat'), place.get('geometry', {}).get('location', {}).get('lng'))
        if key not in unique_places:
            unique_places[key] = place

    for point in grid_points:
        if point not in visited_points:
            visited_points.add(point)
            # Fetch and process data for this point

    for type_filter in medical_types:
        for point in grid_points:
            print(f"Fetching {type_filter} data for grid center: {point}")
            places = fetch_places(api_key, point, type_filter=type_filter)

            # Process places for each point
            for place in places:
                place_id = place.get("place_id")  # Unique identifier for each business
                if place_id not in unique_places:
                    lat = place.get("geometry", {}).get("location", {}).get("lat")
                    lng = place.get("geometry", {}).get("location", {}).get("lng")

                    # Ensure lat and lng are not None before checking polygon
                    if lat is not None and lng is not None:
                        if is_within_polygon(lat, lng, polygon):
                            unique_places[place_id] = {
                                'Business Name': place.get('name'),
                                'Latitude': lat,
                                'Longitude': lng,
                                'Status': place.get('business_status', 'UNKNOWN'),
                                'Category': ', '.join(place.get('types', [])),
                            }

    # Save unique results to CSV
    save_to_csv(list(unique_places.values()), output_file)


# Get API key from environment variables
api_key = os.getenv("GOOGLE_PLACES_API_KEY")

# Replace these with your actual shapefile path and output file
shapefile_path = "shp/testBricks.shp"  # Replace with your shapefile path
output_file = "data.csv"

# Define grid points (example; replace with actual grid logic if needed)
grid_points = [
    (25.0, 67.0),
    (24.9, 66.9),
    (24.8, 67.1)
]  # Replace with actual grid points or a generated list

# Run the scraping process
scrape_medical_businesses(api_key, shapefile_path, grid_points, output_file)