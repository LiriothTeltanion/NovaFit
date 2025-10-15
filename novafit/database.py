"""Database operations for NovaFit

This module handles all SQLite database operations including:
- Database initialization and schema creation
- CRUD operations (Create, Read, Update, Delete)
- Statistics and analytics queries
- Data validation and error handling
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Tuple, Dict
from datetime import date, timedelta

from .config import DB_PATH, DATA_DIR

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db(path: Path = DB_PATH) -> None:
    """Initialize SQLite database with health logs table.
    
    Creates the database file and logs table if they don't exist.
    The table stores daily health metrics with a unique constraint on date.
    
    Args:
        path (Path): Path to the database file (default: DB_PATH from config)
    
    Table Schema:
        - id: INTEGER PRIMARY KEY (auto-increment)
        - date: TEXT UNIQUE (format: YYYY-MM-DD)
        - steps: INTEGER (number of steps walked)
        - water_l: REAL (liters of water consumed)
        - calories: INTEGER (calories consumed, optional)
        - mood: TEXT (emoji or text description, optional)
    """
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


# =============================================================================
# CRUD OPERATIONS
# =============================================================================

def add_entry(date_str: str, steps: int, water_l: float, 
              calories: Optional[int] = None, mood: Optional[str] = None) -> None:
    """Add or update a daily health entry.
    
    If an entry for the given date already exists, it will be replaced.
    This uses SQLite's INSERT OR REPLACE functionality.
    
    Args:
        date_str (str): Date in YYYY-MM-DD format
        steps (int): Number of steps walked
        water_l (float): Liters of water consumed
        calories (int, optional): Calories consumed
        mood (str, optional): Mood emoji or description
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO logs (date, steps, water_l, calories, mood) VALUES (?, ?, ?, ?, ?)", 
        (date_str, steps, water_l, calories, mood)
    )
    conn.commit()
    conn.close()


def get_entry(date_str: str) -> Optional[Dict]:
    """Get a specific entry by date.
    
    Args:
        date_str (str): Date in YYYY-MM-DD format
        
    Returns:
        dict or None: Entry data as dictionary, or None if not found
            Keys: id, date, steps, water_l, calories, mood
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, date, steps, water_l, calories, mood FROM logs WHERE date = ?",
        (date_str,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'date': row[1],
            'steps': row[2],
            'water_l': row[3],
            'calories': row[4],
            'mood': row[5]
        }
    return None


def update_entry(date_str: str, steps: int, water_l: float,
                 calories: Optional[int] = None, mood: Optional[str] = None) -> bool:
    """Update an existing entry.
    
    Args:
        date_str (str): Date of entry to update
        steps (int): New step count
        water_l (float): New water amount
        calories (int, optional): New calorie count
        mood (str, optional): New mood
        
    Returns:
        bool: True if entry was updated, False if entry doesn't exist
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE logs 
        SET steps = ?, water_l = ?, calories = ?, mood = ?
        WHERE date = ?
    """, (steps, water_l, calories, mood, date_str))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_entry(date_str: str) -> bool:
    """Delete an entry by date.
    
    Args:
        date_str (str): Date of entry to delete (YYYY-MM-DD)
        
    Returns:
        bool: True if entry was deleted, False if entry doesn't exist
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs WHERE date = ?", (date_str,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# =============================================================================
# QUERY OPERATIONS
# =============================================================================

def list_entries(limit: int = 10) -> List[Tuple]:
    """Get recent entries from database.
    
    Returns entries ordered by date (newest first).
    
    Args:
        limit (int): Maximum number of entries to return (default: 10)
        
    Returns:
        list of tuples: Each tuple contains (date, steps, water_l, calories, mood)
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT date, steps, water_l, calories, mood FROM logs ORDER BY date DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return rows


def get_all_entries() -> List[Dict]:
    """Get all entries as list of dictionaries.
    
    Returns:
        list of dict: All entries with keys: id, date, steps, water_l, calories, mood
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, steps, water_l, calories, mood FROM logs ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [{
        'id': row[0],
        'date': row[1],
        'steps': row[2],
        'water_l': row[3],
        'calories': row[4],
        'mood': row[5]
    } for row in rows]


def search_entries(start_date: str, end_date: str) -> List[Tuple]:
    """Search entries within a date range.
    
    Args:
        start_date (str): Start date (YYYY-MM-DD, inclusive)
        end_date (str): End date (YYYY-MM-DD, inclusive)
        
    Returns:
        list of tuples: Matching entries (date, steps, water_l, calories, mood)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, steps, water_l, calories, mood 
        FROM logs 
        WHERE date BETWEEN ? AND ? 
        ORDER BY date DESC
    """, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return rows


# =============================================================================
# STATISTICS
# =============================================================================

def get_dashboard_stats() -> Dict:
    """Calculate comprehensive dashboard statistics.
    
    Aggregates data from all entries to provide summary statistics
    including totals, averages, and the most recent entry date.
    
    Returns:
        dict: Statistics with keys:
            - count: Total number of entries
            - total_steps: Sum of all steps
            - avg_steps: Average steps per day (rounded)
            - total_water: Sum of water in liters
            - avg_water: Average water per day (1 decimal)
            - last_date: Most recent entry date
    """
    conn = sqlite3.connect(DB_PATH)
    stats = conn.execute(
        "SELECT COUNT(*), SUM(steps), SUM(water_l), MAX(date) FROM logs"
    ).fetchone()
    count, total_steps, total_water, last_date = stats
    
    if count == 0:
        return {
            "count": 0,
            "total_steps": 0,
            "avg_steps": 0,
            "total_water": 0,
            "avg_water": 0,
            "last_date": "None"
        }
    
    avg_steps = int(total_steps / count) if total_steps else 0
    avg_water = round(total_water / count, 1) if total_water else 0
    conn.close()
    
    return {
        "count": count,
        "total_steps": total_steps or 0,
        "avg_steps": avg_steps,
        "total_water": total_water or 0,
        "avg_water": avg_water,
        "last_date": last_date or "None"
    }


def get_stats_summary() -> Dict:
    """Get extended statistics including min/max values.
    
    Returns:
        dict: Extended statistics with additional metrics
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            AVG(steps) as avg_steps,
            AVG(water_l) as avg_water,
            AVG(calories) as avg_calories,
            MAX(steps) as max_steps,
            MIN(steps) as min_steps,
            MAX(water_l) as max_water,
            MIN(water_l) as min_water
        FROM logs
    """)
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[0] == 0:
        return {
            'total_entries': 0,
            'avg_steps': 0,
            'avg_water': 0,
            'avg_calories': 0,
            'max_steps': 0,
            'min_steps': 0,
            'max_water': 0,
            'min_water': 0
        }
    
    return {
        'total_entries': row[0],
        'avg_steps': round(row[1], 0) if row[1] else 0,
        'avg_water': round(row[2], 2) if row[2] else 0,
        'avg_calories': round(row[3], 0) if row[3] else 0,
        'max_steps': row[4] or 0,
        'min_steps': row[5] or 0,
        'max_water': row[6] or 0,
        'min_water': row[7] or 0
    }


# =============================================================================
# DATA MANAGEMENT
# =============================================================================

def clear_all_data() -> int:
    """Delete all entries from the database.
    
    WARNING: This operation cannot be undone!
    
    Returns:
        int: Number of entries deleted
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs")
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected


def count_entries() -> int:
    """Get total number of entries in database.
    
    Returns:
        int: Total entry count
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM logs")
    count = cursor.fetchone()[0]
    conn.close()
    return count
