#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "======================================================================"
echo "   The Hackers Den - NASA Field Shift Weather AI"
echo "======================================================================"
echo ""

if [ -f "venv/bin/python" ]; then
    PY_EXE="venv/bin/python"
elif [ -f "prithvi-env/bin/python" ]; then
    PY_EXE="prithvi-env/bin/python"
else
    echo "[*] Creating virtual environment 'venv'..."
    python3 -m venv venv
    PY_EXE="venv/bin/python"
    echo "[*] Installing dependencies from requirements.txt..."
    "$PY_EXE" -m pip install --upgrade pip
    "$PY_EXE" -m pip install -r requirements.txt
fi

echo ""
echo "[*] Starting NASA Field Shift AI GUI Server on port 5000..."
echo "[*] Open your browser to: http://127.0.0.1:5000"
echo ""
"$PY_EXE" prithvi_weather_gui.py --port 5000
