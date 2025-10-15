"""Weather integration for NovaFit

This module provides weather information using the Open-Meteo API.
Supports multiple Israeli cities and includes comprehensive error handling.
"""

import json
from typing import Dict, Optional, List

try:
    import requests
except ImportError:
    requests = None

from .config import CITY_COORDS, Colors

# =============================================================================
# WEATHER DATA RETRIEVAL
# =============================================================================

def get_weather(city: str) -> Dict[str, any]:
    """Fetch current weather data using Open-Meteo API.
    
    Retrieves temperature and humidity for the specified city.
    Uses Open-Meteo free weather API (no API key required).
    
    Args:
        city (str): City name (case-insensitive)
                   Supported: beersheba, tel aviv, jerusalem, haifa, eilat
        
    Returns:
        dict: Weather data with keys:
            - temp: Temperature in Celsius (or "N/A")
            - humidity: Relative humidity percentage (or "N/A")
            - windspeed: Wind speed in km/h (optional)
            - weathercode: WMO weather code (optional)
            - source: Data source or error message
            - status: Status code (success, api_error, timeout, etc.)
            
    Example:
        >>> weather = get_weather("tel aviv")
        >>> print(f"{weather['temp']}°C, {weather['humidity']}% humidity")
        24°C, 65% humidity
    """
    # Check if requests is available
    if requests is None:
        return {
            "temp": "N/A",
            "humidity": "N/A",
            "source": "requests library not installed",
            "status": "library_error"
        }
    
    # Get coordinates for city (case-insensitive)
    city_key = city.lower().strip()
    
    if city_key not in CITY_COORDS:
        return {
            "temp": "N/A",
            "humidity": "N/A",
            "source": f"Unknown city: {city}",
            "status": "invalid_city"
        }
    
    lat, lon = CITY_COORDS[city_key]
    
    try:
        # Open-Meteo API endpoint
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "hourly": "relative_humidity_2m"
        }
        
        # Make request with timeout (SSL verification disabled for compatibility)
        response = requests.get(url, params=params, timeout=10, verify=False)
        
        # Check response status
        if response.status_code != 200:
            return {
                "temp": "N/A",
                "humidity": "N/A",
                "source": f"API Error {response.status_code}",
                "status": "api_error"
            }
        
        # Parse JSON response
        data = response.json()
        weather = data.get("current_weather", {})
        
        # Extract temperature and wind data
        temperature = weather.get("temperature", "N/A")
        windspeed = weather.get("windspeed", "N/A")
        weathercode = weather.get("weathercode", 0)
        
        # Extract humidity (from hourly data, first hour as approximation)
        humidity = 45  # Default fallback
        if "hourly" in data and "relative_humidity_2m" in data["hourly"]:
            humidity_data = data["hourly"]["relative_humidity_2m"]
            if humidity_data and len(humidity_data) > 0:
                humidity = humidity_data[0]
        
        return {
            "temp": temperature,
            "humidity": humidity,
            "windspeed": windspeed,
            "weathercode": weathercode,
            "source": "Open-Meteo API",
            "status": "success"
        }
        
    except requests.exceptions.Timeout:
        return {
            "temp": "N/A",
            "humidity": "N/A",
            "source": "Request timeout (API slow to respond)",
            "status": "timeout"
        }
    except requests.exceptions.ConnectionError:
        return {
            "temp": "N/A",
            "humidity": "N/A",
            "source": "Network connection error",
            "status": "connection_error"
        }
    except requests.exceptions.RequestException as e:
        return {
            "temp": "N/A",
            "humidity": "N/A",
            "source": f"Network error: {str(e)}",
            "status": "network_error"
        }
    except json.JSONDecodeError:
        return {
            "temp": "N/A",
            "humidity": "N/A",
            "source": "Invalid API response (JSON decode error)",
            "status": "json_error"
        }
    except Exception as e:
        return {
            "temp": "N/A",
            "humidity": "N/A",
            "source": f"Unexpected error: {str(e)}",
            "status": "general_error"
        }


# =============================================================================
# WEATHER DISPLAY FORMATTING
# =============================================================================

