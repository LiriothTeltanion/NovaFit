"""Configuration and constants for NovaFit

This module contains all configuration settings, constants, and utility
classes used throughout the application.
"""

import os
import json
from pathlib import Path

# =============================================================================
# SSL CONFIGURATION - Fix SSL certificate issues
# =============================================================================
def configure_ssl():
    """Configure SSL to avoid certificate verification issues.
    
    This function disables SSL verification and removes problematic
    environment variables that may interfere with HTTPS requests.
    Useful when dealing with corporate proxies or development environments.
    """
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    
    # Remove problematic SSL environment variables set by PostgreSQL
    problematic_vars = ['SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']
    for var in problematic_vars:
        if var in os.environ:
            problematic_path = os.environ[var]
            if 'PostgreSQL' in problematic_path or not os.path.exists(problematic_path):
                del os.environ[var]
    
    # Try to disable SSL warnings
    try:
        import urllib3
        urllib3.disable_warnings()
    except ImportError:
        pass

# Configure SSL on module import
configure_ssl()

# =============================================================================
# FILE PATHS - Easy to modify settings
# =============================================================================
# These constants define where NovaFit stores its data files
# You can change these paths if you want to store data elsewhere

DATA_DIR = Path("./data")                           # Folder for all data files
DB_PATH = DATA_DIR / "novafit.db"                  # SQLite database file
EXPORT_PATH = DATA_DIR / "novafit_export.json"     # Default JSON export file
CSV_EXPORT_PATH = DATA_DIR / "novafit_export.csv"  # Default CSV export file
CONFIG_PATH = DATA_DIR / "config.json"             # User settings file

# =============================================================================
# WEATHER CITIES - Coordinates for weather lookup
# =============================================================================
# City coordinates (latitude, longitude) for weather API requests
# Add more cities here if needed

CITY_COORDS = {
    "beersheba": (31.2529, 34.7915),
    "tel aviv": (32.0853, 34.7818),
    "jerusalem": (31.7683, 35.2137),
    "haifa": (32.7940, 34.9896),
    "eilat": (29.5581, 34.9482),
}

# =============================================================================
# TERMINAL COLORS - ANSI color codes for CLI
# =============================================================================

class Colors:
    """ANSI color codes for terminal text formatting.
    
    These codes add colors to text in terminal/console output.
    Works on most modern terminals (Windows Terminal, Linux, macOS).
    
    Usage:
        print(f"{Colors.GREEN}Success!{Colors.ENDC}")
    """
    HEADER = '\033[95m'    # Purple/Magenta
    BLUE = '\033[94m'      # Blue
    CYAN = '\033[96m'      # Cyan
    GREEN = '\033[92m'     # Green
    WARNING = '\033[93m'   # Yellow
    FAIL = '\033[91m'      # Red
    ENDC = '\033[0m'       # Reset to default
    BOLD = '\033[1m'       # Bold text
    UNDERLINE = '\033[4m'  # Underlined text

# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================

def load_config():
    """Load user configuration from JSON file.
    
    Returns a dictionary with user preferences. If the config file
    doesn't exist or is corrupted, returns default values.
    
    Returns:
        dict: Configuration dictionary with keys:
            - step_goal: Daily step goal (default: 10000)
            - water_goal: Daily water goal in liters (default: 2.0)
            - default_city: Default city for weather (default: "tel aviv")
            - theme: GUI theme (default: "dark")
            - show_achievements: Show achievement popups (default: True)
    """
    defaults = {
        "step_goal": 10000,
        "water_goal": 2.0,
        "default_city": "tel aviv",
        "theme": "dark",
        "show_achievements": True
    }
    
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                defaults.update(config)
        except Exception:
            pass  # Return defaults if file is corrupted
    
    return defaults


def save_config(config):
    """Save user configuration to JSON file.
    
    Creates the data directory if it doesn't exist and writes
    the configuration dictionary to config.json.
    
    Args:
        config (dict): Configuration dictionary to save
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        DATA_DIR.mkdir(exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


# =============================================================================
# GLOBAL CONFIGURATION INSTANCE
# =============================================================================
# This is loaded once when the module is imported
CONFIG = load_config()
