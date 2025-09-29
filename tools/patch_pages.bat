# ======================================
# FILE: tools/patch_pages.bat  (NEW)
# ======================================
# Double-click this file in Explorer.
# Tries your venv python first, then falls back to system python.
@echo off
setlocal
cd /d "%~dp0\.."
set PY_VENV=.venv\Scripts\python.exe
if exist "%PY_VENV%" (
    "%PY_VENV%" tools\patch_pages.py
) else (
    python tools\patch_pages.py
)
echo.
echo [Patch] Complete. If Streamlit is running, press 'r' in the console or refresh the browser.
pause
endlocal