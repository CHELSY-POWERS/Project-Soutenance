"""
Main Orchestrator for AI-IDS Project
Autonomous AI-Based Intrusion Detection System

Usage:
    python main.py

Author: Your Name
Date: February 2026
"""

import os
import sys

# Project directories
ROOT_DIR    = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')

# Add backend to Python path and set working directory
#sys.path.insert(0, BACKEND_DIR)
#os.chdir(BACKEND_DIR)


def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def check_dependencies():
    print_header("CHECKING DEPENDENCIES")
    required = ['numpy', 'pandas', 'sklearn', 'flask']
    missing  = []
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  ✓ {pkg}")
        except ImportError:
            print(f"  ✗ {pkg} (MISSING)")
            missing.append(pkg)
    if missing:
        print(f"\n[ERROR] Missing: {', '.join(missing)}")
        print("[INFO] Run: pip install -r requirements.txt")
        return False
    print("\n[SUCCESS] All dependencies installed!")
    return True


def create_directories():
    print_header("CREATING PROJECT DIRECTORIES")
    for d in ['data', 'data/processed', 'models', 'results', 'logs']:
        os.makedirs(os.path.join(BACKEND_DIR, d), exist_ok=True)
        print(f"  ✓ backend/{d}/")
    print("\n[SUCCESS] Directories ready!")


def run_pipeline():
    print_header("RUNNING AI PIPELINE")
    input("Press Enter to start...\n")

    # Step 1
    print_header("STEP 1 — DATASET PREPARATION")
    try:
        from backend.data.prepare_dataset import main as prepare
        prepare()
    except Exception as e:
        print(f"[ERROR] {e}"); return False

    # Step 2
    print_header("STEP 2 — FEATURE EXTRACTION")
    try:
        from backend.feature_engineering.extractor import main as extract
        extract()
    except Exception as e:
        print(f"[ERROR] {e}"); return False

    # Step 3
    print_header("STEP 3 — AI MODEL TRAINING & EVALUATION")
    try:
        from backend.ai_engine.anomaly_detector import main as train
        train()
    except Exception as e:
        print(f"[ERROR] {e}"); return False

    print_header("PIPELINE COMPLETED SUCCESSFULLY")
    print("  ✓ Dataset prepared        → backend/data/")
    print("  ✓ Features extracted      → backend/data/processed/")
    print("  ✓ AI model trained        → backend/models/")
    print("  ✓ Results generated       → backend/results/\n")
    print("Next:")
    print("  Start backend  → python backend/app.py")
    print("  Start frontend → cd dashboard && npm install && npm start")
    print("  Open browser   → http://localhost:3000\n")
    return True


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║       AI-BASED INTRUSION DETECTION SYSTEM  (AI-IDS)          ║
║         Autonomous Solution — University Context             ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    if not check_dependencies(): sys.exit(1)
    create_directories()
    sys.exit(0 if run_pipeline() else 1)


if __name__ == "__main__":
    main()