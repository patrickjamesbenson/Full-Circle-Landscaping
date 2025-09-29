#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "[1/4] Python:"; python3 --version
echo "[2/4] Creating venv (.venv)..."
python3 -m venv .venv
source .venv/bin/activate
echo "[3/4] Installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo "[4/4] Launching Streamlit..."
python -m streamlit run "FullCircle-Home.py"
