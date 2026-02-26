# AI-IDS — Artificial Intelligence Intrusion Detection System

A complete cybersecurity system using Machine Learning to detect network intrusions and anomalies in real time.

## Features
- Isolation Forest + Random Forest AI models
- Real-time log analysis (auth.log, Apache, syslog)
- SQL Injection detection (7 attack categories)
- Live network traffic monitoring (packet sniffing)
- React dashboard with 5 tabs

## Quick Start

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd ai-ids-project
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Download the dataset (required once)
- Go to: https://www.kaggle.com/datasets/hassan06/nslkdd
- Download `KDDTrain+.txt` and `KDDTest+.txt`
- Place them in `backend/data/processed/`

### 4. Run setup (installs dependencies + trains models)
```bash
python backend/setup.py
```

### 5. Start the backend
```bash
cd backend
python app.py
```

### 6. Start the frontend (new terminal)
```bash
cd dashboard
npm install
npm start
```

### 7. Open your browser
```
http://localhost:3000
```

## Important Note About localhost
The frontend is configured for `localhost:5000` by default.
If you want others on the same WiFi to access it, find your IP:
```bash
hostname -I | awk '{print $1}'
```
Then share: `http://YOUR_IP:5000`

## Project Structure
```
ai-ids-project/
├── backend/
│   ├── app.py                    # Flask API
│   ├── train_model.py            # Train Isolation Forest
│   ├── train_random_forest.py    # Train Random Forest
│   ├── requirements.txt          # Python dependencies
│   ├── setup.py                  # First-time setup script
│   ├── ai_engine/                # AI detection engines
│   ├── log_analysis/             # Log parsers + network monitor
│   ├── data/processed/           # NSL-KDD dataset (not in git)
│   └── models/                   # Trained models (not in git)
└── dashboard/
    └── src/
        ├── AIDashboard.jsx       # Main component
        ├── services/api.js       # API calls
        └── components/           # UI components + tabs
```

## Tech Stack
- Python 3.10+, Flask, scikit-learn, Scapy
- React 18, Recharts
- NSL-KDD Dataset (125,973 samples)
