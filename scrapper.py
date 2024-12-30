import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import requests
from dotenv import load_dotenv
import os
from sklearn.cluster import DBSCAN
import numpy as np

# def cluster_close_coordinates(all_places, eps=0.001):
#     """
#     Clusters places based on their coordinates and selects one representative from each cluster.
#     Args:
#         all_places (list): List of place dictionaries with 'Latitude' and 'Longitude'.
#         eps (float): Maximum distance between coordinates to consider them part of the same cluster.
#     Returns:
#         list: Deduplicated list of places.
#     """
#     # Extract coordinates
#     coords = np.array([[place['Latitude'], place['Longitude']] for place in all_places])
    
#     # Apply DBSCAN clustering
#     db = DBSCAN(eps=eps, min_samples=1).fit(coords)
#     labels = db.labels_
    
#     # Group places by cluster label and pick the first one as representative
#     clustered_places = []
#     for label in set(labels):
#         cluster = [all_places[i] for i in range(len(labels)) if labels[i] == label]
#         clustered_places.append(cluster[0])  # Pick the first place in each cluster

#     return clustered_places


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
def fetch_places(api_key, location, radius=3000, type_filter='hospital', raw_response=False):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'key': api_key,
        'location': f"{location[0]},{location[1]}",
        'radius': radius,
        'type': type_filter,
    }
    try:
        response = requests.get(base_url, params=params)
        if raw_response:
            return response.text

        if response.status_code == 200:
            data = response.json()
            if data.get("status") != "OK":
                print(f"API Error for location {location}, type {type_filter}: {data.get('error_message', 'Unknown error')} (Status: {data.get('status')})")
            return data.get("results", [])
        else:
            print(f"API Request Failed for location {location}, type {type_filter}: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching data for location {location}, type {type_filter}: {e}")
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

def deduplicate_places(all_places):
    """
    Deduplicates places based on Place ID and Business Name.
    Args:
        all_places (list): List of place dictionaries.
    Returns:
        list: Deduplicated list of places.
    """
    df = pd.DataFrame(all_places)
    
    # Remove duplicates based on 'Place ID' and 'Business Name'
    deduplicated_df = df.drop_duplicates(subset=['Place ID', 'Business Name'], keep='first')
    
    # Convert back to list of dictionaries
    return deduplicated_df.to_dict(orient='records')


# Function to load the GeoDataFrame with Brick Names
def load_bricks_from_shapefile(shapefile_path):
    gdf = gpd.read_file(shapefile_path)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")  # Ensure CRS is WGS84 (lat/lng)
    return gdf  # Return the GeoDataFrame instead of merging into one geometry

# Function to get the Brick Name for a given point
def get_brick_name(lat, lng, gdf):
    point = Point(lng, lat)  # Create a Point from lat/lng
    for _, row in gdf.iterrows():  # Iterate over each polygon in the GeoDataFrame
        if row.geometry and row.geometry.is_valid:  # Check if geometry exists and is valid
            if row.geometry.contains(point):  # Check if the point is inside the polygon
                return row['name']  # Replace 'BrickName' with the actual column name in your shapefile
    return None  # Return None if no matching polygon is found


# Main function to scrape businesses within a polygon
def scrape_medical_businesses(api_key, shapefile_path, output_file):
    if not api_key:
        raise ValueError("API Key not found. Check your .env file.")

    # Load the GeoDataFrame with Brick Names
    gdf = load_bricks_from_shapefile(shapefile_path)
    print("Shapefile loaded. Generating grid points...")

    # Generate grid points dynamically
    polygon = gdf.geometry.unary_union  # Combine all polygons into one for grid generation
    grid_points = generate_grid_points(polygon, step=0.01)  # Adjust step for density
    print(f"Generated {len(grid_points)} grid points.")

    medical_types = ['hospital', 'doctor', 'pharmacy', 'dentist', 'medical_store', 'chemist', 'clinic', 'lab', 'medical_clinic', 'physiotherapist']
    all_places = []  # Initialize empty list for all places
    processed_ids = set()

    for type_filter in medical_types:
        for point in grid_points:
            try:
                # Fetch the brick name for the current point
                brick_name = get_brick_name(point[0], point[1], gdf) or "Unknown"
                print(f"Fetching {type_filter} data for grid center: {point} in brick: {brick_name}")

                # Fetch places from API
                places = fetch_places(api_key, point, radius=2000, type_filter=type_filter)

                for place in places:
                    place_id = place.get("place_id")
                    if place_id and place_id not in processed_ids:
                        processed_ids.add(place_id)

                        lat = place.get("geometry", {}).get("location", {}).get("lat")
                        lng = place.get("geometry", {}).get("location", {}).get("lng")

                        if lat is not None and lng is not None:
                            if is_within_polygon(lat, lng, polygon):
                                all_places.append({
                                    'Place ID': place_id,
                                    'Brick Name': brick_name,
                                    'Business Name': place.get('name'),
                                    'Latitude': lat,
                                    'Longitude': lng,
                                    'Status': place.get('business_status', 'UNKNOWN'),
                                    'Category': ', '.join(place.get('types', [])),
                                })
            except Exception as e:
                print(f"Error while processing point {point} in brick {brick_name}: {e}")
                continue

    # Deduplicate results
    all_places = deduplicate_places(all_places)

    # Save results
    save_to_csv(all_places, output_file)


# Replace these with your actual API key and shapefile path
api_key = os.getenv("GOOGLE_PLACES_API_KEY")  # Replace with your actual API key if needed
shapefile_path = "shp/SujhaniBricks.shp"  # Replace with your shapefile path
output_file = "SurjhaniData.csv"

# Run the scraping process
scrape_medical_businesses(api_key, shapefile_path, output_file)
