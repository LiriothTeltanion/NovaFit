def seed_fake(n: int) -> int:
    """Generate n days of fake demo data."""
    from faker import Faker
    import sqlite3
    from datetime import date, timedelta
    from pathlib import Path
    from novafit.config import CONFIG
    DB_PATH = Path(CONFIG.get('db_path', './data/novafit.db'))
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
"""Import/Export and Data Generation for NovaFit

This module handles:
- JSON export/import with metadata
- CSV export/import for spreadsheet compatibility
- Demo data generation with Faker
- Sample data initialization for new users
"""

import json
import csv
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional

try:
    from faker import Faker
except ImportError:
    Faker = None

from .config import EXPORT_PATH, CSV_EXPORT_PATH, DATA_DIR
from .database import get_all_entries, add_entry

# =============================================================================
# JSON EXPORT/IMPORT
# =============================================================================

def export_to_json(filepath: Path = EXPORT_PATH, include_metadata: bool = True) -> int:
    """Export all health data to JSON file with optional metadata.
    
    Creates a JSON file with all health entries from the database.
    Includes metadata (export date, entry count, app version) by default.
    
    Args:
        filepath (Path): Destination file path (default: EXPORT_PATH from config)
        include_metadata (bool): Whether to include metadata (default: True)
        
    Returns:
        int: Number of entries exported
        
    Raises:
        IOError: If file cannot be written
        
    Example:
        >>> count = export_to_json()
        >>> print(f"Exported {count} entries")
    """
    # Get all entries from database
    entries = get_all_entries()
    
    # Prepare data structure
    if include_metadata:
        export_data = {
            "metadata": {
                "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_entries": len(entries),
                "application": "NovaFit Health Tracker",
                "version": "1.0"
            },
            "health_data": [{
                "date": e['date'],
                "steps": e['steps'],
                "water_l": e['water_l'],
                "calories": e['calories'],
                "mood": e['mood']
            } for e in entries]
        }
    else:
        export_data = [{
            "date": e['date'],
            "steps": e['steps'],
            "water_l": e['water_l'],
            "calories": e['calories'],
            "mood": e['mood']
        } for e in entries]
    
    # Ensure directory exists
    filepath.parent.mkdir(exist_ok=True)
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    return len(entries)


def import_from_json(filepath: Path) -> int:
    """Import health data from JSON file.
    
    Supports both formats:
    - Simple list: [{"date": "...", "steps": ...}, ...]
    - With metadata: {"metadata": {...}, "health_data": [...]}
    
    Skips entries that already exist (based on date).
    
    Args:
        filepath (Path): Source JSON file path
        
    Returns:
        int: Number of NEW entries imported (duplicates skipped)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
        
    Example:
        >>> count = import_from_json(Path("backup.json"))
        >>> print(f"Imported {count} new entries")
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Read JSON file
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON formats
    if isinstance(data, list):
        # Simple list format
        entries = data
    elif isinstance(data, dict) and "health_data" in data:
        # Metadata format
        entries = data["health_data"]
    else:
        # Assume it's the data itself
        entries = data if isinstance(data, list) else [data]
    
    # Import entries
    imported = 0
    for entry in entries:
        try:
            add_entry(
                entry['date'],
                entry['steps'],
                entry['water_l'],
                entry.get('calories'),
                entry.get('mood')
            )
            imported += 1
        except (KeyError, TypeError, ValueError):
            # Skip invalid entries
            continue
    
    return imported


# =============================================================================
# CSV EXPORT/IMPORT
# =============================================================================

def export_to_csv(filepath: Path = CSV_EXPORT_PATH) -> int:
    """Export all health data to CSV file.
    
    Creates a spreadsheet-compatible CSV file with headers:
    Date, Steps, Water (L), Calories, Mood
    
    Args:
        filepath (Path): Destination file path (default: CSV_EXPORT_PATH)
        
    Returns:
        int: Number of entries exported
        
    Example:
        >>> count = export_to_csv()
        >>> print(f"Exported {count} entries to CSV")
    """
    # Get all entries
    entries = get_all_entries()
    
    # Ensure directory exists
    filepath.parent.mkdir(exist_ok=True)
    
    # Write CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['Date', 'Steps', 'Water (L)', 'Calories', 'Mood'])
        
        # Write data rows
        for entry in entries:
            writer.writerow([
                entry['date'],
                entry['steps'],
                entry['water_l'],
                entry['calories'] or '',
                entry['mood'] or ''
            ])
    
    return len(entries)


def import_from_csv(filepath: Path) -> int:
    """Import health data from CSV file.
    
    Expects CSV with headers (case-insensitive):
    - Date or date
    - Steps or steps
    - Water (L) or water_l or Water
    - Calories or calories (optional)
    - Mood or mood (optional)
    
    Args:
        filepath (Path): Source CSV file path
        
    Returns:
        int: Number of entries imported
        
    Raises:
        FileNotFoundError: If file doesn't exist
        
    Example:
        >>> count = import_from_csv(Path("health_data.csv"))
        >>> print(f"Imported {count} entries from CSV")
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    imported = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Handle different possible column names (case-insensitive)
                date_val = row.get('Date') or row.get('date')
                steps_val = row.get('Steps') or row.get('steps')
                water_val = (row.get('Water (L)') or row.get('water_l') or 
                           row.get('Water') or row.get('water'))
                calories_val = row.get('Calories') or row.get('calories')
                mood_val = row.get('Mood') or row.get('mood')
                
                # Convert to appropriate types
                steps = int(float(steps_val)) if steps_val else 0
                water = float(water_val) if water_val else 0.0
                calories = int(float(calories_val)) if calories_val else None
                mood = mood_val if mood_val else None
                
                # Add entry (INSERT OR IGNORE handles duplicates)
                add_entry(date_val, steps, water, calories, mood)
                imported += 1
                
            except (ValueError, TypeError, KeyError):
                # Skip invalid rows
                continue
    
    return imported


