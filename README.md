# NovaFit — Mini Health Tracker

![NovaFit Demo](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A simple daily health metrics tracker with CLI menu and compact GUI built for the Developers Institute Hackathon.

## ✨ Features

### �️ **Enhanced CLI Interface**
- 🎨 **Colorized Menu**: Beautiful color-coded interface with emojis
- 📝 **Smart Data Entry**: Enhanced validation and user-friendly prompts
- 🗑️ **Delete Entries**: Remove entries by date with confirmation
- 🔍 **Date Range Search**: Find entries within specific date ranges
- 📊 **Advanced Dashboard**: Comprehensive stats with trends analysis
- 🌤️ **Weather Integration**: Multi-city weather lookup with better UX
- 🧹 **Clear Screen**: Keep your terminal organized
- 🛡️ **Input Validation**: Robust error handling and data validation

### �️ **Professional GUI Interface**
- 📑 **Tabbed Layout**: Organized into Add Entry, View Data, Dashboard, and Tools
- 📅 **Date Picker**: Easy date selection with validation
- 🎚️ **Interactive Sliders**: Visual input for steps and water
- � **Visual Dashboard**: Rich statistics display with goal tracking
- 🎲 **Demo Data Generator**: Quick test data creation
- 📁 **File Dialogs**: Professional import/export with file selection
- 🌤️ **Weather Widget**: Integrated weather lookup
- 📈 **Data Visualization**: Enhanced treeview for viewing entries

### 💾 **Core Health Tracking**
- 📊 **Track Daily Metrics**: steps, water intake, calories, mood
- 💾 **SQLite Database**: Reliable local data storage
- � **JSON Import/Export**: Easy data backup and sharing
- 🎯 **Goal Tracking**: Monitor progress toward daily targets
- 📈 **Trend Analysis**: Compare recent performance with historical data

## 🚀 Quick Start

### Installation
```bash
pip install requests Faker
```

### Usage
```bash
# Demo test script
python test_improvements.py

# Interactive CLI
python novafit.py

# Professional GUI
python novafit.py --gui

# Generate demo data
python novafit.py --seed 7
```

## 📋 Menu Options

### 🖥️ **Enhanced CLI Menu**
```
NovaFit — Health Tracker
========================================
📝 Data Management:
  1) ➕ Add new entry
  2) 📋 List recent entries  
  3) 🗑️ Delete entry by date
📊 Analytics:
  4) 📈 Dashboard (stats & trends)
  5) 🔍 Search entries by date range
🌐 External:
  6) 🌤️ Weather lookup
💾 Import/Export:
  7) 📤 Export to JSON
  8) 📥 Import from JSON
  9) 🎲 Generate demo data
🖥️ Interface:
  10) 🖼️ Open GUI
  11) 🧹 Clear screen
  0) 👋 Exit
```

### 🖼️ **GUI Tabs**
- **➕ Add Entry**: Interactive form with sliders and validation
- **📋 View Entries**: Sortable table with all your health data
- **📊 Dashboard**: Visual statistics and goal tracking
- **🛠️ Tools**: Import/export, demo data, weather lookup

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
[
  {
    "date": "2025-10-14",
    "steps": 8500,
    "water_l": 2.5,
    "calories": 2000,
    "mood": "😊"
  }
]
```

## 🌟 Hackathon Requirements

✅ **Tech Stack**: Python, JSON, SQLite Database, Files, Requests API, Faker  
✅ **Open Source**: MIT License  
✅ **User Friendly**: Beginner-friendly code and interface  
✅ **Dual Interface**: Both CLI and GUI implementations  
✅ **Complete Solution**: All specified features implemented  

## 👤 Author

**Kevin 'Lirioth' Cusnir**  
📅 October 14, 2025  
🌍 TZ: Asia/Jerusalem

## 📄 License

MIT License - See [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT)

---

*Built with ❤️ for the Developers Institute Hackathon*