#!/bin/bash
# Startup script for AI-IDS Backend

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run the backend
echo "Starting AI-IDS Backend API..."
cd "$SCRIPT_DIR"
python backend/app.py
