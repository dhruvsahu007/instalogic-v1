# Start Backend and Frontend Development Servers

Write-Host "Starting InstaLogic Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

# Check for Python
if (-not (Test-Command python)) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check for Node.js
if (-not (Test-Command node)) {
    Write-Host "Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version

Write-Host "Checking Node.js version..." -ForegroundColor Yellow
node --version

Write-Host ""
Write-Host "=== Starting Backend Server ===" -ForegroundColor Green

# Start backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; Write-Host 'Setting up Python virtual environment...' -ForegroundColor Cyan; if (-not (Test-Path 'venv')) { python -m venv venv }; .\venv\Scripts\Activate.ps1; Write-Host 'Installing dependencies...' -ForegroundColor Cyan; pip install -r requirements.txt; Write-Host 'Starting FastAPI server...' -ForegroundColor Green; python main.py"

Write-Host "Backend server starting on http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation will be available at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Wait a bit for backend to start
Start-Sleep -Seconds 3

Write-Host "=== Starting Frontend Server ===" -ForegroundColor Green

# Start frontend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; Write-Host 'Installing dependencies...' -ForegroundColor Cyan; npm install; Write-Host 'Starting React development server...' -ForegroundColor Green; npm run dev"

Write-Host "Frontend server starting on http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Both servers are starting in separate windows!" -ForegroundColor Green
Write-Host "Press any key to exit this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
