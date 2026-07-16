# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller onedir definition for the official NovaFit Windows bundle."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


ROOT = Path(SPECPATH).resolve().parent
GUI_ENTRY_POINT = ROOT / "launch_novafit.py"
CLI_ENTRY_POINT = ROOT / "launch_novafit_cli.py"
ICON = ROOT / "assets" / "novafit.ico"

datas = collect_data_files("tzdata")
hiddenimports = [
    "matplotlib.backends.backend_agg",
    "matplotlib.backends.backend_tkagg",
    "PIL._tkinter_finder",
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.ttk",
]

gui_analysis = Analysis(
    [str(GUI_ENTRY_POINT)],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["IPython", "pytest", "pyright", "ruff"],
    noarchive=False,
    optimize=1,
)
cli_analysis = Analysis(
    [str(CLI_ENTRY_POINT)],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["IPython", "pytest", "pyright", "ruff"],
    noarchive=False,
    optimize=1,
)
gui_archive = PYZ(gui_analysis.pure)
cli_archive = PYZ(cli_analysis.pure)

gui = EXE(
    gui_archive,
    gui_analysis.scripts,
    [],
    exclude_binaries=True,
    name="NovaFit",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON),
)

cli = EXE(
    cli_archive,
    cli_analysis.scripts,
    [],
    exclude_binaries=True,
    name="NovaFit-CLI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON),
)

bundle = COLLECT(
    gui,
    cli,
    gui_analysis.binaries,
    gui_analysis.datas,
    cli_analysis.binaries,
    cli_analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="NovaFit",
)
