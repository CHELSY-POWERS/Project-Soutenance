"""
AI-IDS First-Time Setup Script
================================
Run this ONCE after cloning the repository.

Usage:
    python backend/setup.py

What it does:
    1. Checks Python version
    2. Creates virtual environment
    3. Installs all dependencies
    4. Checks for NSL-KDD dataset
    5. Trains AI models (takes 2-3 minutes)
    6. Creates necessary folders
    7. Verifies everything works
"""

import os
import sys
import subprocess
import platform

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(BASE_DIR)
VENV_DIR   = os.path.join(ROOT_DIR, 'venv')
DATA_DIR   = os.path.join(BASE_DIR, 'data', 'processed')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Detect python and pip
IS_WINDOWS = platform.system() == 'Windows'
VENV_PYTHON = os.path.join(VENV_DIR, 'Scripts' if IS_WINDOWS else 'bin', 'python')
VENV_PIP    = os.path.join(VENV_DIR, 'Scripts' if IS_WINDOWS else 'bin', 'pip')

def header(msg):
    print(f"\n{'='*55}")
    print(f"  {msg}")
    print('='*55)

def step(msg):
    print(f"\n⏳ {msg}...")

def ok(msg):
    print(f"✅ {msg}")

def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)

def run(cmd, cwd=None, use_venv=False):
    python = VENV_PYTHON if use_venv else sys.executable
    if isinstance(cmd, str):
        cmd = cmd.replace('python', python, 1) if cmd.startswith('python') else cmd
    result = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd or BASE_DIR)
    return result.returncode == 0

print("""
╔═══════════════════════════════════════════════════════╗
║         AI-IDS — First Time Setup                     ║
║         Autonomous Intrusion Detection System         ║
╚═══════════════════════════════════════════════════════╝
""")

# ── Step 1: Check Python version ─────────────────────────
header("Step 1/6 — Checking Python version")
major, minor = sys.version_info[:2]
print(f"  Python {major}.{minor} detected")
if major < 3 or minor < 8:
    fail("Python 3.8+ required. Please upgrade Python.")
ok(f"Python {major}.{minor} is compatible")

# ── Step 2: Create virtual environment ───────────────────
header("Step 2/6 — Setting up virtual environment")
if os.path.exists(VENV_PYTHON):
    ok("Virtual environment already exists — skipping")
else:
    step("Creating virtual environment")
    if not run(f"{sys.executable} -m venv {VENV_DIR}"):
        fail("Failed to create virtual environment")
    ok("Virtual environment created")

# ── Step 3: Install dependencies ─────────────────────────
header("Step 3/6 — Installing Python dependencies")
step("Installing from requirements.txt")
req_path = os.path.join(BASE_DIR, 'requirements.txt')
result = subprocess.run(
    [VENV_PIP, 'install', '-r', req_path],
    cwd=BASE_DIR
)
if result.returncode != 0:
    fail("Failed to install dependencies")
ok("All dependencies installed")

# ── Step 4: Create necessary folders ─────────────────────
header("Step 4/6 — Creating project folders")
folders = [
    os.path.join(BASE_DIR, 'models'),
    os.path.join(BASE_DIR, 'results'),
    os.path.join(BASE_DIR, 'logs'),
    os.path.join(BASE_DIR, 'data', 'processed'),
]
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"  📁 {folder}")
ok("All folders ready")

# ── Step 5: Check dataset ─────────────────────────────────
header("Step 5/6 — Checking NSL-KDD Dataset")
train_path = os.path.join(DATA_DIR, 'KDDTrain+.txt')
test_path  = os.path.join(DATA_DIR, 'KDDTest+.txt')

if os.path.exists(train_path) and os.path.exists(test_path):
    train_size = os.path.getsize(train_path) / (1024*1024)
    test_size  = os.path.getsize(test_path)  / (1024*1024)
    ok(f"KDDTrain+.txt found ({train_size:.1f} MB)")
    ok(f"KDDTest+.txt found ({test_size:.1f} MB)")
else:
    print("""
  ⚠️  DATASET NOT FOUND — Manual download required:

  1. Go to: https://www.kaggle.com/datasets/hassan06/nslkdd
  2. Click "Download" (you need a free Kaggle account)
  3. Extract the zip file
  4. Copy these two files into  backend/data/processed/ :
       • KDDTrain+.txt
       • KDDTest+.txt
  5. Run this setup script again:
       python backend/setup.py

  The dataset is ~22MB total and is required to train the AI models.
""")
    sys.exit(0)

# ── Step 6: Train models ──────────────────────────────────
header("Step 6/6 — Training AI Models")

model_path = os.path.join(MODELS_DIR, 'ai_detection_model.pkl')
rf_path    = os.path.join(MODELS_DIR, 'random_forest_model.pkl')

if os.path.exists(model_path) and os.path.exists(rf_path):
    print("  Models already trained — skipping")
    print("  (Delete backend/models/*.pkl to force retrain)")
    ok("Models ready")
else:
    step("Training Isolation Forest (1-2 minutes)")
    r1 = subprocess.run([VENV_PYTHON, os.path.join(BASE_DIR, 'train_model.py')], cwd=BASE_DIR)
    if r1.returncode != 0:
        fail("Isolation Forest training failed")
    ok("Isolation Forest trained!")

    step("Training Random Forest (2-3 minutes)")
    r2 = subprocess.run([VENV_PYTHON, os.path.join(BASE_DIR, 'train_random_forest.py')], cwd=BASE_DIR)
    if r2.returncode != 0:
        fail("Random Forest training failed")
    ok("Random Forest trained!")

# ── Done! ─────────────────────────────────────────────────
print("""
╔═══════════════════════════════════════════════════════╗
║  ✅  Setup Complete! Here's how to run the project:   ║
║                                                       ║
║  TERMINAL 1 — Start backend:                          ║
║    cd backend                                         ║
║    source ../venv/bin/activate    (Mac/Linux)         ║
║    venv\\Scripts\\activate          (Windows)           ║
║    python app.py                                      ║
║                                                       ║
║  TERMINAL 2 — Start frontend:                         ║
║    cd dashboard                                       ║
║    npm install                                        ║
║    npm start                                          ║
║                                                       ║
║  BROWSER — Open dashboard:                            ║
║    http://localhost:3000                              ║
║                                                       ║
║  NOTE: Network monitoring requires sudo:              ║
║    sudo venv/bin/python backend/log_analysis/         ║
║         network_monitor.py --interface wlp4s0         ║
╚═══════════════════════════════════════════════════════╝
""")
