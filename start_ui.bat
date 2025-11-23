@echo off
echo Starting Telegram Auto Save Chat UI...
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe ui.py
) else (
    python ui.py
)

pause
