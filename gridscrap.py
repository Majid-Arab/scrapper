import requests

# Function to generate grid points
def generate_grid(bbox, step):
    min_lat, max_lat, min_lng, max_lng = bbox
    latitudes = []
    longitudes = []
    
    # Generate latitude and longitude points
    lat = min_lat
    while lat <= max_lat:
        lng = min_lng
        while lng <= max_lng:
            latitudes.append(lat)
            longitudes.append(lng)
            lng += step  # Move to the next longitude
        lat += step  # Move to the next latitude
    
    # Combine into list of tuples
    return [(lat, lng) for lat, lng in zip(latitudes, longitudes)]

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

# Generate grid points
grid_points = generate_grid(karachi_bbox, grid_step)

# Fetch data for each grid
all_places = []
for point in grid_points:
    print(f"Fetching data for grid center: {point}")
    places = fetch_places(api_key, point)
    all_places.extend(places)

# Output data (you can save this to a file or process further)
print(f"Total places found: {len(all_places)}")
