"""Verified Open-Meteo weather integration for NovaFit."""

from __future__ import annotations

import json
from typing import Any, Optional

try:
    import requests
except ImportError:  # pragma: no cover - handled as a user-facing status
    requests = None

from .config import CITY_COORDS, Colors

WEATHER_EMOJIS = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️",
    48: "🌫️",
    51: "🌦️",
    53: "🌧️",
    55: "🌧️",
    61: "🌧️",
    63: "🌧️",
    65: "🌧️",
    71: "🌨️",
    73: "🌨️",
    75: "🌨️",
    95: "⛈️",
    96: "⛈️",
    99: "⛈️",
}


def _error(status: str, source: str) -> dict[str, Any]:
    return {
        "temp": "N/A",
        "humidity": "N/A",
        "windspeed": "N/A",
        "weathercode": 0,
        "source": source,
        "status": status,
    }


def get_weather(city: str) -> dict[str, Any]:
    """Fetch current weather using normal HTTPS certificate verification."""

    if requests is None:
        return _error("library_error", "requests library not installed")

    city_key = city.lower().strip()
    coordinates = CITY_COORDS.get(city_key)
    if coordinates is None:
        return _error("invalid_city", f"Unknown city: {city}")

    latitude, longitude = coordinates
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": True,
                "hourly": "relative_humidity_2m",
                "timezone": "auto",
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()

        current = payload.get("current_weather") or {}
        humidity_values = (payload.get("hourly") or {}).get("relative_humidity_2m") or []
        humidity = humidity_values[0] if humidity_values else "N/A"

        return {
            "temp": current.get("temperature", "N/A"),
            "humidity": humidity,
            "windspeed": current.get("windspeed", "N/A"),
            "weathercode": current.get("weathercode", 0),
            "source": "Open-Meteo API",
            "status": "success",
        }
    except requests.exceptions.Timeout:
        return _error("timeout", "Request timeout")
    except requests.exceptions.ConnectionError:
        return _error("connection_error", "Network connection error")
    except requests.exceptions.HTTPError as exc:
        code = getattr(exc.response, "status_code", "unknown")
        return _error("api_error", f"API error {code}")
    except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as exc:
        return _error("network_error", f"Weather request failed: {exc}")


def get_weather_emoji(weathercode: int) -> str:
    """Return an emoji for a WMO weather code."""

    return WEATHER_EMOJIS.get(weathercode, "🌡️")


def format_weather_display(city: str, weather: dict[str, Any]) -> str:
    """Return a terminal-friendly weather report."""

    if weather.get("status") != "success":
        return (
            f"\n{Colors.WARNING}⚠️ Weather data unavailable for "
            f"{city.title()}{Colors.ENDC}\n"
            f"{Colors.FAIL}Error: {weather.get('source', 'Unknown error')}"
            f"{Colors.ENDC}\n"
        )

    emoji = get_weather_emoji(int(weather.get("weathercode", 0)))
    lines = [
        f"{Colors.HEADER}{'═' * 40}{Colors.ENDC}",
        f"{Colors.BOLD}  {emoji} Weather for {city.title()}{Colors.ENDC}",
        f"{Colors.HEADER}{'═' * 40}{Colors.ENDC}",
        (
            f"{Colors.CYAN}🌡️ Temperature:{Colors.ENDC} "
            f"{Colors.WARNING}{weather.get('temp')}°C{Colors.ENDC}"
        ),
        (
            f"{Colors.CYAN}💧 Humidity:{Colors.ENDC} "
            f"{Colors.BLUE}{weather.get('humidity')}%{Colors.ENDC}"
        ),
    ]
    if weather.get("windspeed") != "N/A":
        lines.append(
            f"{Colors.CYAN}💨 Wind speed:{Colors.ENDC} "
            f"{Colors.GREEN}{weather.get('windspeed')} km/h{Colors.ENDC}"
        )
    lines.append(f"{Colors.HEADER}{'═' * 40}{Colors.ENDC}")
    return "\n" + "\n".join(lines)


def get_available_cities() -> list[str]:
    return list(CITY_COORDS)


def show_available_cities() -> None:
    print(f"\n{Colors.CYAN}📍 Available Cities:{Colors.ENDC}")
    for index, city in enumerate(get_available_cities(), 1):
        latitude, longitude = CITY_COORDS[city]
        print(
            f"  {index}. {Colors.GREEN}{city.title()}{Colors.ENDC} "
            f"{Colors.WARNING}({latitude:.4f}, {longitude:.4f}){Colors.ENDC}"
        )


def is_valid_city(city: str) -> bool:
    return city.lower().strip() in CITY_COORDS


def get_city_coordinates(city: str) -> Optional[tuple[float, float]]:
    return CITY_COORDS.get(city.lower().strip())


def categorize_temperature(temp: float) -> str:
    if temp < 0:
        return "Freezing ❄️"
    if temp < 10:
        return "Cold 🥶"
    if temp < 20:
        return "Cool 😊"
    if temp < 25:
        return "Comfortable 🌤️"
    if temp < 30:
        return "Warm ☀️"
    if temp < 35:
        return "Hot 🔥"
    return "Very Hot 🌡️"


def categorize_humidity(humidity: float) -> str:
    if humidity < 30:
        return "Dry 🏜️"
    if humidity < 50:
        return "Comfortable 😊"
    if humidity < 70:
        return "Humid 💧"
    return "Very Humid 💦"
