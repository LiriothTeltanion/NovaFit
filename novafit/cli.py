"""NovaFit CLI - Health Tracker"""
import sys
from pathlib import Path
import argparse
from datetime import date
from novafit.config import CONFIG, Colors, save_config, load_config, configure_ssl
from novafit.database import (
	init_db, add_entry, list_entries, clear_all_data
)
from novafit.export import seed_fake, initialize_sample_data, export_to_json, import_from_json, export_to_csv, import_from_csv
from novafit.utils import (
	show_help, validate_date, safe_input, format_entry_display, show_progress_bar, clear_screen
)
from novafit.weather import get_weather

# --- CLI Functions ---
def cli_menu():
	"""Main CLI menu loop interface."""
	print(f"{Colors.CYAN}Welcome to NovaFit! 🏃‍♂️{Colors.ENDC}")
	menu_options = [
		("📝 Data", [("➕ Add new entry", cli_add_entry), ("⚡ Quick entry for today", cli_quick_entry), 
					 ("📋 List recent entries", cli_list_entries), ("🗑️ Delete entry by date", cli_delete_entry)]),
		("📊 Analytics", [("📈 Dashboard", cli_dashboard), ("🔍 Search entries", cli_search_entries)]),
		("🌐 External", [("🌤️ Weather Report", cli_weather)]),
		("💾 Import/Export", [("📤 Export to JSON", cli_export), ("📥 Import from JSON", cli_import),
							  ("📊 Export to CSV", cli_export_csv), ("📋 Import from CSV", cli_import_csv)]),
		("🛠️ Tools", [("🎲 Generate demo data", cli_seed), ("🌟 Initialize sample data", cli_initialize_data),
					   ("🗑️ Clear all data", cli_clear_data), ("❓ Show help", show_help),
					   ("🧹 Clear screen", lambda: (clear_screen(), print(f"{Colors.GREEN}Screen cleared! ✨{Colors.ENDC}")))])
	]
	while True:
		try:
			print(f"\n{Colors.HEADER}{'='*40}{Colors.ENDC}")
			print(f"{Colors.BOLD}{Colors.BLUE}        NovaFit — Health Tracker{Colors.ENDC}")
			print(f"{Colors.HEADER}{'='*40}{Colors.ENDC}")
			option_num = 1
			option_map = {}
			for category, items in menu_options:
				color = Colors.GREEN if "Data" in category else Colors.CYAN if "Analytics" in category else Colors.WARNING if "External" in category else Colors.BLUE if "Import" in category else Colors.HEADER
				print(f"{color}{category}:{Colors.ENDC}")
				for title, func in items:
					print(f"  {option_num}) {title}")
					option_map[str(option_num)] = func
					option_num += 1
			print(f"{Colors.FAIL}  0) 👋 Exit{Colors.ENDC}")
			print(f"{Colors.HEADER}{'='*40}{Colors.ENDC}")
			choice = input(f"{Colors.BOLD}Choose option (0-{option_num-1}): {Colors.ENDC}").strip()
			if choice == "0":
				print(f"{Colors.GREEN}Goodbye! Stay healthy! 👋{Colors.ENDC}")
				break
			elif choice in option_map:
				option_map[choice]()
			else:
				print(f"{Colors.WARNING}Invalid choice! Please enter 0-{option_num-1} ⚠️{Colors.ENDC}")
		except (KeyboardInterrupt, EOFError):
			print(f"\n{Colors.GREEN}Goodbye! 👋{Colors.ENDC}")
			break

