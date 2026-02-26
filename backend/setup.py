"""
AI-IDS Setup Script
Run this once after cloning: python backend/setup.py
It will download the dataset and train the models automatically.
"""

import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run(cmd, msg):
    print(f"\n{'='*50}")
    print(f"⏳ {msg}...")
    print('='*50)
    result = subprocess.run(cmd, shell=True, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"❌ Failed: {msg}")
        sys.exit(1)
    print(f"✅ Done: {msg}")

print("""
╔══════════════════════════════════════════╗
║     AI-IDS — First Time Setup            ║
║     This will take 2-3 minutes           ║
╚══════════════════════════════════════════╝
""")

# 1. Install dependencies
run("pip install -r requirements.txt", "Installing Python dependencies")

# 2. Create necessary folders
os.makedirs(os.path.join(BASE_DIR, 'models'),           exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'results'),          exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'logs'),             exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'data/processed'),   exist_ok=True)
print("✅ Folders created")

# 3. Check if dataset exists
dataset_path = os.path.join(BASE_DIR, 'data/processed/KDDTrain+.txt')
if not os.path.exists(dataset_path):
    print("""
⚠️  DATASET MISSING — Manual step required:

1. Go to: https://www.kaggle.com/datasets/hassan06/nslkdd
2. Download: KDDTrain+.txt and KDDTest+.txt
3. Place them in: backend/data/processed/
4. Re-run this script

""")
    sys.exit(0)

# 4. Train models
run("python train_model.py",         "Training Isolation Forest model")
run("python train_random_forest.py", "Training Random Forest model")

print("""
╔══════════════════════════════════════════╗
║  ✅ Setup Complete!                       ║
║                                          ║
║  Now run:                                ║
║    python app.py                         ║
║                                          ║
║  Then in another terminal:               ║
║    cd dashboard && npm install           ║
║    npm start                             ║
╚══════════════════════════════════════════╝
""")
