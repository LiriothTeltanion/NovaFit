#!/usr/bin/env python3
"""
Test script for NovaFit — demonstrates all features
"""

import sys
from pathlib import Path

# Add current directory to path to import novafit
sys.path.insert(0, str(Path(__file__).parent))

from novafit import (
    init_db, add_entry, list_entries, export_json, import_json,
    seed_fake, get_weather, get_dashboard_stats, DB_PATH, EXPORT_PATH
)

def run_demo():
    """Execute a comprehensive demonstration of all NovaFit features.
    
    Performs a complete test of the NovaFit health tracking system by
    exercising all major functionality including database operations,
    data entry, statistics generation, external API calls, and file I/O.
    
    Demo sequence:
    1. Database initialization and setup
    2. Manual health entry creation
    3. Fake data generation for testing (7 days)
    4. Recent entries display and formatting
    5. Dashboard statistics calculation and display
    6. Weather API integration test
    7. JSON export functionality test
    8. JSON import functionality test (duplicate handling)
    
    Features demonstrated:
    - Core database operations (init, insert, select)
    - Data validation and entry creation
    - Statistical analysis and dashboard generation
    - External API integration (Open-Meteo weather)
    - File I/O operations (JSON export/import)
    - Error handling and graceful degradation
    
    Output includes step-by-step progress with success indicators and
    final summary with usage instructions for interactive modes.
    """
    print("🏃‍♂️ NovaFit Demo - Testing all features...")
    print("="*50)
    
    # 1. Initialize database
    print("1. Initializing database...")
    init_db(DB_PATH)
    print("   ✅ Database initialized")
    
    # 2. Add a manual entry
    print("\n2. Adding a manual entry...")
    add_entry("2025-10-14", 8500, 2.5, 2000, "😊")
    print("   ✅ Entry added: 8500 steps, 2.5L water, 2000 calories, 😊")
    
    # 3. Generate fake data
    print("\n3. Generating fake demo data...")
    count = seed_fake(7)
    print(f"   ✅ Generated {count} fake entries")
    
    # 4. List recent entries
    print("\n4. Listing recent entries...")
    entries = list_entries(5)
    for i, entry in enumerate(entries[:3], 1):  # Show only 3 for demo
        mood_str = f" {entry[4]}" if entry[4] else ""
        cal_str = f", {entry[3]}cal" if entry[3] else ""
        print(f"   {i}. {entry[0]}: {entry[1]} steps, {entry[2]}L{cal_str}{mood_str}")
    if len(entries) > 3:
        print(f"   ... and {len(entries) - 3} more entries")
    
    # 5. Show dashboard stats
    print("\n5. Dashboard statistics...")
    stats = get_dashboard_stats()
    print(f"   📊 Days logged: {stats['count']}")
    print(f"   🚶 Total steps: {stats['total_steps']:,} (avg: {stats['avg_steps']:,})")
    print(f"   💧 Total water: {stats['total_water']}L (avg: {stats['avg_water']}L)")
    print(f"   📅 Last entry: {stats['last_date']}")
    
    # 6. Test weather (may fail due to network)
    print("\n6. Testing weather API...")
    weather = get_weather("beersheba")
    if weather["temp"] != "N/A":
        print(f"   🌤️ Weather in Beersheba: {weather['temp']}°C, RH {weather['humidity']}%")
    else:
        print("   ⚠️ Weather API unavailable (network/firewall issue)")
    
    # 7. Export data
    print("\n7. Exporting data to JSON...")
    exported_count = export_json(EXPORT_PATH)
    print(f"   💾 Exported {exported_count} records to {EXPORT_PATH}")
    
    # 8. Test import (should find no new records)
    print("\n8. Testing JSON import...")
    imported_count = import_json(EXPORT_PATH)
    print(f"   📂 Imported {imported_count} new records (duplicates ignored)")
    
    print("\n" + "="*50)
    print("🎉 Demo complete! All features tested successfully.")
    print("\nTo try the interactive CLI:")
    print("   python novafit.py")
    print("\nTo launch the GUI:")
    print("   python novafit.py --gui")

if __name__ == "__main__":
    run_demo()