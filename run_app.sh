#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m streamlit run "FullCircle-Home.py"
