import requests

def get_distances(user_lat, user_lon, shop_locations, api_key):
    """
    Call Google Maps Distance Matrix API to calculate distances.
    
    Args:
        user_lat (float): Latitude of the user.
        user_lon (float): Longitude of the user.
        shop_locations (list): List of (latitude, longitude) tuples for shops.
        api_key (str): Google Maps API key.
    
    Returns:
        list: List of distances in meters, ordered by the shop locations.
    """
    origins = f"{user_lat},{user_lon}"
    destinations = "|".join([f"{lat},{lon}" for lat, lon in shop_locations])

    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origins}&destinations={destinations}&key={api_key}"
    )
    response = requests.get(url)
    data = response.json()

    if data['status'] != "OK":
        raise Exception(f"Google API error: {data['status']}")

    distances = []
    for row in data['rows'][0]['elements']:
        if row['status'] == "OK":
            distances.append(row['distance']['value'])  # Distance in meters
        else:
            distances.append(float('inf'))  # Unreachable location

    return distances
