# Quick Setup Script for InstaLogic

Write-Host "=== InstaLogic Project Setup ===" -ForegroundColor Cyan
Write-Host ""

# Setup Backend
Write-Host "Setting up Backend..." -ForegroundColor Green
Set-Location "$PSScriptRoot\backend"

if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "Backend setup complete!" -ForegroundColor Green
Write-Host ""

# Setup Frontend
Write-Host "Setting up Frontend..." -ForegroundColor Green
Set-Location "$PSScriptRoot\frontend"

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Write-Host "Frontend setup complete!" -ForegroundColor Green
Write-Host ""

Set-Location $PSScriptRoot

Write-Host "=== Setup Complete! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the development servers, run:" -ForegroundColor Yellow
Write-Host "  .\start-dev.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or start them manually:" -ForegroundColor Yellow
Write-Host "  Backend:  cd backend; .\venv\Scripts\Activate.ps1; python main.py" -ForegroundColor White
Write-Host "  Frontend: cd frontend; npm run dev" -ForegroundColor White
