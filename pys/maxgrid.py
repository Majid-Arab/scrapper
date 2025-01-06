import requests
import pandas as pd

# Function to generate grid points
def generate_grid(bbox, step, max_grids=20):
    min_lat, max_lat, min_lng, max_lng = bbox
    grid_points = []
    count = 0  # Counter to track number of grids generated
    
    # Generate latitude and longitude points
    lat = min_lat
    while lat <= max_lat:
        lng = min_lng
        while lng <= max_lng:
            grid_points.append((lat, lng))
            count += 1
            if count >= max_grids:  # Stop once we reach max_grids
                return grid_points
            lng += step  # Move to the next longitude
        lat += step  # Move to the next latitude

    return grid_points

# Function to fetch data from Google Places API
def fetch_places(api_key, location, radius=2000, type_filter='hospital'):
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'key': api_key,
        'location': f"{location[0]},{location[1]}",
        'radius': radius,
        'type': type_filter,
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Your API key
api_key = "YOUR_GOOGLE_PLACES_API_KEY"  # Replace with your actual key

# Karachi's bounding box and grid step size
karachi_bbox = (24.75, 25.45, 66.60, 67.10)  # (min_lat, max_lat, min_lng, max_lng)
grid_step = 0.018  # ~2 km radius

# Generate the first 20 grid points
grid_points = generate_grid(karachi_bbox, grid_step, max_grids=20)

# Fetch data for each grid and store results
all_places = []
for point in grid_points:
    print(f"Fetching data for grid center: {point}")
    places = fetch_places(api_key, point)
    
    # Process and append place details
    for place in places:
        all_places.append({
            'Name': place.get("name"),
            'Latitude': place.get("geometry", {}).get("location", {}).get("lat"),
            'Longitude': place.get("geometry", {}).get("location", {}).get("lng"),
            'Category': ", ".join(place.get("types", [])),
            'Status': place.get("business_status", 'UNKNOWN'),
            'Grid Center': f"{point[0]},{point[1]}"
        })

# Save the data to an Excel file
df = pd.DataFrame(all_places)
output_path = "medical_businesses_sample.xlsx"  # Desired output file path
df.to_excel(output_path, index=False, engine='openpyxl')

print(f"Data saved to {output_path}")
