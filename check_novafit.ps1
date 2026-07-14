#requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$InstallDependencies,
    [switch]$OpenRepository
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Write-Step([string]$Text) {
    Write-Host ""
    Write-Host "🔍 $Text" -ForegroundColor Cyan
}

function Resolve-Python {
    if (Test-Path ".venv\Scripts\python.exe") {
        return (Resolve-Path ".venv\Scripts\python.exe").Path
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return "py -3" }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return $python.Source }
    throw "Python 3 was not found. Run setup.bat after installing Python 3.10+."
}

Write-Host "============================================================"
Write-Host "  🏃 NovaFit Diagnostics"
Write-Host "============================================================"

$required = @(
    "README.md",
    "requirements.txt",
    "novafit\__init__.py",
    "novafit\cli.py",
    "novafit\gui.py",
    "novafit\config.py",
    "novafit\database.py",
    "novafit\export.py",
    "novafit\utils.py",
    "novafit\weather.py"
)

Write-Step "Checking required files"
$missing = @($required | Where-Object { -not (Test-Path $_) })
if ($missing.Count -gt 0) {
    foreach ($path in $missing) { Write-Host "❌ Missing: $path" -ForegroundColor Red }
    throw "NovaFit is incomplete."
}
foreach ($path in $required) { Write-Host "✅ $path" -ForegroundColor Green }

if ($InstallDependencies -and -not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Step "Creating environment and installing dependencies"
    & "$PSScriptRoot\setup.bat"
    if ($LASTEXITCODE -ne 0) { throw "setup.bat failed." }
}

$python = Resolve-Python
function Invoke-Python([string[]]$Arguments) {
    if ($python -eq "py -3") {
        & py -3 @Arguments
    } else {
        & $python @Arguments
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($Arguments -join ' ')"
    }
}

Write-Step "Compiling Python modules"
Invoke-Python @("-m", "compileall", "-q", "novafit")
Write-Host "✅ Python compilation passed." -ForegroundColor Green

Write-Step "Running smoke tests"
Invoke-Python @("-m", "unittest", "discover", "-s", "tests", "-v")
Write-Host "✅ Smoke tests passed." -ForegroundColor Green

Write-Step "Checking GitHub Pages expectations"
Write-Host "ℹ️ NovaFit is a local Python CLI/Tkinter desktop application."
Write-Host "ℹ️ GitHub Pages cannot run Python or Tkinter; the repository page is source/documentation."
Write-Host "ℹ️ A web demo would require a separate browser implementation."

Write-Step "Repository summary"
$files = Get-ChildItem -Recurse -File |
    Where-Object { $_.FullName -notmatch '\\(\.git|\.venv|__pycache__)\\' }
$total = ($files | Measure-Object -Property Length -Sum).Sum
Write-Host ("📦 Files: {0}" -f $files.Count)
Write-Host ("📏 Working-tree size: {0:N2} KB" -f ($total / 1KB))
Write-Host "✅ Diagnostics complete." -ForegroundColor Green

if ($OpenRepository) {
    Start-Process "https://github.com/LiriothTeltanion/NovaFit"
}
