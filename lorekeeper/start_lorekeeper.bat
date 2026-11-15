@echo off
title LoreKeeper AI — The Memory of Fictional Worlds
cd /d "%~dp0"

echo ======================================================================
echo           LoreKeeper AI — The Memory of Fictional Worlds
echo ======================================================================
echo.
echo [ACCESS LINKS]
echo   1. Local Offline Link (This PC):
echo      http://localhost:5055
echo.
echo   2. Local Wi-Fi / Hotspot Link (Phones, iPads, Laptops on same Wi-Fi):
echo      http://10.214.247.39:5055
echo.
echo ======================================================================
echo Starting server... Browser will open automatically.
echo (Press CTRL+C anytime in this window to stop the server)
echo ======================================================================
echo.

start "" "http://localhost:5055"
python app.py
pause
