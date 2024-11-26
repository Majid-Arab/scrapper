import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def test_google_places_api():
    # Your API key
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")  # Replace with your actual API key if needed
    location = "24.8607,67.0011"  # Karachi coordinates
    radius = 1000  # 1 km radius for testing
    type_filter = "hospital"  # Example type filter
    
    # Base URL
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # Request parameters
    params = {
        'key': api_key,
        'location': location,
        'radius': radius,
        'type': type_filter
    }
    
    # Send request
    response = requests.get(base_url, params=params)
    
    # Print the response status and content
    if response.status_code == 200:
        print("Success! Here is the data:")
        print(response.json())  # Print the data returned by the API
    else:
        print(f"Error: Status code {response.status_code}")
        print(response.json())  # Print error details if any

# Call the function
test_google_places_api()
