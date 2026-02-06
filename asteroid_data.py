import os
import requests
import shutil
from dotenv import load_dotenv
from datetime import date

load_dotenv()

def fetch_asteroid_data(target_date=None):
    """
    Fetches Asteroids for a specific date.
    If target_date is None, uses today.
    target_date format: "YYYY-MM-DD"
    """
    api_key = os.getenv("NASA_API_KEY")
    if not api_key:
        print("Error: NASA_API_KEY not found.")
        return get_dummy_data()

    # Use input date or default to today
    if not target_date:
        target_date = date.today().strftime("%Y-%m-%d")
    
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    params = {
        "start_date": target_date,
        "end_date": target_date,
        "api_key": api_key
    }

    print(f"--- CONNECTING TO NASA GOV ---")
    print(f"Targeting Orbit Date: {target_date}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        daily_objects = data.get("near_earth_objects", {}).get(target_date, [])
        
        cleaned_asteroids = []
        for asteroid in daily_objects:
            # 1. Size
            min_dia = asteroid["estimated_diameter"]["meters"]["estimated_diameter_min"]
            max_dia = asteroid["estimated_diameter"]["meters"]["estimated_diameter_max"]
            avg_diameter = (min_dia + max_dia) / 2
            
            # 2. Physics
            close_data = asteroid["close_approach_data"][0]
            velocity = float(close_data["relative_velocity"]["kilometers_per_hour"])
            
            # 3. Miss Distance (NEW FEATURE)
            miss_km = float(close_data["miss_distance"]["kilometers"])
            
            obj = {
                "id": asteroid["id"],
                "name": asteroid["name"],
                "diameter": avg_diameter,
                "velocity": velocity,
                "miss_distance": miss_km, # <-- Storing real orbital data
                "is_hazardous": asteroid["is_potentially_hazardous_asteroid"]
            }
            cleaned_asteroids.append(obj)
            
        print(f"Radar Lock: {len(cleaned_asteroids)} Objects Detected.")
        return cleaned_asteroids

    except Exception as e:
        print(f"API Connection Failed: {e}")
        return get_dummy_data()

def fetch_apod_image(target_date=None):
    """
    Fetches APOD. 
    - If target_date is in the past, fetches that specific image.
    - If target_date is in the future (or None), fetches TODAY's image.
    """
    api_key = os.getenv("NASA_API_KEY")
    if not api_key: return None

    # Logic: Don't ask for future photos (NASA returns error)
    today_str = date.today().strftime("%Y-%m-%d")
    
    request_date = None
    if target_date:
        if target_date > today_str:
            print(f"Date {target_date} is in the future. Defaulting to Today's APOD.")
            request_date = None # API implies 'today' if date param is missing
        else:
            request_date = target_date

    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": api_key}
    if request_date:
        params["date"] = request_date
    
    print(f"Fetching Background Image ({request_date if request_date else 'TODAY'})...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("media_type") == "image":
            image_url = data.get("url")
            img_response = requests.get(image_url, stream=True)
            if img_response.status_code == 200:
                with open("background.jpg", 'wb') as f:
                    shutil.copyfileobj(img_response.raw, f)
                return "background.jpg"
    except Exception as e:
        print(f"Could not fetch APOD background: {e}")
    
    return None

def get_dummy_data():
    return [{"name": "Simulated Rock", "diameter": 50, "velocity": 20000, "miss_distance": 1000000, "is_hazardous": False}]