# --- Helpers CLI ---
def cli_quick_entry():
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
	print(f"\n{Colors.WARNING}🗑️ Delete Entry{Colors.ENDC}")
	print("=" * 15)
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
	confirm = input(f"⚠️ Delete entry for {date_str}? (yes/no): ").strip().lower()
	if confirm not in ['yes', 'y']:
		print(f"{Colors.CYAN}Operation cancelled{Colors.ENDC}")
		return
	try:
		import sqlite3
		conn = sqlite3.connect(CONFIG.get('db_path', './data/novafit.db'))
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
	print(f"\n{Colors.CYAN}🔍 Search Entries{Colors.ENDC}")
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
		import sqlite3
		conn = sqlite3.connect(CONFIG.get('db_path', './data/novafit.db'))
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
	print(f"\n{Colors.BLUE}📈 Health Dashboard{Colors.ENDC}")
	print("=" * 18)
	try:
		stats = list_entries(10)
		if not stats:
			print(f"{Colors.WARNING}No data available yet! Add some entries first 📝{Colors.ENDC}")
			return
		print(f"\n{Colors.GREEN}🎯 Daily Goals Progress:{Colors.ENDC}")
		latest_entry = list_entries(1)
		if latest_entry:
			latest = latest_entry[0]
			print(f"  {show_progress_bar(latest[1], CONFIG['step_goal'], '🚶 Steps')}")
			print(f"  {show_progress_bar(latest[2], CONFIG['water_goal'], '💧 Water')}")
		print(f"\n{Colors.GREEN}📊 Overall Statistics:{Colors.ENDC}")
		print(f"  📅 Days logged: {len(stats)}")
		print(f"  📆 Last entry: {stats[0][0] if stats else 'None'}")
		print(f"\n{Colors.CYAN}🚶 Steps Summary:{Colors.ENDC}")
		total_steps = sum(entry[1] for entry in stats)
		print(f"  📈 Total steps: {total_steps:,}")
		print(f"  📊 Average/day: {total_steps // len(stats):,}")
		goal_days = sum(1 for entry in stats if entry[1] >= CONFIG['step_goal'])
		goal_percentage = (goal_days / len(stats)) * 100 if stats else 0
		print(f"  🎯 Days reaching 10k steps: {goal_days}/{len(stats)} ({goal_percentage:.1f}%)")
		print(f"\n{Colors.BLUE}💧 Water Summary:{Colors.ENDC}")
		total_water = sum(entry[2] for entry in stats)
		print(f"  📈 Total water: {total_water}L")
		print(f"  📊 Average/day: {total_water / len(stats):.1f}L")
		water_goal_days = sum(1 for entry in stats if entry[2] >= CONFIG['water_goal'])
		water_goal_percentage = (water_goal_days / len(stats)) * 100 if stats else 0
		print(f"  🎯 Days reaching 2L goal: {water_goal_days}/{len(stats)} ({water_goal_percentage:.1f}%)")
	except Exception as e:
		print(f"{Colors.FAIL}❌ Error generating dashboard: {e}{Colors.ENDC}")
def cli_weather():
	print(f"\n{Colors.CYAN}🌤️ Weather Lookup{Colors.ENDC}")
	cities = list(CONFIG.get('city_coords', {'beersheba': (31.2529, 34.7915)}).keys())
	print("Available cities:")
	for i, city in enumerate(cities, 1):
		print(f"  {i}. {city.title()}")
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
def cli_export_import(operation, format_type):
	icons = {"export": {"json": "💾", "csv": "📊"}, "import": {"json": "", "csv": ""}}
	action = "Export" if operation == "export" else "Import"
	icon = "📤" if operation == "export" else "📥"
	print(f"\n{Colors.BLUE}{icon} {action} Data{' to CSV' if format_type == 'csv' and operation == 'export' else ' from CSV' if format_type == 'csv' else ''}{Colors.ENDC}")
	use_custom = input("Use custom file path? (y/n, default n): ").strip().lower()
	default_path = Path(CONFIG.get('export_path', './data/novafit_export.json')) if format_type == "json" else Path(CONFIG.get('csv_export_path', './data/novafit_export.csv'))
	if use_custom in ['y', 'yes']:
		custom_path = input(f"Enter file path (default {default_path}): ").strip()
		file_path = Path(custom_path) if custom_path else default_path
	else:
		file_path = default_path
	if operation == "export":
		func = export_to_json if format_type == "json" else export_to_csv
		count = func(file_path)
		print(f"{Colors.GREEN}✅ Exported {count} records to {file_path} {icons['export'][format_type]}{Colors.ENDC}")
		if count > 0:
			file_size = file_path.stat().st_size / 1024
			print(f"  📁 File size: {file_size:.1f} KB")
			if format_type == "csv":
				print(f"  💡 Tip: You can open this file in Excel, Google Sheets, or any spreadsheet application!")
	else:
		if not file_path.exists():
			print(f"{Colors.WARNING}⚠️ File not found: {file_path}{Colors.ENDC}")
			return
		func = import_from_json if format_type == "json" else import_from_csv
		count = func(file_path)
		print(f"{Colors.GREEN}✅ Imported {count} new records{Colors.ENDC}")
