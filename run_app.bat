@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Full Circle Control Centre
echo.
echo === Checking Python ===
set "PY_EXE="
for %%P in (py.exe python.exe python3.exe) do (
  where %%P >nul 2>nul && set "PY_EXE=%%P" && goto :found
)
:found
if "%PY_EXE%"=="" (
  echo Could not find Python on PATH. Install from https://www.python.org/ and try again.
  pause
  exit /b 1
)
echo Using: %PY_EXE%
echo.
echo === Installing dependencies (first run takes a minute) ===
"%PY_EXE%" -m pip install --upgrade pip
"%PY_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Pip install failed.
  pause
  exit /b 1
)
echo.
echo === Launching app ===
"%PY_EXE%" -m streamlit run app.py
echo.
echo If the browser didn't open automatically, visit: http://localhost:8501
pause
endlocal
