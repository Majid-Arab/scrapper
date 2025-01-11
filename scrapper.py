import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
import os
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from itertools import product
import logging

# Set up logging for API calls
logging.basicConfig(filename='api_calls.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Global dictionaries for logging
search_parameter_counts = {
    'hospital': 0,
    'doctor': 0,
    'pharmacy': 0,
    'dentist': 0
}

grid_search_counts = {}

# Load environment variables
load_dotenv()

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points on earth in meters."""
    R = 6371000  # Earth's radius in meters
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def create_coverage_circle(lat, lon, radius_meters):
    """Create a circular polygon representing the coverage area of a search point."""
    # Convert radius from meters to degrees (approximate)
    radius_degrees = radius_meters / 111320
    
    # Create points for the circle
    angles = np.linspace(0, 360, 32)
    circle_points = []
    for angle in angles:
        dx = radius_degrees * cos(radians(angle))
        dy = radius_degrees * sin(radians(angle))
        circle_points.append((lon + dx, lat + dy))
    
    return Polygon(circle_points)

def validate_coverage(points, search_radius, polygon):
    """Validate coverage and identify gaps in the search area."""
    # Create coverage circles for all points
    coverage_circles = [create_coverage_circle(lat, lon, search_radius) 
                       for lat, lon in points]
    
    # Combine all coverage circles
    total_coverage = unary_union(coverage_circles)
    
    # Find uncovered areas
    uncovered = polygon.difference(total_coverage)
    
    return uncovered, total_coverage

def generate_optimized_grid(polygon, search_radius, overlap_factor=1.4):
    """Generate optimized grid points with validation and gap filling."""
    # Initial grid generation
    bounds = polygon.bounds
    radius_degrees = search_radius / 111320  # Convert meters to degrees
    step = radius_degrees * overlap_factor
    
    # Generate initial points
    x_coords = np.arange(bounds[0], bounds[2], step)
    y_coords = np.arange(bounds[1], bounds[3], step)
    
    points = []
    for x, y in product(x_coords, y_coords):
        point = Point(x, y)
        if polygon.contains(point):
            points.append((y, x))  # Convert to (lat, lon)
    
    # Validate coverage and add additional points if needed
    uncovered, coverage = validate_coverage(points, search_radius, polygon)
    
    # If there are gaps, add additional points
    if not uncovered.is_empty:
        if isinstance(uncovered, MultiPolygon):
            gap_centroids = [gap.centroid for gap in uncovered.geoms]
        else:
            gap_centroids = [uncovered.centroid]
            
        for centroid in gap_centroids:
            points.append((centroid.y, centroid.x))
    
    return points

def visualize_coverage(polygon, points, search_radius, output_file='coverage_map.png'):
    """Visualize the search coverage and any potential gaps."""
    fig, ax = plt.subplots(figsize=(15, 15))
    
    # Plot the main polygon
    if isinstance(polygon, MultiPolygon):
        for geom in polygon.geoms:
            x, y = geom.exterior.xy
            ax.plot(x, y, 'k-', linewidth=2)
    else:
        x, y = polygon.exterior.xy
        ax.plot(x, y, 'k-', linewidth=2)
    
    # Plot coverage circles
    for lat, lon in points:
        circle = create_coverage_circle(lat, lon, search_radius)
        x, y = circle.exterior.xy
        ax.plot(x, y, 'b-', alpha=0.3)
        ax.plot(lon, lat, 'r.', markersize=5)
    
    ax.set_aspect('equal')
    plt.title('Search Coverage Map')
    plt.savefig(output_file)
    plt.close()

def fetch_places(api_key, location, radius=2000, place_type='hospital', grid_index=None, search_index=None, log_file='api_calls.log'):
    """Fetch places from Google Places API and log the number of customers, hits per search, and hits per grid."""
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # Optimize search parameters based on place type
    keyword_map = {
        'hospital': 'hospital OR medical center OR clinic OR welfare',
        'doctor': 'doctor OR physician OR medical clinic',
        'pharmacy': 'pharmacy OR chemist OR drugstore OR medical store',
        'dentist': 'dentist OR dental clinic'
    }
    
    # Ensure location coordinates are properly formatted
    lat, lon = location  # Unpack the location tuple
    
    params = {
        'key': api_key,
        'location': f"{lat},{lon}",  # Use unpacked coordinates
        'radius': radius,
        'type': place_type,
        'keyword': keyword_map.get(place_type, ''),
        'language': 'en'
    }
    
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") != "OK" and data.get("status") != "ZERO_RESULTS":
                print(f"API Error: {data.get('error_message', 'Unknown error')} (Status: {data.get('status')})")
            places = data.get("results", [])
            
            # Log the API hit for this search location, type, and the number of customers found
            with open(log_file, 'a') as log:
                # Log for API hits per grid (index-wise)
                log.write(f"Grid #{grid_index} | Search #{search_index} | API Hit: {place_type} at ({lat:.6f}, {lon:.6f}) - Found: {len(places)} customers\n")
            
            return places
        else:
            print(f"API Request Failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error in API call: {e}")
        return []

def scrape_medical_businesses(api_key, shapefile_path, output_file, log_file='api_calls.log'):
    """Main function to scrape medical businesses and log API hits per search, grid, and customer count."""
    # Load and process shapefile
    gdf = gpd.read_file(shapefile_path)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
    
    polygon = gdf.geometry.unary_union
    print("Shapefile loaded. Generating optimized search points...")
    
    # Define search parameters
    search_types = [
        ('hospital', 2000),
        ('doctor', 1500),
        ('pharmacy', 1000),
        ('dentist', 1000)
    ]
    
    # Generate optimized search points
    all_points = []
    for _, radius in search_types:
        points = generate_optimized_grid(polygon, radius)
        all_points.extend(points)
    
    # Remove duplicates while preserving order
    all_points = list(dict.fromkeys(map(tuple, all_points)))
    print(f"Generated {len(all_points)} optimized search points.")
    
    # Visualize coverage
    visualize_coverage(polygon, all_points, min(radius for _, radius in search_types))
    print("Coverage map generated as 'coverage_map.png'")
    
    # Perform searches
    all_places = []
    processed_ids = set()
    api_calls = 0
    grid_hits = 0  # Total API hits per grid
    
    # Loop over grid points and perform searches for each type
    for grid_index, point in enumerate(all_points):
        # Initialize API call counters per search
        search_hits = {place_type: 0 for place_type, _ in search_types}
        
        for search_index, (place_type, radius) in enumerate(search_types):
            try:
                api_calls += 1
                # Convert point coordinates to string for logging
                point_str = f"({point[0]:.6f}, {point[1]:.6f})"
                print(f"API Call #{api_calls}: {place_type} at {point_str}")
                
                grid_hits += 1
                # Call fetch_places with grid and search indices
                places = fetch_places(api_key, point, radius, place_type, grid_index, search_index, log_file)
                
                for place in places:
                    place_id = place.get("place_id")
                    if place_id and place_id not in processed_ids:
                        processed_ids.add(place_id)
                        
                        location = place.get("geometry", {}).get("location", {})
                        lat = location.get("lat")
                        lng = location.get("lng")
                        
                        if lat and lng and polygon.contains(Point(lng, lat)):
                            # Get brick name
                            brick_name = "Unknown"
                            location_point = Point(lng, lat)
                            for _, row in gdf.iterrows():
                                if row.geometry.contains(location_point):
                                    brick_name = row.get('name', 'Unknown')
                                    break
                            
                            all_places.append({
                                'Place ID': place_id,
                                'Brick Name': brick_name,
                                'Business Name': place.get('name'),
                                'Latitude': lat,
                                'Longitude': lng,
                                'Type': place_type,
                                'Status': place.get('business_status', 'UNKNOWN'),
                                'Address': place.get('vicinity', ''),
                                'Rating': place.get('rating', 'N/A'),
                                'User Ratings': place.get('user_ratings_total', 0)
                            })
                            
                # Log the total number of API hits for each search type (per search)
                search_hits[place_type] += 1
            except Exception as e:
                print(f"Error processing point at {point}: {e}")
                continue
        
        # Log the number of API hits per grid
        with open(log_file, 'a') as log:
            log.write(f"\nGrid #{grid_index} - Total API Hits: {grid_hits}\n")
            for place_type, _ in search_types:
                log.write(f"  {place_type.capitalize()} Search Hits: {search_hits[place_type]}\n")
    
    # Final log after all searches
    print(f"\nTotal API calls made: {grid_hits}")
    print(f"\nTotal API calls made: {api_calls}")
    print(f"Total unique places found: {len(all_places)}")
    
    # Save results
    df = pd.DataFrame(all_places)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data saved to {output_file}")

# Usage
if __name__ == "__main__":
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    shapefile_path = "lahoreShp/Shahdara/Shahdara.shp"
    output_file = "Shahdara.csv"
    
    scrape_medical_businesses(api_key, shapefile_path, output_file)