def cli_export():
	cli_export_import("export", "json")
def cli_import():
	cli_export_import("import", "json")
def cli_export_csv():
	cli_export_import("export", "csv")
def cli_import_csv():
	cli_export_import("import", "csv")
def cli_data_operation(operation_type):
	operations = {
		"seed": {
			"title": "🎲 Generate Demo Data",
			"warning_color": Colors.WARNING,
			"description": "Generate realistic fake health tracking data for testing.",
			"ranges": "Steps: 2,000-15,000, Water: 1.0-4.0L, Calories: 1,200-3,000",
			"prompt_input": True,
			"confirmation": "Generate {n} days of fake data?",
			"processing": "🎲 Generating fake data...",
			"success": "✅ Generated {count} fake entries 🎲"
		},
		"sample": {
			"title": "🌟 Initialize Sample Data",
			"warning_color": Colors.CYAN,
			"description": "Create a week of realistic sample health data to get you started.\nThis is perfect for new users to see how the application works.",
			"ranges": None,
			"prompt_input": False,
			"confirmation": "Initialize sample data? This will overwrite any existing data for the sample dates.",
			"processing": "🌟 Initializing sample data...",
			"success": "✅ Initialized {count} sample entries 🌟\n💡 You now have a week of sample data to explore the application!"
		},
		"clear": {
			"title": "🗑️ Clear All Data",
			"warning_color": Colors.FAIL,
			"description": "⚠️  WARNING: This will permanently delete ALL your health data!\nThis action cannot be undone. Make sure to export your data first if you want to keep it.",
			"ranges": None,
			"prompt_input": False,
			"confirmation": "Are you sure you want to delete all data?",
			"processing": "🗑️ Clearing all data...",
			"success": "✅ Deleted {count} entries\n💡 Your database is now empty and ready for fresh data."
		}
	}
	op = operations[operation_type]
	print(f"\n{op['warning_color']}{op['title']}{Colors.ENDC}")
	print(op["description"])
	if op["ranges"]:
		print(f"\nData ranges: {op['ranges']}")
	n = None
	if op["prompt_input"]:
		n = safe_input("How many days of data to generate? (1-30): ", int, validator=lambda x: 1 <= x <= 30)
		if n is None: return
	confirm_text = op["confirmation"].format(n=n) if n else op["confirmation"]
	confirm = input(f"⚠️ {confirm_text} (yes/no): ").strip().lower()
	if confirm not in ['yes', 'y']:
		print(f"{Colors.CYAN}Operation cancelled{Colors.ENDC}")
		return
	if operation_type == "clear":
		confirm2 = input("Type 'DELETE ALL' to confirm: ").strip()
		if confirm2 != 'DELETE ALL':
			print(f"{Colors.CYAN}Operation cancelled - confirmation phrase not matched{Colors.ENDC}")
			return
	print(op["processing"])
	if operation_type == "seed":
		count = seed_fake(n)
	elif operation_type == "sample":
		count = initialize_sample_data()
	else:  # clear
		count = clear_all_data()
	success_msg = op["success"].format(count=count)
	for line in success_msg.split('\n'):
		print(f"{Colors.GREEN if line.startswith('✅') else Colors.BLUE}{line}{Colors.ENDC}")
def cli_seed():
	cli_data_operation("seed")
def cli_initialize_data():
	cli_data_operation("sample")
def cli_clear_data():
	cli_data_operation("clear")

def main():
	parser = argparse.ArgumentParser(description="NovaFit — Mini Health Tracker")
	parser.add_argument("--seed", type=int, help="Seed N days of fake data")
	args = parser.parse_args()
	init_db(Path(CONFIG.get('db_path', './data/novafit.db')))
	if args.seed:
		count = seed_fake(args.seed)
		print(f"Generated {count} fake entries 🎲")
		return
	cli_menu()

if __name__ == "__main__":
	main()
