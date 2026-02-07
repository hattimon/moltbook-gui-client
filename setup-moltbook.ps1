# setup-moltbook.ps1
# Auto-setup i uruchomienie Moltbook GUI Client na Windows

function Write-Info($msg)  { Write-Host "[INFO]  $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Err($msg)   { Write-Host "[ERROR] $msg" -ForegroundColor Red }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Info "Katalog projektu: $ScriptDir"

# 1. Znajdź Pythona
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Err "Nie znaleziono Pythona w PATH."
    Read-Host "Wciśnij Enter, aby zamknąć okno..."
    exit 1
}

$pythonPath = $python.Source
Write-Ok "Python znaleziony: $pythonPath"

# 2. Utwórz / użyj venv
$venvDir = Join-Path $ScriptDir "venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Ok "Istnieje już środowisko wirtualne: $venvDir"
} else {
    Write-Info "Tworzę środowisko wirtualne: $venvDir"
    & $pythonPath -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Nie udało się utworzyć venv."
        Read-Host "Wciśnij Enter, aby zamknąć okno..."
        exit 1
    }
}

# 3. Zainstaluj zależności z requirements.txt
$requirements = Join-Path $ScriptDir "requirements.txt"
if (-not (Test-Path $requirements)) {
    Write-Err "Brak pliku requirements.txt w katalogu projektu."
    Read-Host "Wciśnij Enter, aby zamknąć okno..."
    exit 1
}

Write-Info "Instaluję zależności z requirements.txt (to może chwilę potrwać)..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r $requirements
if ($LASTEXITCODE -ne 0) {
    Write-Err "Problem z instalacją pakietów."
    Read-Host "Wciśnij Enter, aby zamknąć okno..."
    exit 1
}
Write-Ok "Zależności zainstalowane."

# 4. Uruchom aplikację (main.py) w venv
$mainScript = Join-Path $ScriptDir "main.py"
if (-not (Test-Path $mainScript)) {
    Write-Err "Nie znaleziono main.py w katalogu projektu."
    Read-Host "Wciśnij Enter, aby zamknąć okno..."
    exit 1
}

Write-Info "Uruchamiam Moltbook GUI Client w venv..."
& $venvPython $mainScript

Write-Host ""
Read-Host "Wciśnij Enter, aby zamknąć okno..."
