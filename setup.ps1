# ============================================
# Skrypt inicjalizacyjny projektu
# Theater Booking System
# ============================================
# Uruchom ten skrypt aby przygotować środowisko lokalne

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Theater Booking System - Setup" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Sprawdź czy Python jest zainstalowany
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python nie jest zainstalowany!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] $pythonVersion" -ForegroundColor Green

# Przejdź do katalogu backend
Set-Location -Path "backend"

# Utwórz środowisko wirtualne jeśli nie istnieje
if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Tworzenie środowiska wirtualnego..." -ForegroundColor Yellow
    python -m venv venv
}

# Aktywuj środowisko wirtualne
Write-Host "[INFO] Aktywacja środowiska wirtualnego..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Zainstaluj zależności
Write-Host "[INFO] Instalacja zależności..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Sprawdź czy .env istnieje
if (-not (Test-Path ".env")) {
    Write-Host "[INFO] Tworzenie pliku .env z przykładu..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "[UWAGA] Edytuj plik backend/.env i uzupełnij klucze Stripe!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup zakończony pomyślnie!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Aby uruchomić backend:" -ForegroundColor Cyan
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python app.py" -ForegroundColor White
Write-Host ""
Write-Host "Aby uruchomić frontend (nowy terminal):" -ForegroundColor Cyan
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  python -m http.server 3000" -ForegroundColor White
Write-Host ""
Write-Host "Aby uruchomić testy:" -ForegroundColor Cyan
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  pytest tests/ -v" -ForegroundColor White
Write-Host ""
