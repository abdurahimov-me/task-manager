$ErrorActionPreference = "Stop"
$pythonExe = (Get-Command python -ErrorAction Stop).Source
Push-Location $PSScriptRoot
try {
& $pythonExe -m PyInstaller --noconfirm --clean --windowed --onefile --noupx --name "HR-Control" --icon "assets\hr-control-app-icon.ico" --add-data "assets\hr-control-app-icon.png;assets" main.py
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed (exit code $LASTEXITCODE)."
}
Write-Host "Тайёр: dist\HR-Control.exe"
} finally {
    Pop-Location
}
