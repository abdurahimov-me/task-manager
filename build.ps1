$ErrorActionPreference = "Stop"
python -m PyInstaller --noconfirm --clean --windowed --onefile --name "HR-Control" main.py
Write-Host "Tayyor: dist\HR-Control.exe"
