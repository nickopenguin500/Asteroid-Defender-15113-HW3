import os
import requests
from dotenv import load_dotenv
from datetime import date

# Load environment variables from .env file
load_dotenv()

def fetch_asteroid_data():
    """
    Fetches Near Earth Objects (Asteroids) for today from NASA NeoWs API.
    Returns a list of simplified asteroid dictionaries.
    """
    api_key = os.getenv("NASA_API_KEY")
    if not api_key:
        print("Error: NASA_API_KEY not found in .env file.")
        return get_dummy_data()

    # Get today's date in YYYY-MM-DD format
    today_str = date.today().strftime("%Y-%m-%d")
    
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    params = {
        "start_date": today_str,
        "end_date": today_str,
        "api_key": api_key
    }

    print(f"Fetching asteroid data for {today_str}...")

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # Raise an error for bad status codes (404, 403, etc)
        data = response.json()
        
        # The API returns a dictionary of dates. We only want 'today'.
        # Structure: data['near_earth_objects']['2025-02-06'] -> [List of objects]
        daily_objects = data.get("near_earth_objects", {}).get(today_str, [])
        
        cleaned_asteroids = []
        
        for asteroid in daily_objects:
            # Extract Diameter (Average of min/max in meters)
            min_dia = asteroid["estimated_diameter"]["meters"]["estimated_diameter_min"]
            max_dia = asteroid["estimated_diameter"]["meters"]["estimated_diameter_max"]
            avg_diameter = (min_dia + max_dia) / 2
            
            # Extract Velocity (kph)
            # Note: access [0] because 'close_approach_data' is a list
            velocity = float(asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"])
            
            obj = {
                "id": asteroid["id"],
                "name": asteroid["name"],
                "diameter": avg_diameter,
                "velocity": velocity,
                "is_hazardous": asteroid["is_potentially_hazardous_asteroid"]
            }
            cleaned_asteroids.append(obj)
            
        print(f"Successfully fetched {len(cleaned_asteroids)} asteroids.")
        return cleaned_asteroids

    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
        print("Switching to offline DUMMY data.")
        return get_dummy_data()

def get_dummy_data():
    """
    Returns hardcoded data for testing when API fails or no internet.
    """
    return [
        {"id": "1", "name": "Dummy Rock 1", "diameter": 25.0, "velocity": 20000.0, "is_hazardous": False},
        {"id": "2", "name": "Doomsday 99", "diameter": 80.0, "velocity": 55000.0, "is_hazardous": True},
        {"id": "3", "name": "Tiny Pebble", "diameter": 10.0, "velocity": 15000.0, "is_hazardous": False},
        {"id": "4", "name": "Fast Boi", "diameter": 40.0, "velocity": 80000.0, "is_hazardous": False},
        {"id": "5", "name": "Big Scary", "diameter": 100.0, "velocity": 30000.0, "is_hazardous": True},
    ]

# This block allows you to run this file directly to test it
if __name__ == "__main__":
    asteroids = fetch_asteroid_data()
    # Print the first 3 to verify
    for a in asteroids[:3]:
        print(a)