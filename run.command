#!/bin/bash
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv || { echo "Python 3 is required"; read -r; exit 1; }
fi
source .venv/bin/activate
python -m pip install -r requirements.txt || { echo "Dependency installation failed"; read -r; exit 1; }
python -m streamlit run app.py --server.address localhost
