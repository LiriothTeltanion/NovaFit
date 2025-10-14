#!/usr/bin/env python3
"""NovaFit — Mini Health Tracker (CLI + GUI)"""

import argparse
import json
import sqlite3
import tkinter as tk
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from typing import Optional
import requests
from faker import Faker
import ssl
import os

# =============================================================================
# SSL CONFIGURATION - This section fixes SSL certificate issues
# =============================================================================
# Note for beginners: This section handles a technical issue with SSL certificates
# that can occur when PostgreSQL is installed. You don't need to understand this
# part to use or modify the rest of the application.

# Completely disable SSL certificate verification for requests
# This is necessary due to PostgreSQL's broken SSL certificate configuration
os.environ['PYTHONHTTPSVERIFY'] = '0'

# Remove problematic SSL environment variables set by PostgreSQL
ssl_env_vars = ['SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']
for var in ssl_env_vars:
    if var in os.environ:
        problematic_path = os.environ[var]
        if 'PostgreSQL' in problematic_path or not os.path.exists(problematic_path):
            print(f"Debug: Removing problematic {var}: {problematic_path}")
            del os.environ[var]

# Try to disable SSL warnings if urllib3 is available
try:
    import urllib3
    urllib3.disable_warnings()
except ImportError:
    pass  # urllib3 is not installed, that's fine

# =============================================================================
# END SSL CONFIGURATION
# =============================================================================

# =============================================================================
# CONFIGURATION CONSTANTS - Easy to modify settings
# =============================================================================
# These constants define where NovaFit stores its data files
# You can change these paths if you want to store data elsewhere

DATA_DIR = Path("./data")                    # Folder for all data files
DB_PATH = DATA_DIR / "novafit.db"           # SQLite database file
EXPORT_PATH = DATA_DIR / "novafit_export.json"  # Default export file
CONFIG_PATH = DATA_DIR / "config.json"      # User settings file

# Coordinates for weather lookup (latitude, longitude)
# Add more cities here if needed
CITY_COORDS = {
    "beersheba": (31.2529, 34.7915),
    "tel aviv": (32.0853, 34.7818),
    "jerusalem": (31.7683, 35.2137),
    "haifa": (32.7940, 34.9896),
    "eilat": (29.5581, 34.9482),
}

# =============================================================================
# COLOR CODES FOR TERMINAL OUTPUT
# =============================================================================
# This class defines color codes for making the CLI interface more attractive
# Beginners: You don't need to modify this unless you want different colors

class Colors:
    """ANSI color codes for terminal text formatting."""
    HEADER, BLUE, CYAN, GREEN, WARNING, FAIL, ENDC, BOLD = '\033[95m', '\033[94m', '\033[96m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m'


def load_config():
    """Load user configuration."""
    defaults = {"step_goal": 10000, "water_goal": 2.0, "default_city": "beersheba", "theme": "light", "show_achievements": True}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
                defaults.update(config)
        except Exception:
            pass
    return defaults

def save_config(config):
    """Save user configuration."""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass

CONFIG = load_config()


def show_help():
    """Show enhanced help information."""
    print(f"""
{Colors.HEADER}NovaFit — User Guide{Colors.ENDC}
{'='*30}

{Colors.GREEN}📝 Data Entry:{Colors.ENDC}
  • Use dates in YYYY-MM-DD format
  • Steps and water are required fields

{Colors.CYAN}🎯 Goals:{Colors.ENDC}
  • Steps: {CONFIG['step_goal']:,} per day
  • Water: {CONFIG['water_goal']}L per day

{Colors.WARNING}💡 Tips:{Colors.ENDC}
  • Use GUI mode for easier data entry
  • Export your data regularly for backup

{Colors.BLUE}🔧 Command Line Options:{Colors.ENDC}
  • --gui: Open graphical interface
  • --seed N: Generate N days of demo data
  • --help: Show this help
""")


def validate_date(date_str: str) -> bool:
    """Validate date string format YYYY-MM-DD."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def safe_input(prompt: str, input_type: type = str, default=None, validator=None):
    """Safe input with type conversion and validation.
    
    Prompts the user for input with automatic type conversion, default values,
    and custom validation. Handles keyboard interrupts gracefully.
    
    Args:
        prompt (str): The input prompt to display to the user.
        input_type (type, optional): Type to convert input to. Defaults to str.
        default: Default value if user enters nothing. Defaults to None.
        validator: Function to validate the converted input. Defaults to None.
    
    Returns:
        The user input converted to the specified type, or None if cancelled.
        
    Raises:
        KeyboardInterrupt: Converted to None return value for graceful handling.
    """
    while True:
        try:
            value = input(prompt).strip()
            if not value and default is not None:
                return default
            if not value and default is None:
                print("  ⚠️ This field is required")
                continue
            
            if input_type == int:
                value = int(value)
            elif input_type == float:
                value = float(value)
            
            if validator and not validator(value):
                print("  ⚠️ Invalid format or value")
                continue
                
            return value
        except ValueError:
            print(f"  ⚠️ Please enter a valid {input_type.__name__}")
        except (KeyboardInterrupt, EOFError):
            print("\n  Operation cancelled")
            return None


def format_entry_display(entry):
    """Format for displaying entries."""
    date_str, steps, water, calories, mood = entry
    step_icon = "✅" if steps >= CONFIG["step_goal"] else "⚠️"
    water_icon = "✅" if water >= CONFIG["water_goal"] else "⚠️"
    mood_str = f" {mood}" if mood else " 😐"
    cal_str = f", {calories:,}cal" if calories else ""
    return f"📅 {date_str} | 🚶 {steps:,} {step_icon} | 💧 {water}L {water_icon}{cal_str}{mood_str}"

def show_progress_bar(current, goal, label):
    """Display a visual progress bar for tracking goals.
    
    Creates a visual progress bar using Unicode characters to show
    progress towards a specific goal with percentage calculation.
    
    Args:
        current (int|float): Current value achieved.
        goal (int|float): Target goal value.
        label (str): Label to display with the progress bar.
    
    Returns:
        str: Formatted string containing the progress bar and statistics.
    """
    percentage = min(100, (current / goal) * 100) if goal > 0 else 0
    filled = int(percentage / 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"{label}: {bar} {percentage:.1f}% ({current}/{goal})"

def clear_screen():
    """Clear the terminal screen.
    
    Clears the terminal screen using the appropriate command for the
    current operating system (cls for Windows, clear for Unix-like systems).
    """
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def init_db(path: Path) -> None:
    """Initialize SQLite database."""
    path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            date TEXT UNIQUE,
            steps INTEGER,
            water_l REAL,
            calories INTEGER,
            mood TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_entry(date_str: str, steps: int, water_l: float, calories: Optional[int] = None, mood: Optional[str] = None) -> None:
    """Add or update a daily health entry."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT OR REPLACE INTO logs (date, steps, water_l, calories, mood) VALUES (?, ?, ?, ?, ?)", 
                (date_str, steps, water_l, calories, mood))
    conn.commit()
    conn.close()

