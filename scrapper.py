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
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")  # Ensure CRS is WGS84 (lat/lng)
    return gdf.geometry.unary_union  # Combine all geometries into one

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
        if data.get("status") != "OK":
            print("API Error:", data.get("error_message", "Unknown error"))
        return data.get("results", [])
    else:
        print(f"API Request Failed: {response.status_code} - {response.text}")
        return []

# Function to save places to a CSV file
def save_to_csv(data, output_file):
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data saved to {output_file}")

# Generate grid points dynamically within the polygon's bounding box
def generate_grid_points(polygon, step=0.01):
    minx, miny, maxx, maxy = polygon.bounds  # Get bounding box
    points = []
    x = minx
    while x <= maxx:
        y = miny
        while y <= maxy:
            point = Point(x, y)
            if polygon.contains(point):
                points.append((y, x))  # Append as (lat, lng)
            y += step
        x += step
    return points

# Main function to scrape businesses within a polygon
def scrape_medical_businesses(api_key, shapefile_path, output_file):
    # Check API key
    if not api_key:
        raise ValueError("API Key not found. Check your .env file.")

    # Load and prepare the polygon
    polygon = load_polygon_from_shapefile(shapefile_path)
    print("Polygon loaded. Generating grid points...")

    # Generate grid points dynamically
    grid_points = generate_grid_points(polygon, step=0.01)  # Adjust step for density
    print(f"Generated {len(grid_points)} grid points.")

    # Medical types to search
    medical_types = [
        'hospital', 
        'doctor', 
        'pharmacy', 
        'dentist', 
        'medical_clinic', 
        'physiotherapist'
    ]

    all_places = []

    for type_filter in medical_types:
        for point in grid_points:
            print(f"Fetching {type_filter} data for grid center: {point}")
            places = fetch_places(api_key, point, type_filter=type_filter)
            
            # Process places for each point
            for place in places:
                lat = place.get("geometry", {}).get("location", {}).get("lat")
                lng = place.get("geometry", {}).get("location", {}).get("lng")
                
                # Ensure lat and lng are not None before checking polygon
                if lat is not None and lng is not None:
                    if is_within_polygon(lat, lng, polygon):
                        all_places.append({
                            'Business Name': place.get('name'),
                            'Latitude': lat,
                            'Longitude': lng,
                            'Status': place.get('business_status', 'UNKNOWN'),
                            'Category': ', '.join(place.get('types', [])),
                        })

    # Save results to CSV
    save_to_csv(all_places, output_file)

# Replace these with your actual API key and shapefile path
api_key = os.getenv("GOOGLE_PLACES_API_KEY")  # Replace with your actual API key if needed
shapefile_path = "shp/testBricks.shp"  # Replace with your shapefile path
output_file = "data.csv"

# Run the scraping process
scrape_medical_businesses(api_key, shapefile_path, output_file)
