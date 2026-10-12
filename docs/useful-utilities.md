# Useful Utilities

## Weather API Utility (`lib/weather_api.py`)

The `get_current_weather` function fetches real-time weather details for a provided city using the Open-Meteo Geocoding and Forecast APIs.

### Key Setup & Changes
- **Module location**: [`lib/weather_api.py`](file:///Users/koushiksadhukhan/projects/genai-apps/lib/weather_api.py) containing `get_current_weather(city: str, country_code: str = None) -> dict`.
- **Package export**: Re-exported via [`lib/__init__.py`](file:///Users/koushiksadhukhan/projects/genai-apps/lib/__init__.py) so it can be imported across any file using `from lib import get_current_weather`.
- **Standalone execution**: Both [`lib/weather_api.py`](file:///Users/koushiksadhukhan/projects/genai-apps/lib/weather_api.py) and [`chapter-3/weather-api-impl.py`](file:///Users/koushiksadhukhan/projects/genai-apps/chapter-3/weather-api-impl.py) include `if __name__ == "__main__":` blocks for direct script execution and testing.

---

### Function Signature & Output Format

```python
def get_current_weather(city: str, country_code: str = None) -> dict
```

#### Returns structured dictionary:
- `city` *(str)*: City name and country (e.g., `"Bengaluru, India"`)
- `latitude` *(float)*, `longitude` *(float)*: Geolocation coordinates
- `time` *(str)*: ISO timestamp of current weather measurement
- `temperature_c` *(float)*: Temperature in °C
- `feels_like_c` *(float)*: Apparent temperature in °C
- `humidity_percent` *(int)*: Relative humidity (%)
- `precipitation_mm` *(float)*: Precipitation level (mm)
- `wind_speed_kmh` *(float)*: Wind speed (km/h)
- `wind_direction_deg` *(int)*: Wind direction in degrees
- `is_day` *(bool)*: Boolean indicating daytime
- `condition` *(str)*: Weather condition description (e.g., `"Partly cloudy"`)

---

### Example Usage in Other Files and Functions

```python
from lib import get_current_weather

def display_weather_summary(city_name: str):
    weather = get_current_weather(city_name)
    print(f"City: {weather['city']}")
    print(f"Temperature: {weather['temperature_c']}°C")
    print(f"Condition: {weather['condition']}")

if __name__ == "__main__":
    display_weather_summary("Tokyo")
```