# =============================================================================
# DEMO DATA GENERATION
# =============================================================================

def generate_demo_data(days: int = 7, start_date: Optional[date] = None) -> int:
    """Generate realistic fake health data using Faker library.
    
    Creates random but realistic health entries for testing.
    
    Args:
        days (int): Number of days to generate (default: 7)
        start_date (date, optional): Starting date (default: today)
        
    Returns:
        int: Number of entries generated
        
    Raises:
        ImportError: If Faker library is not installed
        
    Data ranges:
        - Steps: 2,000 - 15,000
        - Water: 1.0L - 4.0L
        - Calories: 1,200 - 3,000
        - Mood: Random emoji (😊, 😐, 😴, 🙂, 😅, 💪, 🤒)
        
    Example:
        >>> count = generate_demo_data(30)
        >>> print(f"Generated {count} days of demo data")
    """
    if Faker is None:
        raise ImportError("Faker library is required for demo data generation. "
                        "Install it with: pip install Faker")
    
    fake = Faker()
    
    if start_date is None:
        start_date = date.today()
    
    generated = 0
    mood_options = ["😊", "😐", "😴", "🙂", "😅", "💪", "🤒"]
    
    for i in range(days):
        entry_date = (start_date - timedelta(days=i)).isoformat()
        
        # Generate realistic random data
        steps = fake.random_int(2000, 15000)
        water_l = round(fake.random.uniform(1.0, 4.0), 1)
        calories = fake.random_int(1200, 3000)
        mood = fake.random_element(mood_options)
        
        try:
            add_entry(entry_date, steps, water_l, calories, mood)
            generated += 1
        except ValueError:
            # Entry already exists, skip
            continue
    
    return generated


def initialize_sample_data(overwrite: bool = True) -> int:
    """Initialize database with a week of realistic sample data.
    
    Perfect for new users to see how the application works.
    Creates 7 days of varied but realistic health data.
    
    Args:
        overwrite (bool): Whether to overwrite existing entries (default: True)
                         If False, uses INSERT OR IGNORE
        
    Returns:
        int: Number of entries created
        
    Example:
        >>> count = initialize_sample_data()
        >>> print(f"Initialized {count} sample entries")
    """
    sample_data = [
        {
            "date": (date.today() - timedelta(days=6)).isoformat(),
            "steps": 8500,
            "water_l": 2.1,
            "calories": 1850,
            "mood": "😊"
        },
        {
            "date": (date.today() - timedelta(days=5)).isoformat(),
            "steps": 12000,
            "water_l": 2.5,
            "calories": 2100,
            "mood": "😊"
        },
        {
            "date": (date.today() - timedelta(days=4)).isoformat(),
            "steps": 6500,
            "water_l": 1.8,
            "calories": 1650,
            "mood": "😐"
        },
        {
            "date": (date.today() - timedelta(days=3)).isoformat(),
            "steps": 10500,
            "water_l": 2.2,
            "calories": 1950,
            "mood": "🙂"
        },
        {
            "date": (date.today() - timedelta(days=2)).isoformat(),
            "steps": 15000,
            "water_l": 3.0,
            "calories": 2300,
            "mood": "💪"
        },
        {
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "steps": 7800,
            "water_l": 2.0,
            "calories": 1700,
            "mood": "😴"
        },
        {
            "date": date.today().isoformat(),
            "steps": 9200,
            "water_l": 2.3,
            "calories": 1800,
            "mood": "😊"
        }
    ]
    
    created = 0
    for entry in sample_data:
        try:
            add_entry(
                entry['date'],
                entry['steps'],
                entry['water_l'],
                entry['calories'],
                entry['mood']
            )
            created += 1
        except ValueError:
            # Entry exists, skip if not overwriting
            if not overwrite:
                continue
    
    return created


# =============================================================================
# FILE UTILITIES
# =============================================================================

def get_export_info(filepath: Path) -> Optional[Dict]:
    """Get information about an exported JSON file.
    
    Args:
        filepath (Path): Path to JSON export file
        
    Returns:
        dict or None: Metadata if available, None otherwise
    """
    if not filepath.exists():
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'metadata' in data:
            return data['metadata']
        
        # No metadata, return basic info
        entries = data.get('health_data', data) if isinstance(data, dict) else data
        return {
            "total_entries": len(entries) if isinstance(entries, list) else 0,
            "has_metadata": False
        }
    except Exception:
        return None


def validate_json_export(filepath: Path) -> bool:
    """Validate that a JSON file is a valid NovaFit export.
    
    Args:
        filepath (Path): Path to JSON file
        
    Returns:
        bool: True if valid export, False otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get entries
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict) and 'health_data' in data:
            entries = data['health_data']
        else:
            return False
        
        # Check at least one entry has required fields
        if entries and len(entries) > 0:
            first_entry = entries[0]
            required_fields = ['date', 'steps', 'water_l']
            return all(field in first_entry for field in required_fields)
        
        return True  # Empty export is valid
        
    except Exception:
        return False


def validate_csv_export(filepath: Path) -> bool:
    """Validate that a CSV file is a valid NovaFit export.
    
    Args:
        filepath (Path): Path to CSV file
        
    Returns:
        bool: True if valid export, False otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Check for required headers (case-insensitive)
            if not headers:
                return False
            
            headers_lower = [h.lower() for h in headers]
            return 'date' in headers_lower and 'steps' in headers_lower
            
    except Exception:
        return False
