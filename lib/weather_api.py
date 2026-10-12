import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_current_weather(city: str, country_code: str = None) -> dict:
    # 1) Convert city name to latitude/longitude
    geo_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    if country_code:
        geo_params["countryCode"] = country_code

    geo_response = requests.get(GEOCODING_URL, params=geo_params, timeout=10)
    geo_response.raise_for_status()
    geo_data = geo_response.json()

    if not geo_data.get("results"):
        raise ValueError(f"City not found: {city}")

    location = geo_data["results"][0]

    # 2) Get current weather using the coordinates
    weather_params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
        ]),
        "timezone": "auto",
    }

    weather_response = requests.get(WEATHER_URL, params=weather_params, timeout=10)
    weather_response.raise_for_status()
    weather_data = weather_response.json()

    current = weather_data["current"]

    return {
        "city": f'{location["name"]}, {location.get("country", "")}',
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "time": current["time"],
        "temperature_c": current["temperature_2m"],
        "feels_like_c": current["apparent_temperature"],
        "humidity_percent": current["relative_humidity_2m"],
        "precipitation_mm": current["precipitation"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "wind_direction_deg": current["wind_direction_10m"],
        "is_day": bool(current["is_day"]),
        "condition": WEATHER_CODES.get(current["weather_code"], "Unknown"),
    }


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
