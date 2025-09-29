Full Circle Control Centre 2 — Excel-backed Streamlit App

How to run (Windows):
  1) Double-click run_app.bat
  2) It will create .venv, install deps, and open http://localhost:8501

macOS:
  1) Double-click run_app.command (or run: ./run_app.command)

Linux:
  1) bash run_app.sh

Excel location:
  - Default: data/fullcircle.xlsx (auto-created on first run)
  - To point at a different workbook, set environment variable FULLCIRCLE_XLSX_PATH before launching.

Troubleshooting:
  - If you see errors about packages, delete .venv and re-run the launcher.
  - If the browser doesn't open, visit http://localhost:8501 manually.
