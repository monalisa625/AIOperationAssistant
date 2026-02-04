import asyncio
import os
from typing import Any, Dict, Optional

import requests


OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def _get_api_key() -> Optional[str]:
    return os.getenv("OPENWEATHER_API_KEY")


def _get_current_weather_sync(city: str, units: str = "metric") -> Dict[str, Any]:
    api_key = _get_api_key()
    if not api_key:
        return {
            "city": city,
            "error": "Missing OPENWEATHER_API_KEY environment variable.",
        }

    params = {"q": city, "appid": api_key, "units": units}
    try:
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        main = data.get("main", {})
        weather_list = data.get("weather", [])
        weather = weather_list[0] if weather_list else {}

        return {
            "city": city,
            "temperature": main.get("temp"),
            "feels_like": main.get("feels_like"),
            "humidity": main.get("humidity"),
            "description": weather.get("description"),
            "raw": data,
        }
    except requests.RequestException as exc:
        return {
            "city": city,
            "error": f"Weather API request failed: {exc}",
        }


async def get_current_weather(city: str, units: str = "metric") -> Dict[str, Any]:
    """
    Fetch current weather for a given city using the OpenWeatherMap API.

    Requires OPENWEATHER_API_KEY to be set in the environment.
    """
    return await asyncio.to_thread(_get_current_weather_sync, city, units)

