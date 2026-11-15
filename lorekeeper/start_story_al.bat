@echo off
title Story AL — Narrative World Engine
cd /d "%~dp0"

echo ======================================================================
echo           Story AL — Narrative World Engine & Voice Studio
echo ======================================================================
echo.
echo [ACCESS LINKS]
echo   1. Local Studio Link (This PC):
echo      http://localhost:5055
echo.
echo   2. Network Link (Phones, iPads, Laptops on same Wi-Fi):
echo      http://localhost:5055
echo.
echo ======================================================================
echo Starting Story AL server... Browser will open automatically.
echo (Press CTRL+C anytime in this window to stop the server)
echo ======================================================================
echo.

start "" "http://localhost:5055"
python app.py
pause
