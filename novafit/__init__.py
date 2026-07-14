"""NovaFit - Mini Health Tracker Package

A modular health tracking application with CLI and GUI interfaces.
Tracks daily health metrics: steps, water intake, calories, and mood.

Author: Kevin 'Lirioth' Cusnir
Date: October 2025
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Kevin 'Lirioth' Cusnir"
__license__ = "MIT"

# Package-level imports
from .config import CONFIG, Colors, configure_ssl
from .database import (
    init_db, add_entry, get_entry, update_entry, delete_entry,
    list_entries, get_all_entries, search_entries,
    get_dashboard_stats, get_stats_summary,
    clear_all_data, count_entries
)
from .utils import (
    validate_date, validate_positive_number, validate_steps, validate_water,
    safe_input, confirm_action,
    format_entry_display, show_progress_bar, format_number, truncate_text,
    clear_screen, print_header, print_section,
    show_help, show_welcome, show_goodbye
)
from .weather import (
    get_weather, format_weather_display, get_weather_emoji,
    get_available_cities, show_available_cities, is_valid_city, get_city_coordinates,
    categorize_temperature, categorize_humidity
)
from .export import (
    export_to_json, import_from_json,
    export_to_csv, import_from_csv,
    generate_demo_data, initialize_sample_data,
    get_export_info, validate_json_export, validate_csv_export
)

__all__ = [
    # Config
    'CONFIG',
    'Colors', 
    'configure_ssl',
    # Database
    'init_db',
    'add_entry',
    'get_entry', 
    'update_entry',
    'delete_entry',
    'list_entries',
    'get_all_entries',
    'search_entries',
    'get_dashboard_stats',
    'get_stats_summary',
    'clear_all_data',
    'count_entries',
    # Utils - Validation
    'validate_date',
    'validate_positive_number',
    'validate_steps',
    'validate_water',
    # Utils - Input
    'safe_input',
    'confirm_action',
    # Utils - Formatting
    'format_entry_display',
    'show_progress_bar',
    'format_number',
    'truncate_text',
    # Utils - Screen
    'clear_screen',
    'print_header',
    'print_section',
    # Utils - Help
    'show_help',
    'show_welcome',
    'show_goodbye',
    # Weather
    'get_weather',
    'format_weather_display',
    'get_weather_emoji',
    'get_available_cities',
    'show_available_cities',
    'is_valid_city',
    'get_city_coordinates',
    'categorize_temperature',
    'categorize_humidity',
    # Export
    'export_to_json',
    'import_from_json',
    'export_to_csv',
    'import_from_csv',
    'generate_demo_data',
    'initialize_sample_data',
    'get_export_info',
    'validate_json_export',
    'validate_csv_export',
]
