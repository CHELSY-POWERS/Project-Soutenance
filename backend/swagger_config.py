"""
Swagger/OpenAPI Documentation Configuration
AI-IDS — Autonomous Intrusion Detection System
"""

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/api/docs/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/",
    "title": "AI-IDS API",
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "AI-IDS — Autonomous Intrusion Detection System API",
        "description": """
## AI-Powered Intrusion Detection System

This API powers a real-time network intrusion detection system using:
- **Isolation Forest** machine learning model trained on NSL-KDD dataset (125,973 samples)
- **Real-time log analysis** of auth.log, Apache2, and syslog
- **Live packet capture** via Scapy network monitoring
- **WebSocket** push notifications for instant threat alerts

### Detection Capabilities
- SSH brute force & failed login attempts
- SQL injection in web server logs
- Network floods (ICMP, UDP, TCP)
- Port scans
- Privilege escalation attempts

### Architecture
```
Log Files → File Watcher (0.5s) → Flask API → WebSocket → React Dashboard
Network Packets → Scapy Monitor → Flask API → React Dashboard
NSL-KDD Dataset → Isolation Forest → Batch Predictions → React Dashboard
```
        """,
        "version": "3.0.0",
        "contact": {
            "name": "AI-IDS Project",
            "url": "https://github.com/CHELSY-POWERS/Project-Soutenance"
        }
    },
    "basePath": "/",
    "schemes": ["http"],
    "tags": [
        {"name": "Health",     "description": "System health and model status"},
        {"name": "Detection",  "description": "AI model predictions and results"},
        {"name": "Metrics",    "description": "Model performance metrics"},
        {"name": "Logs",       "description": "Log file analysis and alerts"},
        {"name": "Network",    "description": "Network traffic monitoring"},
        {"name": "Dashboard",  "description": "Dashboard summary data"},
        {"name": "Tests",      "description": "Attack simulation and testing"},
    ],
    "securityDefinitions": {},
}