def list_entries(limit: int = 10) -> list[tuple]:
    """Get recent entries from database."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT date, steps, water_l, calories, mood FROM logs ORDER BY date DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows


def export_json(path: Path) -> int:
    """Export all health entries to a JSON file.
    
    This function saves all your health data to a JSON file that you can:
    - Share with friends or family
    - Import into other applications
    - Keep as a backup
    
    Args:
        path: Where to save the JSON file
        
    Returns:
        Number of entries exported
        
    For beginners: This function connects to the database, gets all records,
    converts them to a format that's easy to read, and saves to a file.
    """
    # Step 1: Connect to the database and get all entries
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT date, steps, water_l, calories, mood FROM logs").fetchall()
    conn.close()
    
    # Step 2: Convert database rows to a list of dictionaries
    # This makes the data more readable and easier to work with
    data = []
    for row in rows:
        entry = {
            "date": row[0],
            "steps": row[1], 
            "water_l": row[2],
            "calories": row[3],
            "mood": row[4]
        }
        data.append(entry)
    
    # Step 3: Create the directory if it doesn't exist and save the file
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)  # indent=2 makes the file easier to read
    
    return len(data)

def import_json(path: Path) -> int:
    """Import entries from JSON file."""
    if not path.exists():
        return 0
    
    with open(path) as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_PATH)
    count = 0
    for entry in data:
        try:
            conn.execute("INSERT OR IGNORE INTO logs (date, steps, water_l, calories, mood) VALUES (?, ?, ?, ?, ?)",
                        (entry["date"], entry["steps"], entry["water_l"], entry.get("calories"), entry.get("mood")))
            count += 1
        except KeyError:
            continue
    conn.commit()
    conn.close()
    return count


def seed_fake(n: int) -> int:
    """Generate n days of fake demo data."""
    fake = Faker()
    conn = sqlite3.connect(DB_PATH)
    count = 0
    
    for i in range(n):
        fake_date = (date.today() - timedelta(days=i)).isoformat()
        steps = fake.random_int(2000, 15000)
        water_l = round(fake.random.uniform(1.0, 4.0), 1)
        calories = fake.random_int(1200, 3000)
        mood = fake.random_element(["😊", "😐", "😴", "🙂", "😅"])
        
        try:
            conn.execute("INSERT OR IGNORE INTO logs (date, steps, water_l, calories, mood) VALUES (?, ?, ?, ?, ?)",
                        (fake_date, steps, water_l, calories, mood))
            count += 1
        except:
            continue
    
    conn.commit()
    conn.close()
    return count


def get_weather(city: str) -> dict:
    """Fetch current weather using Open-Meteo API."""
    city_key = city.lower()
    lat, lon = CITY_COORDS.get(city_key, CITY_COORDS["beersheba"])
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relative_humidity_2m"
        print(f"Debug: Fetching weather from: {url}")  # Debug line
        
        # Use requests with SSL verification disabled due to PostgreSQL certificate issues
        response = requests.get(url, timeout=10, verify=False)
        print(f"Debug: Response status: {response.status_code}")  # Debug line
        
        if response.status_code == 200:
            data = response.json()
            weather = data.get("current_weather", {})
            
            # Get humidity from hourly data (first hour as approximation)
            humidity = 45  # Default fallback
            if "hourly" in data and "relative_humidity_2m" in data["hourly"]:
                humidity_data = data["hourly"]["relative_humidity_2m"]
                if humidity_data and len(humidity_data) > 0:
                    humidity = humidity_data[0]
            
            return {
                "temp": weather.get("temperature", "N/A"), 
                "humidity": humidity,
                "source": "Open-Meteo",
                "status": "success"
            }
        else:
            print(f"Debug: API error: {response.status_code}")
            return {
                "temp": "N/A", 
                "humidity": "N/A", 
                "source": f"API Error {response.status_code}",
                "status": "api_error"
            }
    except requests.exceptions.Timeout:
        print("Debug: Request timeout")
        return {
            "temp": "N/A", 
            "humidity": "N/A", 
            "source": "Request timeout",
            "status": "timeout"
        }
    except requests.exceptions.ConnectionError:
        print("Debug: Connection error")
        return {
            "temp": "N/A", 
            "humidity": "N/A", 
            "source": "Network connection error",
            "status": "connection_error"
        }
    except requests.exceptions.RequestException as e:
        print(f"Debug: Network error: {e}")
        return {
            "temp": "N/A", 
            "humidity": "N/A", 
            "source": f"Network Error: {str(e)}",
            "status": "network_error"
        }
    except json.JSONDecodeError:
        print("Debug: Invalid JSON response")
        return {
            "temp": "N/A", 
            "humidity": "N/A", 
            "source": "Invalid API response",
            "status": "json_error"
        }
    except Exception as e:
        print(f"Debug: General error: {e}")
        return {
            "temp": "N/A", 
            "humidity": "N/A", 
            "source": f"Error: {str(e)}",
            "status": "general_error"
        }

def get_dashboard_stats() -> dict:
    """Calculate dashboard statistics."""
    conn = sqlite3.connect(DB_PATH)
    stats = conn.execute("SELECT COUNT(*), SUM(steps), SUM(water_l), MAX(date) FROM logs").fetchone()
    count, total_steps, total_water, last_date = stats
    
    if count == 0:
        return {"count": 0, "total_steps": 0, "avg_steps": 0, "total_water": 0, "avg_water": 0, "last_date": "None"}
    
    avg_steps = int(total_steps / count) if total_steps else 0
    avg_water = round(total_water / count, 1) if total_water else 0
    conn.close()
    return {"count": count, "total_steps": total_steps or 0, "avg_steps": avg_steps, "total_water": total_water or 0, "avg_water": avg_water, "last_date": last_date or "None"}


def cli_menu():
    """Main CLI menu loop interface.
    
    Displays the main menu interface for the command-line version of NovaFit,
    handles user input for menu navigation, and routes to appropriate functions.
    Provides comprehensive health tracking features including data entry,
    analytics, import/export, and external integrations.
    
    The menu supports:
    - Data entry and management
    - Analytics and dashboard viewing  
    - Weather integration
    - Import/export functionality
    - GUI launcher
    - Demo data generation
    """
    print(f"{Colors.CYAN}Welcome to NovaFit! 🏃‍♂️{Colors.ENDC}")
    
    while True:
        try:
            print(f"\n{Colors.HEADER}{'='*40}{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.BLUE}        NovaFit — Health Tracker{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*40}{Colors.ENDC}")
            print(f"{Colors.GREEN}📝 Data:{Colors.ENDC}")
            print("  1) ➕ Add new entry")
            print("  2) ⚡ Quick entry for today")
            print("  3) 📋 List recent entries")
            print("  4) 🗑️  Delete entry by date")
            print(f"{Colors.CYAN}📊 Analytics:{Colors.ENDC}")
            print("  5) 📈 Dashboard")
            print("  6) 🔍 Search entries")
            print(f"{Colors.WARNING}🌐 External:{Colors.ENDC}")
            print("  7) 🌤️  Weather lookup")
            print(f"{Colors.BLUE}💾 Import/Export:{Colors.ENDC}")
            print("  8) 📤 Export to JSON")
            print("  9) 📥 Import from JSON")
            print("  10) 🎲 Generate demo data")
            print(f"{Colors.CYAN}🖥️  Interface:{Colors.ENDC}")
            print("  11) 🖼️ Open GUI")
            print("  12) 🧹 Clear screen")
            print("  13) ❓ Show help")
            print(f"{Colors.FAIL}  0) 👋 Exit{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*40}{Colors.ENDC}")
            
            choice = input(f"{Colors.BOLD}Choose option (0-13): {Colors.ENDC}").strip()
            
            if choice == "0":
                print(f"{Colors.GREEN}Goodbye! Stay healthy! 👋{Colors.ENDC}")
                break
            elif choice == "1":
                cli_add_entry()
            elif choice == "2":
                cli_quick_entry()
            elif choice == "3":
                cli_list_entries()
            elif choice == "4":
                cli_delete_entry()
            elif choice == "5":
                cli_dashboard()
            elif choice == "6":
                cli_search_entries()
            elif choice == "7":
                cli_weather()
            elif choice == "8":
                cli_export()
            elif choice == "9":
                cli_import()
            elif choice == "10":
                cli_seed()
            elif choice == "11":
                launch_gui()
            elif choice == "12":
                clear_screen()
                print(f"{Colors.GREEN}Screen cleared! ✨{Colors.ENDC}")
            elif choice == "13":
                show_help()
            else:
                print(f"{Colors.WARNING}Invalid choice! Please enter 0-13 ⚠️{Colors.ENDC}")
                
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.GREEN}Goodbye! 👋{Colors.ENDC}")
            break


def cli_quick_entry():
    """Quick entry interface for today's health data.
    
    Provides a streamlined interface for entering health data for the current date.
    Prompts for steps, water intake, and optional calories and mood data.
    Automatically sets the date to today for convenience.
    
    Required inputs:
    - Steps (integer, must be >= 0)
    - Water intake in liters (float, must be >= 0)
    
    Optional inputs:
    - Calories (integer)
    - Mood (emoji string, defaults to 😊)
    """
    print(f"\n{Colors.BLUE}⚡ Quick Entry for Today{Colors.ENDC}")
    print("=" * 25)
    
    steps = safe_input("🚶 Steps: ", int, validator=lambda x: x >= 0)
    if steps is None: return
    
    water_l = safe_input("💧 Water (L): ", float, validator=lambda x: x >= 0)
    if water_l is None: return
    
    calories_input = safe_input("🍽️ Calories (Enter to skip): ", str, default="")
    calories = int(calories_input) if calories_input.strip() else None
    
    mood = input("😊 Mood (Enter for 😊): ").strip() or "😊"
    
    add_entry(date.today().isoformat(), steps, water_l, calories, mood)
    print(f"{Colors.GREEN}✅ Quick entry saved for today!{Colors.ENDC}")

def cli_add_entry():
    """CLI interface for adding a new health entry.
    
    Interactive command-line interface for adding health tracking data.
    Allows specifying a custom date or defaults to today. Validates all
    input data and provides clear feedback on successful entry creation.
    
    Prompts for:
    - Date (YYYY-MM-DD format, defaults to today)
    - Steps (required, must be >= 0)
    - Water intake in liters (required, must be >= 0)
    - Calories (optional, must be >= 0 if provided)
    - Mood (optional emoji/text)
    
    Validates date format and numeric ranges before saving to database.
    """
    print(f"\n{Colors.BLUE}➕ Add New Health Entry{Colors.ENDC}")
    print("=" * 25)
    
    try:
        date_str = safe_input(f"📅 Date (YYYY-MM-DD, default {date.today()}): ", str, date.today().isoformat(), validate_date)
        if date_str is None: return
        
        steps = safe_input("🚶 Steps: ", int, validator=lambda x: x >= 0)
        if steps is None: return
        
        water_l = safe_input("💧 Water in liters: ", float, validator=lambda x: x >= 0)
        if water_l is None: return
        
        calories = safe_input("🍽️  Calories (optional): ", int, default=None, validator=lambda x: x is None or x >= 0)
        mood = input("😊 Mood (optional): ").strip() or None
        
        add_entry(date_str, steps, water_l, calories, mood)
        print(f"{Colors.GREEN}✅ Entry saved successfully!{Colors.ENDC}")
        print(f"  📅 {date_str} | 🚶 {steps:,} steps | 💧 {water_l}L")
        if calories: print(f"  🍽️ {calories:,} calories")
        if mood: print(f"  😊 {mood}")
            
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error saving entry: {e}{Colors.ENDC}")


def cli_delete_entry():
    """CLI interface for deleting a health entry by date.
    
    Provides a safe interface for deleting health entries from the database.
    Shows recent entries first to help users identify the correct date,
    then prompts for confirmation before deletion to prevent accidental loss.
    
    Process:
    1. Displays recent entries for reference
    2. Prompts for date in YYYY-MM-DD format
    3. Requires explicit confirmation (yes/y)
    4. Provides feedback on deletion success/failure
    
    Args:
        None (interactive CLI prompts)
        
    Returns:
        None (prints status messages)
    """
    print(f"\n{Colors.WARNING}🗑️ Delete Entry{Colors.ENDC}")
    print("=" * 15)
    
    # Show recent entries first
    entries = list_entries(5)
    if not entries:
        print(f"{Colors.WARNING}No entries found to delete 📝{Colors.ENDC}")
        return
    
    print("Recent entries:")
    for i, entry in enumerate(entries, 1):
        mood_str = f" {entry[4]}" if entry[4] else ""
        cal_str = f", {entry[3]}cal" if entry[3] else ""
        print(f"  {i}. {entry[0]}: {entry[1]} steps, {entry[2]}L{cal_str}{mood_str}")
    
    date_str = safe_input(
        "\n📅 Enter date to delete (YYYY-MM-DD): ",
        str,
        validator=validate_date
    )
    if date_str is None:
        return
    
    # Confirm deletion
    confirm = input(f"⚠️ Delete entry for {date_str}? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print(f"{Colors.CYAN}Operation cancelled{Colors.ENDC}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("DELETE FROM logs WHERE date = ?", (date_str,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"{Colors.GREEN}✅ Entry for {date_str} deleted{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠️ No entry found for {date_str}{Colors.ENDC}")
        
        conn.close()
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error deleting entry: {e}{Colors.ENDC}")


def cli_search_entries():
    """CLI interface for searching health entries by date range.
    
    Allows users to search and filter health entries within a specific date range.
    Displays matching entries with summary statistics including totals and averages
    for steps and water intake across the selected period.
    
    Prompts for:
    - Start date (YYYY-MM-DD format)
    - End date (YYYY-MM-DD format)
    
    Output includes:
    - Individual entries within the date range
    - Total steps and water for the period
    - Average daily steps and water consumption
    
    Returns:
        None (prints search results and statistics)
    """
    print(f"\n{Colors.CYAN}� Search Entries{Colors.ENDC}")
    print("=" * 15)
    
    start_date = safe_input(
        "📅 Start date (YYYY-MM-DD): ",
        str,
        validator=validate_date
    )
    if start_date is None:
        return
    
    end_date = safe_input(
        "📅 End date (YYYY-MM-DD): ",
        str,
        validator=validate_date
    )
    if end_date is None:
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        entries = conn.execute("""
            SELECT date, steps, water_l, calories, mood 
            FROM logs 
            WHERE date BETWEEN ? AND ? 
            ORDER BY date DESC
        """, (start_date, end_date)).fetchall()
        conn.close()
        
        if not entries:
            print(f"{Colors.WARNING}No entries found in date range 📝{Colors.ENDC}")
            return
        
        print(f"\n{Colors.GREEN}Found {len(entries)} entries:{Colors.ENDC}")
        total_steps = sum(entry[1] for entry in entries)
        total_water = sum(entry[2] for entry in entries)
        
        for entry in entries:
            mood_str = f" {entry[4]}" if entry[4] else ""
            cal_str = f", {entry[3]}cal" if entry[3] else ""
            print(f"  📅 {entry[0]}: {entry[1]} steps, {entry[2]}L{cal_str}{mood_str}")
        
        print(f"\n{Colors.BLUE}📊 Summary:{Colors.ENDC}")
        print(f"  🚶 Total steps: {total_steps:,}")
        print(f"  💧 Total water: {total_water}L")
        if entries:
            print(f"  📈 Avg steps: {total_steps // len(entries):,}")
            print(f"  📈 Avg water: {total_water / len(entries):.1f}L")
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error searching entries: {e}{Colors.ENDC}")


def cli_list_entries():
    """CLI interface for listing recent health entries.
    
    Displays a configurable number of recent health entries from the database
    in reverse chronological order (newest first). Shows formatted entries
    with icons and summary statistics.
    
    Features:
    - Configurable entry limit (defaults to 10)
    - Formatted display with emojis and goal indicators
    - Summary totals for steps and water across displayed entries
    - Handles empty database gracefully
    
    Prompts for:
    - Number of entries to display (optional, default 10)
    
    Returns:
        None (prints formatted entry list and summary)
    """
    print(f"\n{Colors.BLUE}📋 Recent Entries{Colors.ENDC}")
    
    try:
        limit = safe_input("How many entries to show? (default 10): ", int, default=10, validator=lambda x: x > 0)
        if limit is None: return
        
        entries = list_entries(limit)
        if not entries:
            print(f"{Colors.WARNING}No entries found 📝{Colors.ENDC}")
            return
        
        print(f"\n{Colors.GREEN}Last {len(entries)} entries:{Colors.ENDC}")
        for i, entry in enumerate(entries, 1):
            print(f"{Colors.CYAN}{i:2d}.{Colors.ENDC} {format_entry_display(entry)}")
        
        total_steps = sum(entry[1] for entry in entries)
        total_water = sum(entry[2] for entry in entries)
        print(f"\n{Colors.BLUE}📊 Summary: {total_steps:,} steps, {total_water}L water{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error listing entries: {e}{Colors.ENDC}")


def cli_dashboard():
    """Enhanced CLI dashboard displaying comprehensive health statistics.
    
    Provides a comprehensive overview of health tracking data including:
    - Daily goal progress indicators with visual progress bars
    - Overall statistics (total days logged, last entry date)
    - Step and water consumption summaries with averages
    - Goal achievement analysis (percentage of days meeting goals)
    - Recent trends comparing last 7 days vs previous 7 days
    
    Visual elements include:
    - Progress bars for latest entry against daily goals
    - Achievement percentages for 10k steps and 2L water goals
    - Trend indicators showing recent performance direction
    
    Handles empty database state gracefully with helpful guidance.
    """
    print(f"\n{Colors.BLUE}📈 Health Dashboard{Colors.ENDC}")
    print("=" * 18)
    
    try:
        stats = get_dashboard_stats()
        if stats['count'] == 0:
            print(f"{Colors.WARNING}No data available yet! Add some entries first �{Colors.ENDC}")
            return
        
        print(f"\n{Colors.GREEN}🎯 Daily Goals Progress:{Colors.ENDC}")
        if stats['count'] > 0:
            # Get latest entry for progress display
            latest_entry = list_entries(1)
            if latest_entry:
                latest = latest_entry[0]
                print(f"  {show_progress_bar(latest[1], CONFIG['step_goal'], '🚶 Steps')}")
                print(f"  {show_progress_bar(latest[2], CONFIG['water_goal'], '💧 Water')}")
        
        print(f"\n{Colors.GREEN}�📊 Overall Statistics:{Colors.ENDC}")
        print(f"  📅 Days logged: {stats['count']}")
        print(f"  📆 Last entry: {stats['last_date']}")
        
        print(f"\n{Colors.CYAN}🚶 Steps Summary:{Colors.ENDC}")
        print(f"  📈 Total steps: {stats['total_steps']:,}")
        print(f"  📊 Average/day: {stats['avg_steps']:,}")
        
        # Steps goal analysis (assuming 10,000 steps/day goal)
        goal_days = sum(1 for entry in list_entries(stats['count']) if entry[1] >= 10000)
        goal_percentage = (goal_days / stats['count']) * 100 if stats['count'] > 0 else 0
        print(f"  🎯 Days reaching 10k steps: {goal_days}/{stats['count']} ({goal_percentage:.1f}%)")
        
        print(f"\n{Colors.BLUE}💧 Water Summary:{Colors.ENDC}")
        print(f"  📈 Total water: {stats['total_water']}L")
        print(f"  📊 Average/day: {stats['avg_water']}L")
        
        # Water goal analysis (assuming 2L/day goal)
        water_entries = list_entries(stats['count'])
        water_goal_days = sum(1 for entry in water_entries if entry[2] >= 2.0)
        water_goal_percentage = (water_goal_days / stats['count']) * 100 if stats['count'] > 0 else 0
        print(f"  🎯 Days reaching 2L goal: {water_goal_days}/{stats['count']} ({water_goal_percentage:.1f}%)")
        
        # Recent trend (last 7 days vs previous 7 days)
        recent_entries = list_entries(14)
        if len(recent_entries) >= 7:
            recent_7 = recent_entries[:7]
            prev_7 = recent_entries[7:14] if len(recent_entries) >= 14 else recent_entries[7:]
            
            recent_avg_steps = sum(entry[1] for entry in recent_7) / len(recent_7)
            prev_avg_steps = sum(entry[1] for entry in prev_7) / len(prev_7) if prev_7 else recent_avg_steps
            
            trend = "📈" if recent_avg_steps > prev_avg_steps else "📉" if recent_avg_steps < prev_avg_steps else "➡️"
            
            print(f"\n{Colors.WARNING}📈 Recent Trends (last 7 days):{Colors.ENDC}")
            print(f"  {trend} Steps trend: {recent_avg_steps:.0f} vs {prev_avg_steps:.0f} (previous 7 days)")
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error generating dashboard: {e}{Colors.ENDC}")


def cli_weather():
    """CLI interface for weather lookup functionality.
    
    Provides weather information for predefined Israeli cities using the Open-Meteo API.
    Users can select from a numbered list of cities or enter a custom city name.
    Displays current temperature and humidity data when available.
    
    Supported cities:
    - Beersheba, Tel Aviv, Jerusalem, Haifa, Eilat
    
    Features:
    - Numbered city selection or manual city name entry
    - Real-time weather data via Open-Meteo API
    - Graceful handling of network/API failures
    - Temperature in Celsius and relative humidity percentage
    
    Returns:
        None (prints weather information or error messages)
    """
    print(f"\n{Colors.CYAN}🌤️ Weather Lookup{Colors.ENDC}")
    
    cities = list(CITY_COORDS.keys())
    print("Available cities:")
    for i, city in enumerate(cities, 1):
        print(f"  {i}. {city.title()}")
    
    try:
        choice = safe_input(f"\nSelect city (1-{len(cities)}) or enter name: ", str)
        if choice is None: return
        
        if choice.isdigit() and 1 <= int(choice) <= len(cities):
            city = cities[int(choice) - 1]
        else:
            city = choice.lower()
        
        print(f"🔍 Looking up weather for {city.title()}...")
        weather = get_weather(city)
        
        if weather["temp"] != "N/A":
            print(f"{Colors.GREEN}🌤️ {city.title()}: {weather['temp']}°C, {weather['humidity']}% humidity{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠️ Could not fetch weather data{Colors.ENDC}")
            
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error fetching weather: {e}{Colors.ENDC}")

def cli_export():
    """CLI interface for exporting health data to JSON format.
    
    Exports all health tracking data from the database to a JSON file.
    Supports both default export location and custom file paths.
    Provides feedback on export success including record count and file size.
    
    Options:
    - Use default export path (./data/novafit_export.json)
    - Specify custom file path
    
    Output information:
    - Number of records exported
    - File size in KB (when records > 0)
    - Export file location
    
    Handles errors gracefully with informative error messages.
    """
    print(f"\n{Colors.BLUE}📤 Export Data{Colors.ENDC}")
    
    try:
        use_custom = input("Use custom file path? (y/n, default n): ").strip().lower()
        
        if use_custom in ['y', 'yes']:
            custom_path = input(f"Enter file path (default {EXPORT_PATH}): ").strip()
            export_path = Path(custom_path) if custom_path else EXPORT_PATH
        else:
            export_path = EXPORT_PATH
        
        count = export_json(export_path)
        print(f"{Colors.GREEN}✅ Exported {count} records to {export_path} 💾{Colors.ENDC}")
        
        if count > 0:
            file_size = export_path.stat().st_size / 1024
            print(f"  📁 File size: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error exporting data: {e}{Colors.ENDC}")

def cli_import():
    """CLI interface for importing health data from JSON format.
    
    Imports health tracking data from a JSON file into the database.
    Supports both default import location and custom file paths.
    Uses INSERT OR IGNORE to prevent duplicate entries when importing.
    
    Options:
    - Use default import path (./data/novafit_export.json)
    - Specify custom file path
    
    Features:
    - File existence validation before import attempt
    - Duplicate entry prevention (ignores existing dates)
    - Count of newly imported records
    - Graceful error handling for invalid files
    
    Returns:
        None (prints import results and status)
    """
    print(f"\n{Colors.BLUE}📥 Import Data{Colors.ENDC}")
    
    try:
        use_custom = input("Use custom file path? (y/n, default n): ").strip().lower()
        
        if use_custom in ['y', 'yes']:
            custom_path = input(f"Enter file path (default {EXPORT_PATH}): ").strip()
            import_path = Path(custom_path) if custom_path else EXPORT_PATH
        else:
            import_path = EXPORT_PATH
        
        if not import_path.exists():
            print(f"{Colors.WARNING}⚠️ File not found: {import_path}{Colors.ENDC}")
            return
        
        count = import_json(import_path)
        print(f"{Colors.GREEN}✅ Imported {count} new records{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error importing data: {e}{Colors.ENDC}")

def cli_seed():
    """CLI interface for generating fake demo health data.
    
    Generates realistic fake health tracking data for testing and demonstration
    purposes using the Faker library. Creates entries for recent dates with
    randomized but realistic values for steps, water, calories, and mood.
    
    Features:
    - Configurable number of days (1-30)
    - Realistic random values within healthy ranges
    - Confirmation prompt to prevent accidental data generation
    - Uses INSERT OR IGNORE to avoid overwriting existing data
    
    Data ranges:
    - Steps: 2,000 - 15,000
    - Water: 1.0L - 4.0L  
    - Calories: 1,200 - 3,000
    - Mood: Random emoji selection
    
    Args:
        None (interactive CLI prompts)
        
    Returns:
        None (prints generation results)
    """
    print(f"\n{Colors.WARNING}🎲 Generate Demo Data{Colors.ENDC}")
    
    try:
        n = safe_input("How many days of data to generate? (1-30): ", int, validator=lambda x: 1 <= x <= 30)
        if n is None: return
        
        confirm = input(f"⚠️ Generate {n} days of fake data? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print(f"{Colors.CYAN}Operation cancelled{Colors.ENDC}")
            return
        
        print("🎲 Generating fake data...")
        count = seed_fake(n)
        print(f"{Colors.GREEN}✅ Generated {count} fake entries 🎲{Colors.ENDC}")
        
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error generating data: {e}{Colors.ENDC}")


class NovaFitGUI:
    """Tkinter-based graphical user interface for NovaFit health tracking.
    
    Provides a comprehensive GUI for health data tracking with tabbed navigation,
    real-time validation, visual progress indicators, and integrated tools.
    Supports both light and dark themes with user preference persistence.
    
    Features:
    - Multi-tab interface (Add Entry, View Entries, Dashboard, Tools)
    - Real-time input validation with visual feedback
    - Interactive progress charts and goal tracking
    - Import/export functionality with file dialogs
    - Weather integration for environmental context
    - Theme switching and user preference persistence
    - Achievement notifications and goal progress tracking
    
    Attributes:
        root (tk.Tk): Main application window
        style (ttk.Style): Theme and styling manager
        notebook (ttk.Notebook): Main tabbed interface container
        Various GUI component variables for data binding
    """
    
    def __init__(self):
        """Initialize the NovaFit GUI application.
        
        Sets up the main window, applies user-configured theme, initializes
        the widget hierarchy, and loads initial data. Configures window
        properties including title, size, and minimum dimensions.
        
        The constructor:
        1. Creates main Tk window with appropriate sizing
        2. Applies theme based on user configuration
        3. Sets up all GUI widgets and tabs
        4. Loads and displays initial health data
        
        Window properties:
        - Title: "NovaFit — Mini Health Tracker GUI"
        - Size: 800x600 pixels (resizable)
        - Minimum size: 700x500 pixels
        """
        self.root = tk.Tk()
        self.root.title("NovaFit — Mini Health Tracker GUI")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        self.style = ttk.Style()
        if CONFIG.get("theme", "light") == "dark":
            self.style.theme_use('alt')
            self.root.configure(bg='#2b2b2b')
        else:
            self.style.theme_use('clam')
        
        self.setup_widgets()
        self.refresh_data()
    
    def setup_widgets(self):
        """Create and configure the main GUI widget hierarchy.
        
        Initializes the main notebook (tabbed) interface and sets up all
        application tabs. This method orchestrates the creation of the
        complete user interface by calling individual tab setup methods.
        
        Creates:
        - Main notebook container with padding
        - All application tabs via individual setup methods
        - Proper tab ordering and initialization
        
        Tab structure:
        1. Add Entry - Data input interface
        2. View Entries - Data viewing and management
        3. Dashboard - Statistics and analytics
        4. Tools - Utilities and settings
        """
        self.notebook = ttk.Notebook(self.root, padding="8")
        self.notebook.pack(fill="both", expand=True)
        
        self.setup_add_tab()
        self.setup_view_tab()
        self.setup_dashboard_tab()
        self.setup_tools_tab()
    
    def setup_add_tab(self):
        """Configure the Add Entry tab interface.
        
        Creates a comprehensive data entry interface with input validation,
        visual feedback, and user-friendly controls. Includes both manual
        input fields and interactive sliders for numeric values.
        
        Components created:
        - Date picker with "Today" button
        - Steps input with validation, status indicator, and slider
        - Water input with validation, status indicator, and slider  
        - Optional calories input field
        - Mood selection dropdown with emoji options
        - Action buttons (Save, Clear, Random fill)
        
        Features:
        - Real-time input validation with visual status indicators
        - Interactive sliders synchronized with text inputs
        - Goal achievement indicators (🎯 for goals met)
        - Random data generation for testing
        """
        add_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(add_frame, text="➕ Add Entry")
        
        ttk.Label(add_frame, text="Add New Health Entry", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        input_frame = ttk.LabelFrame(add_frame, text="Health Metrics", padding="10")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Date picker
        date_frame = ttk.Frame(input_frame)
        date_frame.pack(fill="x", pady=5)
        ttk.Label(date_frame, text="📅 Date:").pack(side="left")
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(date_frame, textvariable=self.date_var, width=12).pack(side="left", padx=(10, 5))
        ttk.Button(date_frame, text="Today", command=self.set_today).pack(side="left")
        
        # Steps
        steps_frame = ttk.Frame(input_frame)
        steps_frame.pack(fill="x", pady=5)
        ttk.Label(steps_frame, text="🚶 Steps:", width=12).pack(side="left")
        self.steps_var = tk.StringVar()
        ttk.Entry(steps_frame, textvariable=self.steps_var, width=15).pack(side="left", padx=10)
        self.steps_status = ttk.Label(steps_frame, text="", foreground="green")
        self.steps_status.pack(side="left", padx=5)
        self.steps_scale = ttk.Scale(steps_frame, from_=0, to=20000, orient="horizontal", command=self.update_steps_from_scale)
        self.steps_scale.pack(fill="x", expand=True, padx=(10, 0))
        
        # Water
        water_frame = ttk.Frame(input_frame)
        water_frame.pack(fill="x", pady=5)
        ttk.Label(water_frame, text="💧 Water (L):", width=12).pack(side="left")
        self.water_var = tk.StringVar()
        ttk.Entry(water_frame, textvariable=self.water_var, width=15).pack(side="left", padx=10)
        self.water_status = ttk.Label(water_frame, text="", foreground="green")
        self.water_status.pack(side="left", padx=5)
        self.water_scale = ttk.Scale(water_frame, from_=0, to=5, orient="horizontal", command=self.update_water_from_scale)
        self.water_scale.pack(fill="x", expand=True, padx=(10, 0))
        
        self.setup_validation()
        
        # Calories
        cal_frame = ttk.Frame(input_frame)
        cal_frame.pack(fill="x", pady=5)
        ttk.Label(cal_frame, text="🍽️ Calories:", width=12).pack(side="left")
        self.calories_var = tk.StringVar()
        ttk.Entry(cal_frame, textvariable=self.calories_var, width=15).pack(side="left", padx=10)
        ttk.Label(cal_frame, text="(optional)").pack(side="left")
        
        # Mood
        mood_frame = ttk.Frame(input_frame)
        mood_frame.pack(fill="x", pady=5)
        ttk.Label(mood_frame, text="😊 Mood:", width=12).pack(side="left")
        self.mood_var = tk.StringVar()
        mood_combo = ttk.Combobox(mood_frame, textvariable=self.mood_var, width=12, values=["😊", "😐", "😴", "😅", "😎", "🤒", "💪"])
        mood_combo.pack(side="left", padx=10)
        
        # Buttons
        btn_frame = ttk.Frame(add_frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(btn_frame, text="💾 Save Entry", command=self.add_entry).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🧹 Clear", command=self.clear_inputs).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🎲 Random", command=self.fill_random).pack(side="left", padx=5)
    
    def setup_view_tab(self):
        """Configure the View Entries tab interface.
        
        Creates a data viewing interface using a treeview widget to display
        health entries in a tabular format. Includes column headers with
        emojis for visual appeal and a refresh button for data updates.
        
        Components created:
        - Header with title and refresh button
        - Treeview widget with columns: Date, Steps, Water, Calories, Mood
        - Vertical scrollbar for large datasets
        - Properly sized columns for optimal display
        
        Features:
        - Tabular display of health entries
        - Scrollable interface for large datasets
        - Manual refresh capability
        - Emoji-enhanced column headers for visual appeal
        """
        view_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(view_frame, text="📋 View Entries")
        
        header_frame = ttk.Frame(view_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="Health Entries", font=("Arial", 14, "bold")).pack(side="left")
        ttk.Button(header_frame, text="🔄 Refresh", command=self.refresh_data).pack(side="right", padx=(5, 0))
        
        columns = ("Date", "Steps", "Water", "Calories", "Mood")
        self.tree = ttk.Treeview(view_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("Date", text="📅 Date")
        self.tree.heading("Steps", text="🚶 Steps")
        self.tree.heading("Water", text="💧 Water (L)")
        self.tree.heading("Calories", text="🍽️ Calories")
        self.tree.heading("Mood", text="😊 Mood")
        
        self.tree.column("Date", width=100)
        self.tree.column("Steps", width=80)
        self.tree.column("Water", width=80)
        self.tree.column("Calories", width=80)
        self.tree.column("Mood", width=60)
        
        scrollbar = ttk.Scrollbar(view_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_dashboard_tab(self):
        """Configure the Dashboard tab interface.
        
        Creates a comprehensive analytics and statistics interface with
        visual progress tracking and detailed health metrics. Combines
        graphical elements with textual statistics for complete overview.
        
        Components created:
        - Weekly progress chart canvas with goal indicators
        - Statistics text area with comprehensive health metrics
        - Quick action buttons for common dashboard operations
        
        Features:
        - Visual weekly progress chart with goal line
        - Scrollable statistics display with totals and averages
        - Quick access buttons for refresh, export, and weather
        - Color-coded progress indicators
        - Trend analysis and goal achievement tracking
        """
        dash_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(dash_frame, text="📊 Dashboard")
        
        # Title
        ttk.Label(dash_frame, text="Health Dashboard", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Progress chart frame
        progress_frame = ttk.LabelFrame(dash_frame, text="📈 Weekly Progress", padding="10")
        progress_frame.pack(fill="x", pady=(0, 10))
        
        self.progress_canvas = tk.Canvas(progress_frame, height=100, bg="white")
        self.progress_canvas.pack(fill="x", padx=5, pady=5)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(dash_frame, text="� Statistics", padding="10")
        stats_frame.pack(fill="x", pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=10, wrap="word", state="disabled")
        stats_scroll = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_text.pack(side="left", fill="both", expand=True)
        stats_scroll.pack(side="right", fill="y")
        
        # Quick actions
        action_frame = ttk.LabelFrame(dash_frame, text="⚡ Quick Actions", padding="10")
        action_frame.pack(fill="x")
        
        ttk.Button(action_frame, text="📈 Refresh Stats", 
                  command=self.update_dashboard).pack(side="left", padx=5)
        ttk.Button(action_frame, text="📤 Export Data", 
                  command=self.export_data).pack(side="left", padx=5)
        ttk.Button(action_frame, text="🌤️ Check Weather", 
                  command=self.check_weather).pack(side="left", padx=5)
    
    def setup_tools_tab(self):
        """Configure the Tools tab interface.
        
        Creates a utility interface with various tools and settings for
        data management, customization, and external integrations.
        Organizes functionality into logical sections with labeled frames.
        
        Sections created:
        - Import/Export: JSON data management with file dialogs
        - Appearance: Theme switching and visual customization
        - Data Generation: Demo data creation for testing
        - Weather: Real-time weather lookup for supported cities
        
        Features:
        - File dialog integration for import/export operations
        - Theme switching with immediate visual feedback
        - Configurable demo data generation (1-30 days)
        - Weather lookup with city selection dropdown
        - Real-time weather display in dedicated text widget
        """
        tools_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tools_frame, text="🛠️ Tools")
        
        ttk.Label(tools_frame, text="Tools & Utilities", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Import/Export section
        io_frame = ttk.LabelFrame(tools_frame, text="📁 Import/Export", padding="10")
        io_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(io_frame, text="📤 Export to JSON", 
                  command=self.export_data).pack(side="left", padx=5)
        ttk.Button(io_frame, text="📥 Import from JSON", 
                  command=self.import_data).pack(side="left", padx=5)
        
        # Theme section
        theme_frame = ttk.LabelFrame(tools_frame, text="🎨 Appearance", padding="10")
        theme_frame.pack(fill="x", pady=(0, 10))
        
        self.dark_mode = tk.BooleanVar(value=CONFIG.get("theme", "light") == "dark")
        theme_check = ttk.Checkbutton(theme_frame, text="🌙 Dark Mode", 
                                      variable=self.dark_mode, command=self.toggle_theme)
        theme_check.pack(side="left", padx=10)
        
        # Data generation section
        gen_frame = ttk.LabelFrame(tools_frame, text="🎲 Data Generation", padding="10")
        gen_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(gen_frame, text="Generate demo data:").pack(side="left")
        self.seed_var = tk.StringVar(value="7")
        ttk.Entry(gen_frame, textvariable=self.seed_var, width=5).pack(side="left", padx=5)
        ttk.Label(gen_frame, text="days").pack(side="left")
        ttk.Button(gen_frame, text="🎲 Generate", 
                  command=self.generate_demo_data).pack(side="left", padx=10)
        
        # Weather section
        weather_frame = ttk.LabelFrame(tools_frame, text="🌤️ Weather", padding="10")
        weather_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(weather_frame, text="City:").pack(side="left")
        self.city_var = tk.StringVar(value="beersheba")
        city_combo = ttk.Combobox(weather_frame, textvariable=self.city_var, width=15,
                                 values=list(CITY_COORDS.keys()))
        city_combo.pack(side="left", padx=5)
        ttk.Button(weather_frame, text="🌤️ Get Weather", 
                  command=self.check_weather).pack(side="left", padx=10)
        
        self.weather_text = tk.Text(weather_frame, height=3, width=40, state="disabled")
        self.weather_text.pack(pady=10)
    
    def set_today(self):
        """Set the date input field to today's date.
        
        Convenience method that automatically fills the date field with
        the current date in YYYY-MM-DD format. Used by the "Today" button
        in the date input section.
        """
        self.date_var.set(date.today().isoformat())
    
    def update_steps_from_scale(self, value):
        """Update the steps input field from the slider value.
        
        Callback function for the steps slider widget. Converts the slider
        value to an integer and updates the corresponding text input field.
        Provides synchronized interaction between slider and text input.
        
        Args:
            value (str): Slider value as string (Tkinter callback format).
        """
        self.steps_var.set(str(int(float(value))))
    
    def update_water_from_scale(self, value):
        """Update the water input field from the slider value.
        
        Callback function for the water slider widget. Converts the slider
        value to a float with one decimal place and updates the corresponding
        text input field. Provides synchronized interaction between slider and text input.
        
        Args:
            value (str): Slider value as string (Tkinter callback format).
        """
        self.water_var.set(f"{float(value):.1f}")
    
    def clear_inputs(self):
        """Clear all input fields and reset sliders to default values.
        
        Resets the data entry form to empty/default state by clearing
        all text input fields and setting sliders to zero. Used by the
        Clear button and after successful data entry.
        
        Clears:
        - Steps input and slider
        - Water input and slider  
        - Calories input field
        - Mood selection dropdown
        """
        self.steps_var.set("")
        self.water_var.set("")
        self.calories_var.set("")
        self.mood_var.set("")
        self.steps_scale.set(0)
        self.water_scale.set(0)
    
    def fill_random(self):
        """Fill input fields with random realistic values for testing.
        
        Generates random but realistic health data values and populates
        all input fields. Useful for testing the interface and demonstrating
        the application with sample data. Also updates sliders to match.
        
        Random ranges:
        - Steps: 2,000 - 15,000
        - Water: 1.0L - 4.0L (one decimal place)
        - Calories: 1,200 - 3,000  
        - Mood: Random selection from emoji list
        """
        from random import randint, uniform, choice
        self.steps_var.set(str(randint(2000, 15000)))
        self.water_var.set(f"{uniform(1.0, 4.0):.1f}")
        self.calories_var.set(str(randint(1200, 3000)))
        self.mood_var.set(choice(["😊", "😐", "😴", "😅", "💪"]))
        self.steps_scale.set(int(self.steps_var.get()))
        self.water_scale.set(float(self.water_var.get()))
    
    def add_entry(self):
        """Process and save a new health entry from GUI inputs.
        
        Validates all input data, saves to database if valid, checks for
        achievements, and provides user feedback. Handles both required
        and optional fields with appropriate error messaging.
        
        Validation performed:
        - Date format (YYYY-MM-DD)
        - Steps and water are positive numbers
        - Calories is positive if provided
        
        On success:
        - Saves entry to database
        - Checks and displays achievements
        - Clears input form
        - Refreshes data displays
        - Shows success message
        
        On error:
        - Displays specific error message
        - Retains user input for correction
        """
        try:
            date_str = self.date_var.get().strip()
            if not validate_date(date_str):
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return
            
            steps = int(self.steps_var.get())
            water_l = float(self.water_var.get())
            
            if steps < 0 or water_l < 0:
                messagebox.showerror("Error", "Steps and water must be positive numbers!")
                return
            
            calories = int(self.calories_var.get()) if self.calories_var.get() else None
            mood = self.mood_var.get().strip() or None
            
            add_entry(date_str, steps, water_l, calories, mood)
            
            # Check for achievements
            self.check_achievements(steps, water_l)
            
            # Clear inputs
            self.clear_inputs()
            self.set_today()
            
            self.refresh_data()
            messagebox.showinfo("Success", "Entry saved successfully! ✅")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for steps and water!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving entry: {e}")
    
    def setup_validation(self):
        """Configure real-time input validation for form fields.
        
        Sets up trace callbacks on input variables to provide immediate
        visual feedback as users type. Validation occurs on every keystroke
        to give real-time goal achievement indicators.
        
        Traces configured:
        - Steps field: Shows goal achievement icons (🎯, 👍, or ❌)
        - Water field: Shows hydration goal achievement icons
        
        The validation is non-blocking and purely visual - users can still
        submit invalid data which will be caught by add_entry validation.
        """
        # Connect validation events
        self.steps_var.trace("w", self.validate_steps)
        self.water_var.trace("w", self.validate_water)
    
    def validate_steps(self, *args):
        """Provide real-time validation feedback for steps input.
        
        Updates the visual status indicator next to the steps field based
        on the current input value compared to daily step goals.
        
        Visual indicators:
        - 🎯 Green: Meets or exceeds step goal (10,000 steps)
        - 👍 Orange: Meets half of step goal (5,000+ steps)  
        - ❌ Red: Invalid input (non-numeric)
        - Empty: No input or below half goal
        
        Args:
            *args: Variable arguments from Tkinter trace callback (unused).
        """
        try:
            steps_text = self.steps_var.get()
            if not steps_text:
                self.steps_status.config(text="", foreground="gray")
                return
                
            steps = int(steps_text)
            if steps >= CONFIG["step_goal"]:
                self.steps_status.config(text="🎯", foreground="green")
            elif steps >= CONFIG["step_goal"] // 2:
                self.steps_status.config(text="👍", foreground="orange")
            else:
                self.steps_status.config(text="", foreground="gray")
        except ValueError:
            self.steps_status.config(text="❌", foreground="red")
    
    def validate_water(self, *args):
        """Provide real-time validation feedback for water input.
        
        Updates the visual status indicator next to the water field based
        on the current input value compared to daily hydration goals.
        
        Visual indicators:
        - 🎯 Green: Meets or exceeds water goal (2.0L)
        - 👍 Orange: Meets half of water goal (1.0L+)
        - ❌ Red: Invalid input (non-numeric)  
        - Empty: No input or below half goal
        
        Args:
            *args: Variable arguments from Tkinter trace callback (unused).
        """
        try:
            water_text = self.water_var.get()
            if not water_text:
                self.water_status.config(text="", foreground="gray")
                return
                
            water = float(water_text)
            if water >= CONFIG["water_goal"]:
                self.water_status.config(text="🎯", foreground="green")
            elif water >= CONFIG["water_goal"] / 2:
                self.water_status.config(text="👍", foreground="orange")
            else:
                self.water_status.config(text="", foreground="gray")
        except ValueError:
            self.water_status.config(text="❌", foreground="red")
    
    def check_achievements(self, steps, water):
        """Check for goal achievements and display notifications.
        
        Evaluates the entered health data against daily goals and displays
        achievement notifications for goals met. Only shows notifications
        if the achievement display setting is enabled in configuration.
        
        Achievements checked:
        - Step goal achievement (10,000 steps)
        - Hydration goal achievement (2.0L water)
        - Super active achievement (15,000+ steps)
        
        Args:
            steps (int): Number of steps for the entry.
            water (float): Water intake in liters for the entry.
            
        Displays:
            Achievement popup with list of unlocked achievements (if any).
        """
        achievements = []
        
        if steps >= CONFIG["step_goal"]:
            achievements.append("🎯 Step goal achieved!")
        if water >= CONFIG["water_goal"]:
            achievements.append("💧 Hydration goal achieved!")
        if steps >= CONFIG["step_goal"] * 1.5:
            achievements.append("🏆 Super active today!")
        
        if achievements and CONFIG.get("show_achievements", True):
            achievement_text = "\n".join(achievements)
            messagebox.showinfo("🏆 Achievements Unlocked!", achievement_text)
    
    def refresh_data(self):
        """Refresh all data displays throughout the GUI.
        
        Orchestrates a complete refresh of all data-dependent interface
        elements. Called after data modifications to ensure all views
        show current information from the database.
        
        Updates:
        - Entry list in the View tab
        - Dashboard statistics and metrics  
        - Weekly progress chart visualization
        
        This is a comprehensive refresh that may take a moment for large
        datasets but ensures complete data consistency across all tabs.
        """
        self.refresh_entries()
        self.update_dashboard()
        self.update_progress_chart()
    
    def update_progress_chart(self):
        """Update the weekly progress chart visualization.
        
        Creates a visual bar chart showing the last 7 days of step data
        with color-coded bars and a goal reference line. Each bar represents
        one day's step count with different colors for goal achievement.
        
        Chart features:
        - Green bars: Days meeting step goal (10,000+ steps)
        - Yellow bars: Days below step goal  
        - Red dashed line: Daily step goal indicator
        - Date labels: MM/DD format below each bar
        - Responsive sizing: Adapts to canvas width
        
        Handles empty data gracefully with informative message.
        Chart automatically scales to show the highest step count or goal.
        """
        self.progress_canvas.delete("all")
        
        # Get last 7 days of data
        entries = list_entries(7)
        if not entries:
            self.progress_canvas.create_text(200, 50, text="No data available", 
                                           fill="gray", font=("Arial", 12))
            return
        
        # Get canvas dimensions
        self.progress_canvas.update_idletasks()
        width = self.progress_canvas.winfo_width()
        height = 80
        
        if width <= 1:  # Canvas not yet rendered
            width = 400
        
        # Calculate bar dimensions
        bar_width = max(30, (width - 20) // 7)
        max_steps = max(entry[1] for entry in entries) if entries else CONFIG["step_goal"]
        max_steps = max(max_steps, CONFIG["step_goal"])  # Ensure goal line is visible
        
        # Draw bars for each day
        for i, entry in enumerate(entries):
            x1 = 10 + i * (bar_width + 5)
            bar_height = min(height - 20, (entry[1] / max_steps) * (height - 20))
            y1 = height - bar_height
            x2 = x1 + bar_width
            y2 = height
            
            # Color based on goal achievement
            color = "#4CAF50" if entry[1] >= CONFIG["step_goal"] else "#FFC107"
            self.progress_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
            
            # Add date label
            date_parts = entry[0].split("-")
            date_label = f"{date_parts[1]}/{date_parts[2]}" if len(date_parts) == 3 else entry[0]
            self.progress_canvas.create_text(x1 + bar_width//2, height + 10, 
                                           text=date_label, fill="black", font=("Arial", 8))
        
        # Draw goal line
        goal_y = height - ((CONFIG["step_goal"] / max_steps) * (height - 20))
        self.progress_canvas.create_line(5, goal_y, width - 5, goal_y, 
                                       fill="red", dash=(3, 3), width=2)
        self.progress_canvas.create_text(width - 30, goal_y - 10, text="Goal", 
                                       fill="red", font=("Arial", 8))
    
    def refresh_entries(self):
        """Refresh the health entries display in the View tab.
        
        Updates the treeview widget with current health entries from the
        database. Clears existing display and repopulates with up to 50
        recent entries in reverse chronological order.
        
        Display format:
        - Date: YYYY-MM-DD format
        - Steps: Formatted with thousand separators  
        - Water: Decimal liters
        - Calories: Integer or empty if not recorded
        - Mood: Emoji or empty if not recorded
        
        The treeview provides sortable columns and scrolling for large datasets.
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add entries
        entries = list_entries(50)  # Show more entries in GUI
        for entry in entries:
            mood_str = entry[4] if entry[4] else ""
            cal_str = str(entry[3]) if entry[3] else ""
            self.tree.insert("", "end", values=(
                entry[0], f"{entry[1]:,}", f"{entry[2]}", cal_str, mood_str
            ))
    
    def update_dashboard(self):
        """Update the dashboard statistics display.
        
        Calculates and displays comprehensive health statistics in the
        dashboard tab's text widget. Shows both overall statistics and
        goal achievement analysis with percentage calculations.
        
        Statistics displayed:
        - Total days logged and last entry date
        - Step totals, averages, and goal achievement rates
        - Water totals, averages, and hydration goal rates  
        - Goal achievement percentages (10k steps, 2L water)
        
        Handles empty database state with helpful guidance message.
        All statistics are formatted for readability with proper separators.
        """
        try:
            stats = get_dashboard_stats()
            
            self.stats_text.config(state="normal")
            self.stats_text.delete("1.0", tk.END)
            
            if stats['count'] == 0:
                self.stats_text.insert(tk.END, "📝 No data available yet!\n\nAdd some health entries to see statistics here.")
            else:
                self.stats_text.insert(tk.END, f"📊 STATISTICS\n{'='*20}\n")
                self.stats_text.insert(tk.END, f"📅 Days logged: {stats['count']}\n📆 Last entry: {stats['last_date']}\n\n")
                self.stats_text.insert(tk.END, f"🚶 Total steps: {stats['total_steps']:,} (avg: {stats['avg_steps']:,})\n")
                self.stats_text.insert(tk.END, f"� Total water: {stats['total_water']}L (avg: {stats['avg_water']}L)\n\n")
                
                entries = list_entries(stats['count'])
                goal_days = sum(1 for entry in entries if entry[1] >= 10000)
                water_goal_days = sum(1 for entry in entries if entry[2] >= 2.0)
                self.stats_text.insert(tk.END, f"🎯 10k+ step days: {goal_days}/{stats['count']} ({goal_days/stats['count']*100:.1f}%)\n")
                self.stats_text.insert(tk.END, f"🎯 2L+ water days: {water_goal_days}/{stats['count']} ({water_goal_days/stats['count']*100:.1f}%)\n")
            
            self.stats_text.config(state="disabled")
            
        except Exception as e:
            self.stats_text.config(state="normal")
            self.stats_text.delete("1.0", tk.END)
            self.stats_text.insert(tk.END, f"❌ Error loading statistics: {e}")
            self.stats_text.config(state="disabled")
    
    def export_data(self):
        """Export health data to JSON file using file dialog.
        
        Opens a file save dialog allowing users to choose location and
        filename for data export. Exports all health entries to a JSON
        file with proper formatting and provides feedback on success.
        
        Features:
        - File dialog with JSON filter and default filename
        - Exports up to 1000 recent entries  
        - Proper JSON formatting with indentation
        - Success message with export count
        - Error handling with user-friendly messages
        
        Default filename: novafit_export.json
        File format: JSON array with entry objects
        """
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialname="novafit_export.json"
            )
            
            if filename:
                entries = list_entries(1000)
                data = [{"date": r[0], "steps": r[1], "water_l": r[2], "calories": r[3], "mood": r[4]} for r in entries]
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                messagebox.showinfo("Export Complete", f"Exported {len(entries)} records to {filename} 💾")
                    
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {e}")
    
    def import_data(self):
        """Import health data from JSON file using file dialog.
        
        Opens a file selection dialog allowing users to choose a JSON file
        for data import. Imports health entries while avoiding duplicates
        using the database's INSERT OR IGNORE functionality.
        
        Features:
        - File dialog with JSON filter
        - Duplicate prevention during import
        - Automatic data refresh after successful import
        - Import count feedback to user
        - Error handling for invalid JSON files
        
        The import process preserves existing data and only adds new entries
        based on unique date keys.
        """
        try:
            filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if filename:
                count = import_json(Path(filename))
                messagebox.showinfo("Import Complete", f"Imported {count} new records 📥")
                self.refresh_data()
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing data: {e}")
    
    def generate_demo_data(self):
        """Generate demo health data for testing and demonstration.
        
        Creates realistic fake health entries for a specified number of days
        using the Faker library. Useful for testing the application interface
        and demonstrating features with sample data.
        
        Features:
        - Configurable day count (1-30 days)
        - Confirmation dialog to prevent accidental generation
        - Realistic random values within healthy ranges
        - Automatic data refresh after generation
        - Generation count feedback
        
        Data ranges match those used in CLI seed function:
        - Steps: 2,000 - 15,000
        - Water: 1.0L - 4.0L
        - Calories: 1,200 - 3,000
        - Mood: Random emoji selection
        """
        try:
            n = int(self.seed_var.get())
            if not 1 <= n <= 30:
                messagebox.showerror("Error", "Please enter a number between 1 and 30")
                return
            
            if messagebox.askyesno("Confirm", f"Generate {n} days of demo data?"):
                count = seed_fake(n)
                messagebox.showinfo("Demo Data", f"Generated {count} fake entries 🎲")
                self.refresh_data()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating data: {e}")
    
    def check_weather(self):
        """Retrieve and display current weather for selected city.
        
        Fetches real-time weather data using the Open-Meteo API for the
        city selected in the dropdown. Updates the weather display widget
        with current conditions or error information.
        
        Features:
        - Real-time weather data via Open-Meteo API
        - Support for predefined Israeli cities
        - Temperature in Celsius and humidity percentage  
        - Graceful error handling for network issues
        - Clear display in dedicated text widget
        
        Display format:
        - City name with emoji
        - Temperature in Celsius  
        - Relative humidity percentage
        - Error messages for connection issues
        """
        try:
            city = self.city_var.get()
            print(f"Debug: Getting weather for: {city}")  # Debug line
            
            # Update weather text to show loading
            self.weather_text.config(state="normal")
            self.weather_text.delete("1.0", tk.END)
            self.weather_text.insert(tk.END, "🔄 Loading weather data...")
            self.weather_text.config(state="disabled")
            
            # Update the GUI to show loading message
            self.root.update()
            
            weather = get_weather(city)
            print(f"Debug: Weather result: {weather}")  # Debug line
            
            self.weather_text.config(state="normal")
            self.weather_text.delete("1.0", tk.END)
            
            if weather["status"] == "success":
                self.weather_text.insert(tk.END, f"🌤️ {city.title()}\n🌡️ {weather['temp']}°C\n💧 {weather['humidity']}% humidity\n📡 Source: {weather['source']}")
            else:
                # Show detailed error messages based on error type
                error_messages = {
                    "timeout": "⏱️ Request timeout - API is slow to respond",
                    "connection_error": "🌐 Internet connection issue",
                    "api_error": "⚠️ Weather service error",
                    "json_error": "📄 Invalid response from weather service",
                    "network_error": "🔌 Network error occurred",
                    "general_error": "❌ Unknown error occurred"
                }
                
                error_msg = error_messages.get(weather["status"], "❌ Unknown error")
                
                self.weather_text.insert(tk.END, 
                    f"⚠️ Weather data unavailable for {city.title()}\n"
                    f"{error_msg}\n"
                    f"📡 Details: {weather['source']}\n\n"
                    f"Troubleshooting:\n"
                    f"• Check internet connection\n"
                    f"• Verify firewall settings\n"
                    f"• Try again in a moment"
                )
            
            self.weather_text.config(state="disabled")
        except Exception as e:
            print(f"Debug: GUI weather error: {e}")
            self.weather_text.config(state="normal")
            self.weather_text.delete("1.0", tk.END)
            self.weather_text.insert(tk.END, f"❌ Error fetching weather: {str(e)}")
            self.weather_text.config(state="disabled")
    
    def toggle_theme(self):
        """Switch between light and dark visual themes.
        
        Toggles the application theme based on the dark mode checkbox state.
        Updates both the visual appearance and saves the preference to the
        configuration file for persistence across sessions.
        
        Themes:
        - Light theme: 'clam' style with system default colors
        - Dark theme: 'alt' style with dark background (#2b2b2b)
        
        The theme preference is automatically saved to config.json and
        will be restored when the application restarts.
        """
        if self.dark_mode.get():
            self.style.theme_use('alt')
            self.root.configure(bg='#2b2b2b')
            CONFIG["theme"] = "dark"
        else:
            self.style.theme_use('clam')
            self.root.configure(bg='SystemButtonFace')
            CONFIG["theme"] = "light"
        save_config(CONFIG)
    
    def run(self):
        """Start the GUI main event loop.
        
        Initiates the Tkinter main event loop which handles user interactions,
        widget updates, and maintains the GUI until the user closes the window.
        This method blocks until the GUI is closed.
        
        The main loop handles:
        - User input events (clicks, typing, etc.)
        - Widget redraws and updates
        - Timer events and animations
        - Window management and closing
        """
        self.root.mainloop()


