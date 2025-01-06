import pandas as pd

def generate_grid_with_names(bbox, step):
    """
    Generate grid points with names, latitudes, and longitudes.
    """
    min_lat, max_lat, min_lng, max_lng = bbox
    grid_data = []

    # Generate grid points with unique names
    row_index = 1
    lat = min_lat
    while lat <= max_lat:
        col_index = 1
        lng = min_lng
        while lng <= max_lng:
            # Generate grid name in "Row-Col" format
            grid_name = f"Grid-{row_index}-{col_index}"
            grid_data.append({
                "Grid Name": grid_name,
                "Latitude": round(lat, 6),
                "Longitude": round(lng, 6)
            })
            lng += step  # Move to the next longitude
            col_index += 1
        lat += step  # Move to the next latitude
        row_index += 1

    return grid_data

# Karachi's bounding box and grid step size
karachi_bbox = (24.698307388893962, 25.743251280693435, 66.62466586784075, 67.7379432267916)
grid_step = 0.018  # ~2 km

# Generate grids with names
grids = generate_grid_with_names(karachi_bbox, grid_step)

# Save grid data to a CSV file
df = pd.DataFrame(grids)
output_file = "karachi_grids1.csv"
df.to_csv(output_file, index=False)  # No need for engine='openpyxl' for CSV

print(f"Grid data saved to {output_file}")