def format_weather_display(city: str, weather: Dict) -> str:
    """Format weather data for terminal display.
    
    Creates a nicely formatted weather report with emojis and colors.
    
    Args:
        city (str): City name
        weather (dict): Weather data from get_weather()
        
    Returns:
        str: Formatted weather string with colors and emojis
    """
    # Weather emoji mapping (WMO Weather codes)
    weather_emojis = {
        0: "☀️",   # Clear sky
        1: "🌤️",   # Mainly clear
        2: "⛅",   # Partly cloudy
        3: "☁️",   # Overcast
        45: "🌫️",  # Fog
        48: "🌫️",  # Depositing rime fog
        51: "🌦️",  # Light drizzle
        53: "🌧️",  # Moderate drizzle
        55: "🌧️",  # Dense drizzle
        61: "🌧️",  # Slight rain
        63: "🌧️",  # Moderate rain
        65: "🌧️",  # Heavy rain
        71: "🌨️",  # Slight snow
        73: "🌨️",  # Moderate snow
        75: "🌨️",  # Heavy snow
        95: "⛈️",  # Thunderstorm
        96: "⛈️",  # Thunderstorm with slight hail
        99: "⛈️"   # Thunderstorm with heavy hail
    }
    
    # Get weather emoji
    weathercode = weather.get('weathercode', 0)
    emoji = weather_emojis.get(weathercode, "🌡️")
    
    # Build formatted output
    if weather['status'] == 'success':
        output = f"""
{Colors.HEADER}════════════════════════════════════════{Colors.ENDC}
{Colors.BOLD}  {emoji} Weather for {city.title()}{Colors.ENDC}
{Colors.HEADER}════════════════════════════════════════{Colors.ENDC}
{Colors.CYAN}🌡️  Temperature:{Colors.ENDC} {Colors.YELLOW}{weather['temp']}°C{Colors.ENDC}
{Colors.CYAN}💧 Humidity:{Colors.ENDC}    {Colors.BLUE}{weather['humidity']}%{Colors.ENDC}"""
        
        # Add wind speed if available
        if 'windspeed' in weather and weather['windspeed'] != "N/A":
            output += f"\n{Colors.CYAN}💨 Wind Speed:{Colors.ENDC}  {Colors.GREEN}{weather['windspeed']} km/h{Colors.ENDC}"
        
        output += f"\n{Colors.HEADER}════════════════════════════════════════{Colors.ENDC}"
        return output
    else:
        # Error case
        return f"""
{Colors.WARNING}⚠️  Weather data unavailable for {city.title()}{Colors.ENDC}
{Colors.FAIL}Error: {weather['source']}{Colors.ENDC}

Troubleshooting:
  • Check your internet connection
  • Verify firewall/proxy settings
  • Try again in a moment
"""


def get_weather_emoji(weathercode: int) -> str:
    """Get emoji for weather code.
    
    Args:
        weathercode (int): WMO weather code
        
    Returns:
        str: Emoji representing the weather condition
    """
    weather_emojis = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌦️", 53: "🌧️", 55: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️",
        71: "🌨️", 73: "🌨️", 75: "🌨️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return weather_emojis.get(weathercode, "🌡️")


# =============================================================================
# CITY MANAGEMENT
# =============================================================================

def get_available_cities() -> List[str]:
    """Get list of supported cities.
    
    Returns:
        list: List of city names (lowercase)
    """
    return list(CITY_COORDS.keys())


def show_available_cities() -> None:
    """Display list of available cities with formatting."""
    cities = get_available_cities()
    
    print(f"\n{Colors.CYAN}📍 Available Cities:{Colors.ENDC}")
    print(f"{Colors.CYAN}{'─' * 25}{Colors.ENDC}")
    
    for i, city in enumerate(cities, 1):
        lat, lon = CITY_COORDS[city]
        print(f"  {i}. {Colors.GREEN}{city.title()}{Colors.ENDC} "
              f"{Colors.WARNING}({lat:.4f}, {lon:.4f}){Colors.ENDC}")
    
    print()


def is_valid_city(city: str) -> bool:
    """Check if city is supported.
    
    Args:
        city (str): City name (case-insensitive)
        
    Returns:
        bool: True if city is supported, False otherwise
    """
    return city.lower().strip() in CITY_COORDS


def get_city_coordinates(city: str) -> Optional[tuple]:
    """Get coordinates for a city.
    
    Args:
        city (str): City name (case-insensitive)
        
    Returns:
        tuple or None: (latitude, longitude) or None if city not found
    """
    city_key = city.lower().strip()
    return CITY_COORDS.get(city_key)


# =============================================================================
# WEATHER STATISTICS
# =============================================================================

def categorize_temperature(temp: float) -> str:
    """Categorize temperature into descriptive ranges.
    
    Args:
        temp (float): Temperature in Celsius
        
    Returns:
        str: Temperature category
    """
    if temp < 0:
        return "Freezing ❄️"
    elif temp < 10:
        return "Cold 🥶"
    elif temp < 20:
        return "Cool 😊"
    elif temp < 25:
        return "Comfortable 🌤️"
    elif temp < 30:
        return "Warm ☀️"
    elif temp < 35:
        return "Hot 🔥"
    else:
        return "Very Hot 🌡️"


def categorize_humidity(humidity: float) -> str:
    """Categorize humidity into descriptive ranges.
    
    Args:
        humidity (float): Relative humidity percentage
        
    Returns:
        str: Humidity category
    """
    if humidity < 30:
        return "Dry 🏜️"
    elif humidity < 50:
        return "Comfortable 😊"
    elif humidity < 70:
        return "Humid 💧"
    else:
        return "Very Humid 💦"
