# AI-IDS — Autonomous Intrusion Detection System

A complete cybersecurity project using Machine Learning to detect network intrusions in real time.

## 🔍 What It Does
- **Isolation Forest + Random Forest** AI models trained on NSL-KDD dataset (125,973 samples)
- **Real-time log analysis** — scans auth.log, Apache, syslog for threats
- **SQL Injection detection** — detects 7 categories of SQLi attacks
- **Live network monitoring** — packet sniffing via Scapy
- **Attack simulation** — test panel to launch simulated attacks from the browser
- **React dashboard** — 6 tabs: Overview, Results, Metrics, Logs, Network, Tests

## 🚀 Quick Start (First Time)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd ai-ids-project
```

### 2. Download the NSL-KDD Dataset (one time only)
- Go to: https://www.kaggle.com/datasets/hassan06/nslkdd
- Download and extract the zip
- Copy `KDDTrain+.txt` and `KDDTest+.txt` into `backend/data/processed/`

### 3. Run setup (installs everything + trains AI models)
```bash
python backend/setup.py
```
This takes about 3-5 minutes the first time.

### 4. Start the backend
```bash
cd backend
source ../venv/bin/activate       # Mac/Linux
# venv\Scripts\activate           # Windows
python app.py
```

### 5. Start the frontend (new terminal)
```bash
cd dashboard
npm install
npm start
```

### 6. Open browser
```
http://localhost:3000
```

## 🧪 Running Tests From the Dashboard
1. Open the **TESTS** tab
2. Click **Launch SQL Injection** — alerts appear in Logs tab
3. Click **Launch Port Scan** — triggers port scan detection
4. Click **Start Monitor** — starts live network monitoring
5. Check **NETWORK** tab for real-time alerts

## 📁 Project Structure
```
ai-ids-project/
├── backend/
│   ├── app.py                      # Flask API (9 endpoints)
│   ├── train_model.py              # Train Isolation Forest
│   ├── train_random_forest.py      # Train Random Forest
│   ├── requirements.txt            # Python dependencies
│   ├── setup.py                    # First-time setup script
│   ├── ai_engine/
│   │   └── anomaly_detector.py     # Core AI detection engine
│   ├── log_analysis/
│   │   ├── log_detector.py         # Real-time log scanning
│   │   ├── log_parser.py           # Log file parser
│   │   ├── log_scorer.py           # Threat scorer
│   │   ├── sqli_detector.py        # SQL injection detector
│   │   └── network_monitor.py      # Packet sniffer
│   ├── data/processed/             # NSL-KDD dataset (not in git)
│   ├── models/                     # Trained models (not in git)
│   └── results/                    # Detection results (not in git)
└── dashboard/
    └── src/
        ├── AIDashboard.jsx         # Main component
        ├── services/api.js         # All API calls
        └── components/
            ├── UI.jsx              # Shared components
            └── tabs/
                ├── OverviewTab.jsx
                ├── ResultsTab.jsx
                ├── MetricsTab.jsx
                ├── LogsTab.jsx
                ├── NetworkTab.jsx
                └── TestsTab.jsx

## 🤖 AI Model Performance (NSL-KDD Test Set — 22,544 samples)
| Metric    | Isolation Forest |
|-----------|-----------------|
| Accuracy  | 78.55%          |
| Precision | 81.97%          |
| Recall    | 79.90%          |
| F1-Score  | 80.92%          |

## ⚠️ Important Notes
- Models and dataset are NOT in the repository (too large)
- Run `python backend/setup.py` to generate them
- Network monitoring requires `sudo` privileges
- The system monitors **your real system logs** — alerts are genuine
