"""Utility functions for NovaFit

This module provides helper functions for:
- Input validation (dates, numbers, etc.)
- User input handling with error recovery
- Display formatting (entries, progress bars)
- Screen management
- Help information
"""

import os
from datetime import datetime
from typing import Optional, Callable, Any, Union, Tuple

from .config import Colors, CONFIG

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_date(date_str: str) -> bool:
    """Validate date string format (YYYY-MM-DD).
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        bool: True if valid date format, False otherwise
        
    Example:
        >>> validate_date("2025-10-15")
        True
        >>> validate_date("15-10-2025")
        False
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_positive_number(value: Any, allow_zero: bool = True) -> bool:
    """Validate that a value is a positive number.
    
    Args:
        value: Value to validate
        allow_zero (bool): Whether to allow zero (default: True)
        
    Returns:
        bool: True if valid positive number, False otherwise
    """
    try:
        num = float(value)
        return num >= 0 if allow_zero else num > 0
    except (ValueError, TypeError):
        return False


def validate_steps(steps: int) -> bool:
    """Validate step count (must be non-negative).
    
    Args:
        steps (int): Step count to validate
        
    Returns:
        bool: True if valid (>= 0), False otherwise
    """
    return isinstance(steps, int) and steps >= 0


def validate_water(water_l: float) -> bool:
    """Validate water intake (must be non-negative, reasonable max).
    
    Args:
        water_l (float): Water in liters to validate
        
    Returns:
        bool: True if valid (0-10L range), False otherwise
    """
    try:
        water = float(water_l)
        return 0 <= water <= 10.0  # Reasonable daily limit
    except (ValueError, TypeError):
        return False


# =============================================================================
# SAFE INPUT HANDLING
# =============================================================================

def safe_input(prompt: str, input_type: type = str, default: Any = None, 
               validator: Optional[Callable] = None) -> Any:
    """Get user input with type conversion, validation, and error handling.
    
    This function provides a robust way to get user input with:
    - Type conversion (int, float, str)
    - Optional default values
    - Custom validation functions
    - Error recovery (retry on invalid input)
    - Graceful handling of Ctrl+C
    
    Args:
        prompt (str): Input prompt to display to user
        input_type (type): Expected type (int, float, or str)
        default: Value to return if user presses Enter (default: None)
        validator (callable, optional): Function to validate converted value
        
    Returns:
        Converted and validated user input, or default/None on cancellation
        
    Example:
        >>> age = safe_input("Enter age: ", int, validator=lambda x: x > 0)
        >>> date = safe_input("Date: ", str, validator=validate_date)
        >>> water = safe_input("Water (L): ", float, default=2.0)
    """
    while True:
        try:
            value = input(prompt).strip()
            
            # Handle empty input
            if not value:
                if default is not None:
                    return default
                print(f"  {Colors.WARNING}⚠️ This field is required{Colors.ENDC}")
                continue
            
            # Type conversion
            if input_type == int:
                value = int(value)
            elif input_type == float:
                value = float(value)
            # str doesn't need conversion
            
            # Custom validation
            if validator and not validator(value):
                print(f"  {Colors.FAIL}⚠️ Invalid format or value{Colors.ENDC}")
                continue
            
            return value
            
        except ValueError:
            print(f"  {Colors.FAIL}⚠️ Please enter a valid {input_type.__name__}{Colors.ENDC}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {Colors.WARNING}⚠️ Operation cancelled{Colors.ENDC}")
            return None


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user to confirm an action (yes/no).
    
    Args:
        message (str): Confirmation message
        default (bool): Default choice if user presses Enter
        
    Returns:
        bool: True if confirmed, False otherwise
        
    Example:
        >>> if confirm_action("Delete all data?"):
        >>>     delete_all()
    """
    default_str = "[Y/n]" if default else "[y/N]"
    response = input(f"{message} {default_str}: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']


# =============================================================================
# FORMATTING AND DISPLAY
# =============================================================================

def format_entry_display(entry: Union[Tuple, dict]) -> str:
    """Format a health entry for display in terminal.
    
    Adds emojis, colors, and goal indicators to make entries readable.
    
    Args:
        entry: Tuple (date, steps, water, calories, mood) or dict
        
    Returns:
        str: Formatted string with colors and emojis
        
    Example:
        >>> entry = ("2025-10-15", 10000, 2.5, 2000, "😊")
        >>> print(format_entry_display(entry))
        📅 2025-10-15 | 🚶 10,000 ✅ | 💧 2.5L ✅, 2,000cal 😊
    """
    # Handle both tuple and dict formats
    if isinstance(entry, dict):
        date_str = entry['date']
        steps = entry['steps']
        water = entry['water_l']
        calories = entry.get('calories')
        mood = entry.get('mood')
    else:
        date_str, steps, water, calories, mood = entry
    
    # Goal indicators
    step_icon = "✅" if steps >= CONFIG["step_goal"] else "⚠️"
    water_icon = "✅" if water >= CONFIG["water_goal"] else "⚠️"
    
    # Optional fields
    mood_str = f" {mood}" if mood else " 😐"
    cal_str = f", {calories:,}cal" if calories else ""
    
    return (
        f"📅 {date_str} | "
        f"🚶 {steps:,} {step_icon} | "
        f"💧 {water}L {water_icon}"
        f"{cal_str}"
        f"{mood_str}"
    )


def show_progress_bar(current: Union[int, float], goal: Union[int, float], 
                     label: str, width: int = 10) -> str:
    """Create a visual progress bar for goal tracking.
    
    Args:
        current: Current value
        goal: Target goal value
        label: Label to display before bar
        width (int): Width of bar in characters (default: 10)
        
    Returns:
        str: Formatted progress bar string
        
    Example:
        >>> bar = show_progress_bar(7500, 10000, "Steps")
        >>> print(bar)
        Steps: ███████░░░ 75.0% (7500/10000)
    """
    if goal <= 0:
        percentage = 0
    else:
        percentage = min(100, (current / goal) * 100)
    
    filled = int(percentage / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    
    return f"{label}: {bar} {percentage:.1f}% ({current}/{goal})"


def format_number(num: Union[int, float], decimals: int = 0) -> str:
    """Format number with thousand separators.
    
    Args:
        num: Number to format
        decimals (int): Number of decimal places (default: 0)
        
    Returns:
        str: Formatted number string
        
    Example:
        >>> format_number(10000)
        '10,000'
        >>> format_number(2.5, 1)
        '2.5'
    """
    if decimals > 0:
        return f"{num:,.{decimals}f}"
    return f"{int(num):,}"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length (default: 50)
        suffix (str): Suffix to add when truncated (default: "...")
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# =============================================================================
# SCREEN MANAGEMENT
# =============================================================================

def clear_screen() -> None:
    """Clear the terminal screen.
    
    Works on both Windows (cls) and Unix-like systems (clear).
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str, width: int = 40, char: str = "=") -> None:
    """Print a formatted header with title.
    
    Args:
        title (str): Header title
        width (int): Total width of header (default: 40)
        char (str): Character to use for border (default: "=")
        
    Example:
        >>> print_header("NovaFit Dashboard")
        ========================================
        NovaFit Dashboard
        ========================================
    """
    border = char * width
    print(f"\n{Colors.HEADER}{border}{Colors.ENDC}")
    print(f"{Colors.BOLD}{title.center(width)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{border}{Colors.ENDC}\n")


def print_section(title: str, color: str = Colors.CYAN) -> None:
    """Print a section header.
    
    Args:
        title (str): Section title
        color (str): ANSI color code (default: Colors.CYAN)
    """
    print(f"\n{color}{title}{Colors.ENDC}")
    print(f"{color}{'─' * len(title)}{Colors.ENDC}")


# =============================================================================
# HELP AND INFORMATION
# =============================================================================

def show_help() -> None:
    """Display comprehensive help information.
    
    Shows usage guide, tips, and command-line options.
    """
    help_text = f"""
{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗
║                    NovaFit — User Guide                     ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.GREEN}📝 Data Entry:{Colors.ENDC}
  • Use YYYY-MM-DD format for dates
  • Steps and water are required fields
  • Calories and mood are optional
  • Press Enter to use default values

{Colors.CYAN}🎯 Goals:{Colors.ENDC}
  • Steps: {CONFIG['step_goal']:,} steps/day
  • Water: {CONFIG['water_goal']}L/day
  • Goal indicators: ✅ = achieved, ⚠️ = below goal

{Colors.WARNING}💡 Tips:{Colors.ENDC}
  • Use GUI mode (--gui) for easier data entry
  • Export data regularly for backup
  • Use quick entry for today's data
  • Generate demo data to test features

{Colors.BLUE}🔧 Command Line:{Colors.ENDC}
  • python novafit.py         → CLI menu
  • python novafit.py --gui   → GUI interface
  • python novafit.py --seed 7 → Generate 7 days of demo data

{Colors.HEADER}Press Enter to continue...{Colors.ENDC}"""
    
    print(help_text)
    input()


def show_welcome() -> None:
    """Display welcome message on startup."""
    print(f"""
{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗
║                      🏃 Welcome to NovaFit! 🏃                ║
║                  Your Personal Health Tracker               ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
""")


def show_goodbye() -> None:
    """Display goodbye message on exit."""
    print(f"""
{Colors.GREEN}╔══════════════════════════════════════════════════════════════╗
║                  👋 Stay healthy! See you soon! 👋            ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
""")
