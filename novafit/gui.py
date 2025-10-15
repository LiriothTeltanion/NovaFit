"""NovaFit GUI - Health Tracker"""
from novafit.config import CONFIG, Colors, save_config, load_config, configure_ssl, DATA_DIR, CITY_COORDS
from novafit.database import (
	init_db, add_entry, list_entries, clear_all_data, get_dashboard_stats
)
from novafit.export import (
	seed_fake, initialize_sample_data,
	export_to_json as do_export_json,
	import_from_json as do_import_json,
	export_to_csv as do_export_csv,
	import_from_csv as do_import_csv,
)
from novafit.utils import (
	show_help, validate_date, safe_input, format_entry_display, show_progress_bar, clear_screen
)
from novafit.weather import get_weather
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from pathlib import Path

# --- GUI Class ---
class NovaFitGUI:
	def apply_dark_theme(self):
		"""Apply a modern dark theme with improved colors and gradients."""
		self.style.theme_use('clam')
		colors = {
			'bg_primary': '#0d1117',
			'bg_secondary': '#161b22',
			'bg_tertiary': '#21262d',
			'surface': '#30363d',
			'surface_hover': '#373e47',
			'surface_active': '#444c56',
			'accent': '#1f6feb',
			'accent_hover': '#388bfd',
			'success': '#238636',
			'warning': '#d29922',
			'danger': '#da3633',
			'text_primary': '#f0f6fc',
			'text_secondary': '#8b949e',
			'text_muted': '#6e7681',
			'border': '#30363d',
			'border_muted': '#21262d'
		}
		self.root.configure(bg=colors['bg_primary'])
		self.style.configure('TFrame', background=colors['bg_primary'], borderwidth=0, relief='flat')
		self.style.configure('TLabel', background=colors['bg_primary'], foreground=colors['text_primary'], font=('Segoe UI', 9))
		self.style.configure('TButton', background=colors['surface'], foreground=colors['text_primary'], borderwidth=1, relief='flat', focuscolor='none', padding=(12, 8), font=('Segoe UI', 9))
		self.style.map('TButton', background=[('active', colors['surface_hover']), ('pressed', colors['surface_active']), ('focus', colors['surface_hover'])], bordercolor=[('active', colors['accent']), ('focus', colors['accent'])])
		self.style.configure('TEntry', fieldbackground=colors['surface'], foreground=colors['text_primary'], borderwidth=1, relief='flat', insertcolor=colors['text_primary'], selectbackground=colors['accent'], selectforeground=colors['text_primary'])
		self.style.map('TEntry', bordercolor=[('focus', colors['accent']), ('!focus', colors['border'])], lightcolor=[('focus', colors['accent'])])
		self.style.configure('TCombobox', fieldbackground=colors['surface'], foreground=colors['text_primary'], borderwidth=1, relief='flat', arrowcolor=colors['text_secondary'], selectbackground=colors['accent'])
		self.style.map('TCombobox', bordercolor=[('focus', colors['accent']), ('!focus', colors['border'])], lightcolor=[('focus', colors['accent'])])
		self.style.configure('TNotebook', background=colors['bg_primary'], borderwidth=0, tabmargins=[2, 5, 2, 0])
		self.style.configure('TNotebook.Tab', background=colors['bg_secondary'], foreground=colors['text_secondary'], padding=[16, 10], borderwidth=1, focuscolor='none')
		self.style.map('TNotebook.Tab', background=[('selected', colors['bg_tertiary']), ('active', colors['surface'])], foreground=[('selected', colors['text_primary']), ('active', colors['text_primary'])], expand=[('selected', [1, 1, 1, 0])])
		self.style.configure('TLabelFrame', background=colors['bg_primary'], foreground=colors['text_primary'], borderwidth=1, relief='solid', bordercolor=colors['border'])
		self.style.configure('TLabelFrame.Label', background=colors['bg_primary'], foreground=colors['text_primary'], font=('Segoe UI', 9, 'bold'))
		self.style.configure('Treeview', background=colors['bg_tertiary'], foreground=colors['text_primary'], fieldbackground=colors['bg_tertiary'], borderwidth=1, relief='flat')
		self.style.configure('Treeview.Heading', background=colors['surface'], foreground=colors['text_primary'], borderwidth=1, relief='flat', font=('Segoe UI', 9, 'bold'))
		self.style.map('Treeview.Heading', background=[('active', colors['surface_hover'])], relief=[('active', 'flat')])
		self.style.map('Treeview', background=[('selected', colors['accent'])], foreground=[('selected', colors['text_primary'])])
		self.style.configure('TScale', background=colors['bg_primary'], troughcolor=colors['surface'], borderwidth=0, sliderthickness=16, gripcount=0)
		self.style.map('TScale', troughcolor=[('active', colors['surface_hover'])])
		self.style.configure('TCheckbutton', background=colors['bg_primary'], foreground=colors['text_primary'], focuscolor='none', borderwidth=0, font=('Segoe UI', 9))
		self.style.map('TCheckbutton', background=[('active', colors['bg_primary'])])
		self.style.configure('Vertical.TScrollbar', background=colors['surface'], troughcolor=colors['bg_tertiary'], borderwidth=0, arrowcolor=colors['text_secondary'], width=12)
		self.style.map('Vertical.TScrollbar', background=[('active', colors['surface_hover'])])
		if hasattr(self, 'stats_text'):
			self.stats_text.configure(bg=colors['bg_tertiary'], fg=colors['text_primary'], insertbackground=colors['text_primary'], selectbackground=colors['accent'], selectforeground=colors['text_primary'], borderwidth=1, relief='flat', font=('Consolas', 9))
		if hasattr(self, 'weather_text'):
			self.weather_text.configure(bg=colors['bg_tertiary'], fg=colors['text_primary'], insertbackground=colors['text_primary'], selectbackground=colors['accent'], selectforeground=colors['text_primary'], borderwidth=1, relief='flat', font=('Segoe UI', 9))
		if hasattr(self, 'progress_canvas'):
			self.progress_canvas.configure(bg=colors['bg_tertiary'], highlightbackground=colors['border'], highlightthickness=1)

	def apply_light_theme(self):
		"""Apply a modern light theme with improved colors."""
		self.style.theme_use('clam')
		colors = {
			'bg_primary': '#ffffff',
			'bg_secondary': '#f6f8fa',
			'bg_tertiary': '#f1f3f4',
			'surface': '#ffffff',
			'surface_hover': '#f6f8fa',
			'surface_active': '#eaeef2',
			'accent': '#0969da',
			'accent_hover': '#0860ca',
			'success': '#1a7f37',
			'warning': '#9a6700',
			'danger': '#d1242f',
			'text_primary': '#24292f',
			'text_secondary': '#656d76',
			'text_muted': '#8b949e',
			'border': '#d0d7de',
			'border_muted': '#eaeef2'
		}
		self.root.configure(bg=colors['bg_primary'])
		self.style.configure('TFrame', background=colors['bg_primary'], borderwidth=0, relief='flat')
		self.style.configure('TLabel', background=colors['bg_primary'], foreground=colors['text_primary'], font=('Segoe UI', 9))
		self.style.configure('TButton', background=colors['surface'], foreground=colors['text_primary'], borderwidth=1, relief='flat', focuscolor='none', padding=(12, 8), font=('Segoe UI', 9))
		self.style.map('TButton', background=[('active', colors['surface_hover']), ('pressed', colors['surface_active']), ('focus', colors['surface_hover'])], bordercolor=[('active', colors['accent']), ('focus', colors['accent'])])
		self.style.configure('TEntry', fieldbackground=colors['surface'], foreground=colors['text_primary'], borderwidth=1, relief='flat', insertcolor=colors['text_primary'], selectbackground=colors['accent'], selectforeground='white')
		self.style.map('TEntry', bordercolor=[('focus', colors['accent']), ('!focus', colors['border'])], lightcolor=[('focus', colors['accent'])])
		self.style.configure('TCombobox', fieldbackground=colors['surface'], foreground=colors['text_primary'], borderwidth=1, relief='flat', arrowcolor=colors['text_secondary'], selectbackground=colors['accent'])
		self.style.map('TCombobox', bordercolor=[('focus', colors['accent']), ('!focus', colors['border'])], lightcolor=[('focus', colors['accent'])])
		self.style.configure('TNotebook', background=colors['bg_primary'], borderwidth=0, tabmargins=[2, 5, 2, 0])
		self.style.configure('TNotebook.Tab', background=colors['bg_secondary'], foreground=colors['text_secondary'], padding=[16, 10], borderwidth=1, focuscolor='none')
		self.style.map('TNotebook.Tab', background=[('selected', colors['bg_primary']), ('active', colors['surface_hover'])], foreground=[('selected', colors['text_primary']), ('active', colors['text_primary'])], expand=[('selected', [1, 1, 1, 0])])
		self.style.configure('TLabelFrame', background=colors['bg_primary'], foreground=colors['text_primary'], borderwidth=1, relief='solid', bordercolor=colors['border'])
		self.style.configure('TLabelFrame.Label', background=colors['bg_primary'], foreground=colors['text_primary'], font=('Segoe UI', 9, 'bold'))
		self.style.configure('Treeview', background=colors['surface'], foreground=colors['text_primary'], fieldbackground=colors['surface'], borderwidth=1, relief='flat')
		self.style.configure('Treeview.Heading', background=colors['bg_secondary'], foreground=colors['text_primary'], borderwidth=1, relief='flat', font=('Segoe UI', 9, 'bold'))
		self.style.map('Treeview.Heading', background=[('active', colors['surface_hover'])], relief=[('active', 'flat')])
		self.style.map('Treeview', background=[('selected', colors['accent'])], foreground=[('selected', 'white')])
		self.style.configure('TScale', background=colors['bg_primary'], troughcolor=colors['bg_secondary'], borderwidth=0, sliderthickness=16, gripcount=0)
		self.style.map('TScale', troughcolor=[('active', colors['surface_hover'])])
		self.style.configure('TCheckbutton', background=colors['bg_primary'], foreground=colors['text_primary'], focuscolor='none', borderwidth=0, font=('Segoe UI', 9))
		self.style.map('TCheckbutton', background=[('active', colors['bg_primary'])])
		self.style.configure('Vertical.TScrollbar', background=colors['bg_secondary'], troughcolor=colors['surface'], borderwidth=0, arrowcolor=colors['text_secondary'], width=12)
		self.style.map('Vertical.TScrollbar', background=[('active', colors['surface_hover'])])
		if hasattr(self, 'stats_text'):
			self.stats_text.configure(bg=colors['surface'], fg=colors['text_primary'], insertbackground=colors['text_primary'], selectbackground=colors['accent'], selectforeground='white', borderwidth=1, relief='flat', font=('Consolas', 9))
		if hasattr(self, 'weather_text'):
			self.weather_text.configure(bg=colors['surface'], fg=colors['text_primary'], insertbackground=colors['text_primary'], selectbackground=colors['accent'], selectforeground='white', borderwidth=1, relief='flat', font=('Segoe UI', 9))
		if hasattr(self, 'progress_canvas'):
			self.progress_canvas.configure(bg=colors['surface'], highlightbackground=colors['border'], highlightthickness=1)
	def __init__(self):
		self.root = tk.Tk()
		self.root.title("NovaFit — Enhanced Health Tracker 🏃‍♂️")
		self.root.geometry("850x650")
		self.root.minsize(750, 550)
		try:
			self.root.iconify()
			self.root.deiconify()
		except:
			pass
		self.style = ttk.Style()
		self.dark_mode = tk.BooleanVar(value=CONFIG.get("theme", "light") == "dark")
		if self.dark_mode.get():
			self.apply_dark_theme()
		else:
			self.apply_light_theme()
		self.setup_widgets()
		self.root.after(100, self.final_theme_application)
		self.refresh_data()

	def final_theme_application(self):
		if self.dark_mode.get():
			self.apply_dark_theme()
		else:
			self.apply_light_theme()

	def setup_widgets(self):
		self.notebook = ttk.Notebook(self.root, padding="8")
		self.notebook.pack(fill="both", expand=True)
		self.setup_add_tab()
		self.setup_view_tab()
		self.setup_dashboard_tab()
		self.setup_tools_tab()

	# Métodos copiados desde novafit.py (adaptados a módulos actuales)
	def setup_add_tab(self):
		add_frame = ttk.Frame(self.notebook, padding="10")
		self.notebook.add(add_frame, text="➕ Add Entry")
		ttk.Label(add_frame, text="Add New Health Entry", font=("Arial", 14, "bold")).pack(pady=(0, 15))
		input_frame = ttk.LabelFrame(add_frame, text="Health Metrics", padding="10")
		input_frame.pack(fill="x", pady=(0, 10))
		date_frame = ttk.Frame(input_frame)
		date_frame.pack(fill="x", pady=5)
		ttk.Label(date_frame, text="📅 Date:").pack(side="left")
		self.date_var = tk.StringVar(value=date.today().isoformat())
		ttk.Entry(date_frame, textvariable=self.date_var, width=12).pack(side="left", padx=(10, 5))
		ttk.Button(date_frame, text="Today", command=self.set_today).pack(side="left")
		steps_frame = ttk.Frame(input_frame)
		steps_frame.pack(fill="x", pady=5)
		ttk.Label(steps_frame, text="🚶 Steps:", width=12).pack(side="left")
		self.steps_var = tk.StringVar()
		ttk.Entry(steps_frame, textvariable=self.steps_var, width=15).pack(side="left", padx=10)
		self.steps_status = ttk.Label(steps_frame, text="", foreground="green")
		self.steps_status.pack(side="left", padx=5)
		self.steps_scale = ttk.Scale(steps_frame, from_=0, to=20000, orient="horizontal", command=self.update_steps_from_scale)
		self.steps_scale.pack(fill="x", expand=True, padx=(10, 0))
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
		cal_frame = ttk.Frame(input_frame)
		cal_frame.pack(fill="x", pady=5)
		ttk.Label(cal_frame, text="🍽️ Calories:", width=12).pack(side="left")
		self.calories_var = tk.StringVar()
		ttk.Entry(cal_frame, textvariable=self.calories_var, width=15).pack(side="left", padx=10)
		ttk.Label(cal_frame, text="(optional)").pack(side="left")
		mood_frame = ttk.Frame(input_frame)
		mood_frame.pack(fill="x", pady=5)
		ttk.Label(mood_frame, text="😊 Mood:", width=12).pack(side="left")
		self.mood_var = tk.StringVar()
		mood_combo = ttk.Combobox(mood_frame, textvariable=self.mood_var, width=12, values=["😊", "😐", "😴", "😅", "😎", "🤒", "💪"])
		mood_combo.pack(side="left", padx=10)
		btn_frame = ttk.Frame(add_frame)
		btn_frame.pack(fill="x", pady=10)
		ttk.Button(btn_frame, text="💾 Save Entry", command=self.add_entry).pack(side="left", padx=5)
		ttk.Button(btn_frame, text="🧹 Clear", command=self.clear_inputs).pack(side="left", padx=5)
		ttk.Button(btn_frame, text="🎲 Random", command=self.fill_random).pack(side="left", padx=5)

	def setup_view_tab(self):
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
		dash_frame = ttk.Frame(self.notebook, padding="10")
		self.notebook.add(dash_frame, text="📊 Dashboard")
		ttk.Label(dash_frame, text="Health Dashboard", font=("Arial", 14, "bold")).pack(pady=(0, 15))
		progress_frame = ttk.LabelFrame(dash_frame, text="📈 Weekly Progress", padding="10")
		progress_frame.pack(fill="x", pady=(0, 10))
		self.progress_canvas = tk.Canvas(progress_frame, height=100, bg="white")
		self.progress_canvas.pack(fill="x", padx=5, pady=5)
		stats_frame = ttk.LabelFrame(dash_frame, text="� Statistics", padding="10")
		stats_frame.pack(fill="x", pady=(0, 10))
		self.stats_text = tk.Text(stats_frame, height=10, wrap="word", state="disabled")
		stats_scroll = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
		self.stats_text.configure(yscrollcommand=stats_scroll.set)
		self.stats_text.pack(side="left", fill="both", expand=True)
		stats_scroll.pack(side="right", fill="y")
		action_frame = ttk.LabelFrame(dash_frame, text="⚡ Quick Actions", padding="10")
		action_frame.pack(fill="x")
		ttk.Button(action_frame, text="📈 Refresh Stats", command=self.update_dashboard).pack(side="left", padx=5)
		ttk.Button(action_frame, text="📤 Export JSON", command=self.export_data).pack(side="left", padx=5)
		ttk.Button(action_frame, text="📊 Export CSV", command=self.export_csv).pack(side="left", padx=5)
		ttk.Button(action_frame, text="🌤️ Check Weather", command=self.check_weather).pack(side="left", padx=5)

	def setup_tools_tab(self):
		tools_frame = ttk.Frame(self.notebook, padding="10")
		self.notebook.add(tools_frame, text="🛠️ Tools")
		ttk.Label(tools_frame, text="Tools & Utilities", font=("Arial", 14, "bold")).pack(pady=(0, 15))
		io_frame = ttk.LabelFrame(tools_frame, text="📁 Import/Export", padding="10")
		io_frame.pack(fill="x", pady=(0, 10))
		json_frame = ttk.Frame(io_frame)
		json_frame.pack(fill="x", pady=(0, 5))
		ttk.Label(json_frame, text="JSON:", font=("Arial", 9, "bold")).pack(side="left", padx=(0, 10))
		ttk.Button(json_frame, text="📤 Export JSON", command=self.export_data).pack(side="left", padx=5)
		ttk.Button(json_frame, text="📥 Import JSON", command=self.import_data).pack(side="left", padx=5)
		csv_frame = ttk.Frame(io_frame)
		csv_frame.pack(fill="x", pady=(5, 0))
		ttk.Label(csv_frame, text="CSV:", font=("Arial", 9, "bold")).pack(side="left", padx=(0, 10))
		ttk.Button(csv_frame, text="📊 Export CSV", command=self.export_csv).pack(side="left", padx=5)
		ttk.Button(csv_frame, text="📋 Import CSV", command=self.import_csv).pack(side="left", padx=5)
		theme_frame = ttk.LabelFrame(tools_frame, text="🎨 Appearance Settings", padding="10")
		theme_frame.pack(fill="x", pady=(0, 10))
		theme_check = ttk.Checkbutton(theme_frame, text="🌙 Enable Dark Theme", variable=self.dark_mode, command=self.toggle_theme)
		theme_check.pack(side="left", padx=10)
		current_theme = "Dark" if self.dark_mode.get() else "Light"
		self.theme_status = ttk.Label(theme_frame, text=f"Current: {current_theme} Mode")
		self.theme_status.pack(side="right", padx=10)
		data_frame = ttk.LabelFrame(tools_frame, text="🗂️ Data Management", padding="10")
		data_frame.pack(fill="x", pady=(0, 10))
		init_frame = ttk.Frame(data_frame)
		init_frame.pack(fill="x", pady=(0, 5))
		ttk.Label(init_frame, text="Sample data:").pack(side="left")
		ttk.Button(init_frame, text="🌟 Initialize Sample Data", command=self.initialize_sample_data).pack(side="left", padx=5)
		ttk.Button(init_frame, text="🗑️ Clear All Data", command=self.clear_all_data).pack(side="left", padx=5)
		demo_frame = ttk.Frame(data_frame)
		demo_frame.pack(fill="x", pady=(5, 0))
		ttk.Label(demo_frame, text="Generate demo data:").pack(side="left")
		self.seed_var = tk.StringVar(value="7")
		ttk.Entry(demo_frame, textvariable=self.seed_var, width=5).pack(side="left", padx=5)
		ttk.Label(demo_frame, text="days").pack(side="left")
		ttk.Button(demo_frame, text="🎲 Generate", command=self.generate_demo_data).pack(side="left", padx=10)
		weather_frame = ttk.LabelFrame(tools_frame, text="🌤️ Weather", padding="10")
		weather_frame.pack(fill="x", pady=(0, 10))
		ttk.Label(weather_frame, text="City:").pack(side="left")
		self.city_var = tk.StringVar(value="beersheba")
		city_combo = ttk.Combobox(weather_frame, textvariable=self.city_var, width=15, values=list(CITY_COORDS.keys()))
		city_combo.pack(side="left", padx=5)
		ttk.Button(weather_frame, text="🌤️ Get Weather", command=self.check_weather).pack(side="left", padx=10)
		self.weather_text = tk.Text(weather_frame, height=3, width=40, state="disabled")
		self.weather_text.pack(pady=10)

	def set_today(self):
		self.date_var.set(date.today().isoformat())

	def update_steps_from_scale(self, value):
		self.steps_var.set(str(int(float(value))))

	def update_water_from_scale(self, value):
		self.water_var.set(f"{float(value):.1f}")

	def clear_inputs(self):
		self.steps_var.set("")
		self.water_var.set("")
		self.calories_var.set("")
		self.mood_var.set("")
		self.steps_scale.set(0)
		self.water_scale.set(0)

	def fill_random(self):
		from random import randint, uniform, choice
		self.steps_var.set(str(randint(2000, 15000)))
		self.water_var.set(f"{uniform(1.0, 4.0):.1f}")
		self.calories_var.set(str(randint(1200, 3000)))
		self.mood_var.set(choice(["😊", "😐", "😴", "😅", "💪"]))
		self.steps_scale.set(int(self.steps_var.get()))
		self.water_scale.set(float(self.water_var.get()))

	def add_entry(self):
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
			self.check_achievements(steps, water_l)
			self.clear_inputs()
			self.set_today()
			self.refresh_data()
			messagebox.showinfo("Success", "Entry saved successfully! ✅")
		except ValueError as e:
			messagebox.showerror("Error", "Please enter valid numbers for steps and water!")
		except Exception as e:
			messagebox.showerror("Error", f"Error saving entry: {e}")

	def setup_validation(self):
		self.steps_var.trace("w", self.validate_steps)
		self.water_var.trace("w", self.validate_water)

	def validate_input(self, input_type, value_str, status_widget, goal):
		try:
			if not value_str:
				status_widget.config(text="", foreground="gray")
				return
			value = int(value_str) if input_type == "steps" else float(value_str)
			half_goal = goal // 2 if input_type == "steps" else goal / 2
			if value >= goal:
				status_widget.config(text="🎯", foreground="green")
			elif value >= half_goal:
				status_widget.config(text="👍", foreground="orange")
			else:
				status_widget.config(text="", foreground="gray")
		except ValueError:
			status_widget.config(text="❌", foreground="red")

	def validate_steps(self, *args):
		self.validate_input("steps", self.steps_var.get(), self.steps_status, CONFIG["step_goal"])

	def validate_water(self, *args):
		self.validate_input("water", self.water_var.get(), self.water_status, CONFIG["water_goal"])

	def check_achievements(self, steps, water):
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
		self.refresh_entries()
		self.update_dashboard()
		self.update_progress_chart()

	def update_progress_chart(self):
		self.progress_canvas.delete("all")
		entries = list_entries(7)
		if not entries:
			text_color = '#8b949e' if self.dark_mode.get() else '#656d76'
			self.progress_canvas.create_text(200, 50, text="📊 No data available", fill=text_color, font=("Segoe UI", 11))
			return
		self.progress_canvas.update_idletasks()
		width = self.progress_canvas.winfo_width()
		height = 80
		if width <= 1:
			width = 400
		if self.dark_mode.get():
			colors = {
				'success': '#238636',
				'warning': '#d29922',
				'goal_line': '#f85149',
				'text_primary': '#f0f6fc',
				'text_secondary': '#8b949e',
				'background': '#21262d'
			}
		else:
			colors = {
				'success': '#1a7f37',
				'warning': '#bf8700',
				'goal_line': '#d1242f',
				'text_primary': '#24292f',
				'text_secondary': '#656d76',
				'background': '#f6f8fa'
			}
		padding = 15
		bar_spacing = 8
		available_width = width - (2 * padding)
		bar_width = max(35, (available_width - (bar_spacing * 6)) // 7)
		max_steps = max(entry[1] for entry in entries) if entries else CONFIG["step_goal"]
		max_steps = max(max_steps, CONFIG["step_goal"])
		max_steps = int(max_steps * 1.1)
		for i, entry in enumerate(entries):
			x1 = padding + i * (bar_width + bar_spacing)
			bar_height = min(height - 25, (entry[1] / max_steps) * (height - 25))
			y1 = height - bar_height - 5
			x2 = x1 + bar_width
			y2 = height - 5
			if entry[1] >= CONFIG["step_goal"]:
				primary_color = colors['success']
				gradient_color = self.lighten_color(primary_color, 0.1)
			else:
				primary_color = colors['warning']
				gradient_color = self.lighten_color(primary_color, 0.1)
			self.progress_canvas.create_rectangle(x1, y1, x2, y2, fill=primary_color, outline="", width=0)
			if bar_height > 5:
				highlight_height = min(4, bar_height // 4)
				self.progress_canvas.create_rectangle(x1, y1, x2, y1 + highlight_height, fill=gradient_color, outline="")
			if bar_height > 15:
				self.progress_canvas.create_text(x1 + bar_width//2, y1 - 8, text=f"{entry[1]:,}", fill=colors['text_secondary'], font=("Segoe UI", 7, "bold"))
			date_parts = entry[0].split("-")
			date_label = f"{date_parts[1]}/{date_parts[2]}" if len(date_parts) == 3 else entry[0]
			self.progress_canvas.create_text(x1 + bar_width//2, height + 12, text=date_label, fill=colors['text_primary'], font=("Segoe UI", 8))
		goal_y = height - 5 - ((CONFIG["step_goal"] / max_steps) * (height - 25))
		self.progress_canvas.create_line(padding - 5, goal_y, width - padding + 5, goal_y, fill=colors['background'], width=4)
		self.progress_canvas.create_line(padding - 5, goal_y, width - padding + 5, goal_y, fill=colors['goal_line'], dash=(5, 3), width=2)
		goal_text = f"🎯 Goal: {CONFIG['step_goal']:,}"
		text_x = width - 80
		text_y = goal_y - 12
		self.progress_canvas.create_rectangle(text_x - 25, text_y - 8, text_x + 55, text_y + 8, fill=colors['background'], outline="", width=0)
		self.progress_canvas.create_text(text_x + 15, text_y, text=goal_text, fill=colors['goal_line'], font=("Segoe UI", 8, "bold"))

	def lighten_color(self, color, factor):
		try:
			color = color.lstrip('#')
			rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
			rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
			return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
		except:
			return color

	def refresh_entries(self):
		for item in self.tree.get_children():
			self.tree.delete(item)
		entries = list_entries(50)
		for entry in entries:
			mood_str = entry[4] if entry[4] else ""
			cal_str = str(entry[3]) if entry[3] else ""
			self.tree.insert("", "end", values=(entry[0], f"{entry[1]:,}", f"{entry[2]}", cal_str, mood_str))

	def update_dashboard(self):
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
		try:
			filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")], initialfile="novafit_export.json")
			if filename:
				count = do_export_json(Path(filename))
				messagebox.showinfo("Export Complete", f"Exported {count} records to {filename} 💾")
			else:
				try:
					default_path = DATA_DIR / "novafit_export.json"
					count = do_export_json(default_path)
					messagebox.showinfo("Export Complete", f"File dialog cancelled. Exported {count} records to default location:\n{default_path}")
				except Exception as default_error:
					messagebox.showerror("Export Error", f"Export failed: {default_error}")
		except Exception as e:
			messagebox.showerror("Export Error", f"Error exporting data: {e}")
			try:
				fallback_path = DATA_DIR / "emergency_export.json"
				count = do_export_json(fallback_path)
				messagebox.showinfo("Fallback Export", f"Main export failed, but data saved to:\n{fallback_path}\n({count} records)")
			except Exception as fallback_error:
				messagebox.showerror("Critical Error", f"All export methods failed: {fallback_error}")

	def import_data(self):
		try:
			filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
			if filename:
				count = do_import_json(Path(filename))
				messagebox.showinfo("Import Complete", f"Imported {count} new records 📥")
				self.refresh_data()
		except Exception as e:
			messagebox.showerror("Import Error", f"Error importing data: {e}")

	def export_csv(self):
		try:
			filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialfile="novafit_export.csv")
			if filename:
				count = do_export_csv(Path(filename))
				messagebox.showinfo("Export Complete", f"Exported {count} records to {filename} 📊\n\n" + f"💡 Tip: You can open this file in Excel, Google Sheets, " + f"or any spreadsheet application!")
			else:
				try:
					default_path = DATA_DIR / "novafit_export.csv"
					count = do_export_csv(default_path)
					messagebox.showinfo("Export Complete", f"File dialog cancelled. Exported {count} records to default location:\n{default_path}\n\n" + f"💡 Tip: You can open this file in Excel, Google Sheets, or any spreadsheet application!")
				except Exception as default_error:
					messagebox.showerror("Export Error", f"CSV export failed: {default_error}")
		except Exception as e:
			messagebox.showerror("Export Error", f"Error exporting CSV data: {e}")
			try:
				fallback_path = DATA_DIR / "emergency_export.csv"
				count = do_export_csv(fallback_path)
				messagebox.showinfo("Fallback Export", f"Main export failed, but CSV data saved to:\n{fallback_path}\n({count} records)")
			except Exception as fallback_error:
				messagebox.showerror("Critical Error", f"All CSV export methods failed: {fallback_error}")

	def import_csv(self):
		try:
			filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
			if filename:
				count = do_import_csv(Path(filename))
				messagebox.showinfo("Import Complete", f"Imported {count} new records 📋")
				self.refresh_data()
		except Exception as e:
			messagebox.showerror("Import Error", f"Error importing CSV data: {e}")

	def generate_demo_data(self):
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

	def initialize_sample_data(self):
		try:
			result = messagebox.askyesno("Initialize Sample Data", "This will create a week of realistic sample health data.\n\nThis is perfect for new users to understand how the application works.\n\nNote: This will overwrite any existing data for the sample dates.\n\nContinue?")
			if result:
				count = initialize_sample_data()
				messagebox.showinfo("Sample Data Initialized", f"Successfully initialized {count} sample entries! 🌟\n\nYou now have a week of sample data to explore the application.")
				self.refresh_data()
		except Exception as e:
			messagebox.showerror("Error", f"Error initializing sample data: {e}")

	def clear_all_data(self):
		try:
			result1 = messagebox.askyesno("Clear All Data", "⚠️ WARNING: This will permanently delete ALL your health data!\n\nThis action cannot be undone.\n\nMake sure to export your data first if you want to keep it.\n\nAre you sure you want to continue?")
			if not result1:
				return
			result2 = messagebox.askyesno("Final Confirmation", "🚨 FINAL CONFIRMATION 🚨\n\nYou are about to delete ALL health data permanently.\n\nThis action CANNOT be undone!\n\nClick 'Yes' only if you are absolutely certain.")
			if result2:
				count = clear_all_data()
				messagebox.showinfo("Data Cleared", f"Successfully deleted {count} entries.\n\nYour database is now empty and ready for fresh data.")
				self.refresh_data()
		except Exception as e:
			messagebox.showerror("Error", f"Error clearing data: {e}")

	def check_weather(self):
		try:
			city = self.city_var.get()
			self.weather_text.config(state="normal")
			self.weather_text.delete("1.0", tk.END)
			self.weather_text.insert(tk.END, "🔄 Loading weather data...")
			self.weather_text.config(state="disabled")
			self.root.update()
			weather = get_weather(city)
			self.weather_text.config(state="normal")
			self.weather_text.delete("1.0", tk.END)
			if weather["status"] == "success":
				self.weather_text.insert(tk.END, f"🌤️ {city.title()}\n🌡️ {weather['temp']}°C\n💧 {weather['humidity']}% humidity\n📡 Source: {weather['source']}")
			else:
				error_messages = {
					"timeout": "⏱️ Request timeout - API is slow to respond",
					"connection_error": "🌐 Internet connection issue",
					"api_error": "⚠️ Weather service error",
					"json_error": "📄 Invalid response from weather service",
					"network_error": "🔌 Network error occurred",
					"general_error": "❌ Unknown error occurred"
				}
				error_msg = error_messages.get(weather["status"], "❌ Unknown error")
				self.weather_text.insert(tk.END, f"⚠️ Weather data unavailable for {city.title()}\n{error_msg}\n📡 Details: {weather['source']}\n\nTroubleshooting:\n• Check internet connection\n• Verify firewall settings\n• Try again in a moment")
			self.weather_text.config(state="disabled")
		except Exception as e:
			self.weather_text.config(state="normal")
			self.weather_text.delete("1.0", tk.END)
			self.weather_text.insert(tk.END, f"❌ Error fetching weather: {str(e)}")
			self.weather_text.config(state="disabled")

	def toggle_theme(self):
		if self.dark_mode.get():
			self.apply_dark_theme()
			CONFIG["theme"] = "dark"
		else:
			self.apply_light_theme()
			CONFIG["theme"] = "light"
		save_config(CONFIG)
		if hasattr(self, 'theme_status'):
			current_theme = "Dark" if self.dark_mode.get() else "Light"
			self.theme_status.configure(text=f"Current: {current_theme} Mode")

	def run(self):
		self.root.mainloop()

def launch_gui():
	gui = NovaFitGUI()
	gui.run()

def main():
	init_db(Path(CONFIG.get('db_path', './data/novafit.db')))
	launch_gui()

if __name__ == "__main__":
	main()