def launch_gui():
    """Launch the Tkinter graphical user interface.
    
    Creates and starts the NovaFitGUI instance, providing a user-friendly
    graphical interface for health tracking. The GUI offers tabbed navigation
    with data entry, viewing, dashboard, and tools functionality.
    
    GUI Features:
    - Tabbed interface for different functions
    - Real-time input validation with visual feedback
    - Interactive charts and progress visualization
    - Theme switching (light/dark mode)
    - Import/export with file dialogs
    - Weather integration
    
    Returns:
        None (runs GUI main loop until user closes window)
    """
    gui = NovaFitGUI()
    gui.run()

def main():
    """Main entry point for the NovaFit application.
    
    Processes command-line arguments and initializes the appropriate interface
    (CLI or GUI). Handles database initialization and provides options for
    direct data seeding or interface selection.
    
    Command-line options:
    - --gui: Launch GUI directly bypassing CLI menu
    - --seed N: Generate N days of fake demo data and exit
    - No args: Start interactive CLI menu
    
    The function ensures the database is properly initialized before any
    operations and provides appropriate error handling for invalid arguments.
    
    Args:
        None (reads from sys.argv via argparse)
        
    Returns:
        None (exits after completing requested operation)
    """
    parser = argparse.ArgumentParser(description="NovaFit — Mini Health Tracker")
    parser.add_argument("--gui", action="store_true", help="Launch GUI directly")
    parser.add_argument("--seed", type=int, help="Seed N days of fake data")
    args = parser.parse_args()
    
    init_db(DB_PATH)
    
    if args.seed:
        count = seed_fake(args.seed)
        print(f"Generated {count} fake entries 🎲")
        return
    
    if args.gui:
        launch_gui()
    else:
        cli_menu()

if __name__ == "__main__":
    main()