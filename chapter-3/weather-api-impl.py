import sys
import os

# Add root directory to sys.path so lib can be imported from any location
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from lib import get_current_weather

if __name__ == "__main__":
    weather = get_current_weather("Bengaluru", country_code="IN")

    print(f"City: {weather['city']}")
    print(f"Time: {weather['time']}")
    print(f"Temperature: {weather['temperature_c']}°C")
    print(f"Feels like: {weather['feels_like_c']}°C")
    print(f"Condition: {weather['condition']}")
    print(f"Humidity: {weather['humidity_percent']}%")
    print(f"Precipitation: {weather['precipitation_mm']} mm")
    print(f"Wind: {weather['wind_speed_kmh']} km/h")