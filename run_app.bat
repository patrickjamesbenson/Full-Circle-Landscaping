@echo off
setlocal
cd /d "%~dp0"
title Full Circle (Excel-backed)
echo [1/4] Checking Python...
where py >nul 2>nul && set "PYCMD=py" || set "PYCMD=python"
%PYCMD% --version || (echo Python not found. Install from https://python.org & try again.& pause & exit /b 1)

echo [2/4] Creating virtual env (.venv)...
%PYCMD% -m venv .venv
if exist ".venv\Scripts\activate.bat" (call ".venv\Scripts\activate.bat") else (echo Failed to create venv.& pause & exit /b 1)

echo [3/4] Installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo [4/4] Launching Streamlit app...
python -m streamlit run "FullCircle-Home.py"
echo If the browser didn't open, visit: http://localhost:8501
pause
endlocal
