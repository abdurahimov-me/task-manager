$ErrorActionPreference = "Stop"
python -m PyInstaller --noconfirm --clean --windowed --onefile --noupx --name "HR-Control" --icon "assets\hr-control-app-icon.ico" --add-data "assets\hr-control-app-icon.png;assets" main.py
Write-Host "Tayyor: dist\HR-Control.exe"
