$ErrorActionPreference = "Stop"
$pythonExe = "C:\Python314\python.exe"
if (-not (Test-Path -LiteralPath $pythonExe)) {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
}
& $pythonExe -m PyInstaller --noconfirm --clean --windowed --onefile --noupx --name "HR-Control" --icon "assets\hr-control-app-icon.ico" --add-data "assets\hr-control-app-icon.png;assets" main.py
Write-Host "Тайёр: dist\HR-Control.exe"
