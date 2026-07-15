# NovaFit — Mini Health Tracker

![NovaFit Demo](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A simple daily health metrics tracker with enhanced CLI menu and professional dark-themed GUI built for the Developers Institute Hackathon.

## ✨ Features

### 🖥️ **Enhanced CLI Interface**
- 🎨 **Colorized Menu**: Beautiful color-coded interface with emojis
- 📝 **Smart Data Entry**: Enhanced validation and user-friendly prompts
- ⚡ **Quick Entry**: Fast data entry for today with smart defaults
- 🗑️ **Delete Entries**: Remove entries by date with confirmation
- 🔍 **Date Range Search**: Find entries within specific date ranges
- 📊 **Advanced Dashboard**: Comprehensive stats with trends analysis
- 🌤️ **Weather Integration**: Multi-city weather lookup with better UX
- 📤 **Data Export**: Export to both JSON and CSV formats
- 📥 **Data Import**: Import from JSON and CSV files
- 🎲 **Demo Data**: Generate realistic test data with Faker
- 🌟 **Sample Data**: Initialize with a week of sample entries
- 🗑️ **Data Management**: Clear all data with double confirmation
- 🧹 **Clear Screen**: Keep your terminal organized
- 🛡️ **Input Validation**: Robust error handling and data validation
- ❓ **Help System**: Built-in help and user guidance

### 🖼️ **Professional GUI Interface**
- 📑 **Tabbed Layout**: Organized into Add Entry, View Data, Dashboard, and Tools
- 📅 **Date Picker**: Easy date selection with validation
- 🎚️ **Interactive Sliders**: Visual input for steps and water
- 📊 **Visual Dashboard**: Rich statistics display with goal tracking
- 🎲 **Demo Data Generator**: Quick test data creation
- 📁 **File Dialogs**: Professional import/export with file selection
- 🌤️ **Weather Widget**: Integrated weather lookup
- 📈 **Data Visualization**: Enhanced treeview for viewing entries
- 🌙 **Enhanced Dark Theme**: Professional dark mode with custom styling
- 🎨 **Theme Toggle**: Switch between light and dark themes with live preview
- ✨ **Modern Styling**: Improved contrast and readability in all modes

### 💾 **Core Health Tracking**
- 📊 **Track Daily Metrics**: steps, water intake, calories, mood
- 💾 **SQLite Database**: Reliable local data storage
- 📁 **JSON Import/Export**: Easy data backup and sharing
- 📄 **CSV Export/Import**: Spreadsheet-compatible data format
- 🎯 **Goal Tracking**: Monitor progress toward daily targets
- 📈 **Trend Analysis**: Compare recent performance with historical data
- 🌟 **Sample Data**: Pre-loaded realistic examples for new users
- 🎲 **Demo Generation**: Create test data with Faker library

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Usage
```bash
# Interactive CLI
python -m novafit.cli

# Professional GUI
python -m novafit.gui

# Generate demo data (7 entries) from CLI
python -m novafit.cli --seed 7

# Windows Quick Launch
./run_cli.bat  # Launch CLI
./run_gui.bat  # Launch GUI
```

## 📋 Menu Options

### 🖥️ **Enhanced CLI Menu**
```
NovaFit — Health Tracker
========================================
📝 Data:
  1) ➕ Add new entry
  2) ⚡ Quick entry for today
  3) 📋 List recent entries
  4) 🗑️ Delete entry by date
📊 Analytics:
  5) 📈 Dashboard
  6) 🔍 Search entries
🌐 External:
  7) 🌤️ Weather Report
💾 Import/Export:
  8) 📤 Export to JSON
  9) 📥 Import from JSON
  10) 📊 Export to CSV
  11) 📋 Import from CSV
🛠️ Tools:
  12) 🎲 Generate demo data
  13) 🌟 Initialize sample data
  14) 🗑️ Clear all data
  15) 🖼️ Open GUI Interface
  16) 🧹 Clear screen
  17) ❓ Show help
  0) 👋 Exit
```

### 🖼️ **GUI Tabs**
- **➕ Add Entry**: Interactive form with sliders and validation
- **📋 View Entries**: Sortable table with all your health data
- **📊 Dashboard**: Visual statistics and goal tracking
- **🛠️ Tools**: Import/export (JSON/CSV), demo data, sample data initialization, clear all data, weather lookup, and theme settings

## 🗂️ Data Structure

**Database**: `./data/novafit.db` (SQLite)
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    date TEXT UNIQUE,
    steps INTEGER,
    water_l REAL,
    calories INTEGER,
    mood TEXT
);
```

**Export**: `./data/novafit_export.json`
```json
{
  "metadata": {
    "export_date": "2025-10-15 10:30:00",
    "total_entries": 7,
    "application": "NovaFit Health Tracker",
    "version": "1.0"
  },
  "health_data": [
    {
      "date": "2025-10-14",
      "steps": 8500,
      "water_l": 2.5,
      "calories": 2000,
      "mood": "😊"
    }
  ]
}
```

**CSV Export**: `./data/novafit_export.csv`
```csv
Date,Steps,Water (L),Calories,Mood
2025-10-14,8500,2.5,2000,😊
2025-10-13,12000,3.0,2200,💪
```

## 🌟 Hackathon Requirements

✅ **Tech Stack**: Python, JSON, SQLite Database, Files, Requests API, Faker  
✅ **Open Source**: MIT License  
✅ **User Friendly**: Beginner-friendly code and interface  
✅ **Dual Interface**: Both CLI and GUI implementations  
✅ **Complete Solution**: All specified features implemented  
✅ **Data Portability**: Multiple export formats (JSON, CSV)  
✅ **Sample Data**: Pre-loaded examples and demo data generation  

## 👤 Author

**Kevin 'Lirioth' Cusnir**  
📅 October 14, 2025  
🌍 TZ: Asia/Jerusalem

## 📄 License

MIT License - See [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT)

---

*Built with ❤️ for the Developers Institute Hackathon*