@echo off
setlocal
cd /d "%~dp0"
echo.
echo === Installing/Updating Python packages (this might take a minute on first run) ===
where py >nul 2>nul
if %errorlevel% neq 0 (
  set PY=python
) else (
  set PY=py
)
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
echo.
echo === Starting the Streamlit app ===
%PY% -m streamlit run app.py
endlocal
