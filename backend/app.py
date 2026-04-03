import eventlet
eventlet.monkey_patch()

"""
Flask Backend API for AI-IDS Project
Iteration 1: Core AI Intelligence

This module provides RESTful API endpoints for the React dashboard
to communicate with the AI detection engine.

Author: Your Name
Date: February 2026
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flasgger import Swagger
from flask_cors import CORS
from datetime import datetime
import numpy as np
import json
import os

from database import init_db, save_log_alert, save_network_alert, get_log_alerts as db_get_log_alerts, get_network_alerts as db_get_network_alerts, clear_alerts as db_clear_alerts, get_stats

# Load central config
with open(os.path.join(os.path.dirname(__file__), 'config.json')) as _f:
    CONFIG = json.load(_f)
import sys
import logging

# Configure logging to file AND console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Add backend directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine.anomaly_detector import AIDetectionEngine
from feature_engineering.extractor import FeatureExtractor


# Initialize Flask app
app = Flask(__name__)

# Swagger API documentation — available at http://localhost:5000/apidocs/
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "AI-IDS — Autonomous Intrusion Detection System API",
        "description": "Real-time intrusion detection using Isolation Forest trained on NSL-KDD dataset. Detects SSH brute force, SQL injection, port scans, network floods.",
        "version": "3.0.0",
        "contact": {"name": "GitHub", "url": "https://github.com/CHELSY-POWERS/Project-Soutenance"}
    },
    "tags": [
        {"name": "Health",    "description": "System status"},
        {"name": "Detection", "description": "AI model predictions"},
        {"name": "Metrics",   "description": "Model performance"},
        {"name": "Logs",      "description": "Log analysis"},
        {"name": "Network",   "description": "Packet capture"},
        {"name": "Dashboard", "description": "Overview data"},
        {"name": "Tests",     "description": "Attack simulation"},
    ]
})
CORS(app)  # Enable CORS for React frontend
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', logger=False, engineio_logger=False)

# Absolute base directory (backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Global variables for model and extractor
detection_engine = None
feature_extractor = None
model_loaded = False


def load_models():
    """
    Load the trained AI model and feature extractor on startup.
    """
    global detection_engine, feature_extractor, model_loaded
    
    print("[INFO] Loading AI models...", flush=True)
    sys.stdout.flush()
    
    # Absolute path relative to this file (backend/)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Load detection engine
        print(f"[DEBUG] Loading model from: {os.path.join(base_dir, 'models/ai_detection_model.pkl')}", flush=True)
        detection_engine = AIDetectionEngine()
        detection_engine.load_model()
        
        # Load feature extractor
        print(f"[DEBUG] Loading extractor from: {os.path.join(base_dir, 'models/feature_extractor.pkl')}", flush=True)
        feature_extractor = FeatureExtractor()
        feature_extractor.load_extractor(os.path.join(base_dir, 'models/feature_extractor.pkl'))
        
        model_loaded = True
        print("[SUCCESS] Models loaded successfully!", flush=True)
        
    except Exception as e:
        print(f"[ERROR] Failed to load models: {str(e)}", flush=True)
        print(f"[ERROR] Traceback: {type(e).__name__}", flush=True)
        print("[INFO] Models will need to be trained first.")
        model_loaded = False


# Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    System health check
    ---
    tags: [Health]
    responses:
      200:
        description: System is healthy
        schema:
          properties:
            status:    {type: string, example: healthy}
            model_loaded: {type: boolean, example: true}
            message:   {type: string}
    """
    """
    Health check endpoint to verify API is running.
    """
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'message': 'AI-IDS Backend API is running'
    }), 200


@app.route('/api/model/info', methods=['GET'])
def get_model_info():
    """
    Get information about the loaded AI model.
    """
    if not model_loaded:
        return jsonify({
            'error': 'Model not loaded',
            'message': 'Please train the model first'
        }), 503
    
    model_info = detection_engine.get_model_info()
    return jsonify(model_info), 200


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    Get statistics from detection results for dashboard.
    """
    try:
        # Load detection results
        results_path = os.path.join(BASE_DIR, 'results/detection_results.json')
        
        if not os.path.exists(results_path):
            return jsonify({
                'error': 'No detection results found',
                'message': 'Please run detection first'
            }), 404
        
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        # Calculate statistics
        total_events = len(results)
        anomalies = sum(1 for r in results if r['prediction'] == 'anomaly')
        normal = total_events - anomalies
        
        # Anomaly scores distribution
        anomaly_scores = [r['anomaly_score'] for r in results]
        avg_anomaly_score = np.mean(anomaly_scores)
        max_anomaly_score = np.max(anomaly_scores)
        
        # Get top anomalies
        top_anomalies = sorted(
            [r for r in results if r['prediction'] == 'anomaly'],
            key=lambda x: x['anomaly_score'],
            reverse=True
        )[:10]
        
        statistics = {
            'total_events': total_events,
            'normal_events': normal,
            'anomalous_events': anomalies,
            'anomaly_percentage': round((anomalies / total_events) * 100, 2),
            'avg_anomaly_score': round(avg_anomaly_score, 4),
            'max_anomaly_score': round(max_anomaly_score, 4),
            'top_anomalies': top_anomalies
        }
        
        return jsonify(statistics), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to calculate statistics',
            'message': str(e)
        }), 500


@app.route('/api/detection/results', methods=['GET'])
def get_detection_results():
    """
    Get AI model detection results
    ---
    tags: [Detection]
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 22544
        description: Number of results per page
      - name: filter
        in: query
        type: string
        enum: [all, normal, anomaly]
        default: all
    responses:
      200:
        description: Detection results from Isolation Forest model
        schema:
          properties:
            results:
              type: array
              items:
                properties:
                  event_id:      {type: integer}
                  prediction:    {type: string, enum: [normal, anomaly]}
                  anomaly_score: {type: number, description: "Isolation score 0-1"}
                  confidence:    {type: number}
                  timestamp:     {type: string}
            pagination:
              type: object
    """
    """
    Get paginated detection results.
    """
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        filter_type = request.args.get('filter', 'all')  # all, normal, anomaly
        
        # Load detection results
        results_path = os.path.join(BASE_DIR, 'results/detection_results.json')
        
        if not os.path.exists(results_path):
            return jsonify({
                'error': 'No detection results found'
            }), 404
        
        with open(results_path, 'r') as f:
            all_results = json.load(f)
        
        # Filter results
        if filter_type == 'normal':
            filtered_results = [r for r in all_results if r['prediction'] == 'normal']
        elif filter_type == 'anomaly':
            filtered_results = [r for r in all_results if r['prediction'] == 'anomaly']
        else:
            filtered_results = all_results
        
        # Paginate
        total = len(filtered_results)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_results = filtered_results[start:end]
        
        return jsonify({
            'results': paginated_results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get detection results',
            'message': str(e)
        }), 500


@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """
    Get model performance metrics
    ---
    tags: [Metrics]
    responses:
      200:
        description: Real metrics calculated on NSL-KDD test set (22,544 samples)
        schema:
          properties:
            accuracy:   {type: number, example: 0.7855}
            precision:  {type: number, example: 0.8197}
            recall:     {type: number, example: 0.7990}
            f1_score:   {type: number, example: 0.8092}
            dataset:    {type: string, example: "NSL-KDD Full Test Set"}
    """
    """
    Get evaluation metrics from the model.
    """
    try:
        metrics_path = os.path.join(BASE_DIR, 'results/evaluation_metrics.json')
        
        if not os.path.exists(metrics_path):
            return jsonify({
                'error': 'No evaluation metrics found'
            }), 404
        
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        return jsonify(metrics), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get metrics',
            'message': str(e)
        }), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict whether network traffic is normal or anomalous.
    This endpoint accepts network traffic features and returns predictions.
    """
    if not model_loaded:
        return jsonify({
            'error': 'Model not loaded',
            'message': 'Please train the model first'
        }), 503
    
    try:
        # Get data from request
        data = request.get_json()
        
        if 'features' not in data:
            return jsonify({
                'error': 'Missing features',
                'message': 'Please provide network traffic features'
            }), 400
        
        features = np.array(data['features'])
        
        # Make prediction
        predictions, scores = detection_engine.predict_with_scores(features)
        
        results = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            results.append({
                'event_id': i,
                'prediction': 'anomaly' if pred == 1 else 'normal',
                'anomaly_score': float(score),
                'confidence': float(abs(score))
            })
        
        return jsonify({
            'predictions': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500


@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """
    Get dashboard overview summary
    ---
    tags: [Dashboard]
    responses:
      200:
        description: Summary KPIs for dashboard overview
        schema:
          properties:
            total_events:    {type: integer, example: 22544}
            anomalies_detected: {type: integer}
            normal_traffic:  {type: integer}
            anomaly_rate:    {type: number, example: 55.48}
            model:
              type: object
              properties:
                algorithm: {type: string, example: Isolation Forest}
                accuracy:  {type: number, example: 78.55}
    """
    """
    Get comprehensive summary for dashboard home page.
    """
    try:
        # Load all necessary data
        results_path = os.path.join(BASE_DIR, 'results/detection_results.json')
        metrics_path = os.path.join(BASE_DIR, 'results/evaluation_metrics.json')
        
        summary = {}
        
        # Detection statistics
        if os.path.exists(results_path):
            with open(results_path, 'r') as f:
                results = json.load(f)
            
            total_events = len(results)
            anomalies = sum(1 for r in results if r['prediction'] == 'anomaly')
            
            summary['detection'] = {
                'total_events': total_events,
                'normal_events': total_events - anomalies,
                'anomalous_events': anomalies,
                'anomaly_rate': round((anomalies / total_events) * 100, 2) if total_events > 0 else 0
            }
        
        # Model performance metrics
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            summary['performance'] = {
                'accuracy': round(metrics.get('accuracy', 0) * 100, 2),
                'precision': round(metrics.get('precision', 0) * 100, 2),
                'recall': round(metrics.get('recall', 0) * 100, 2),
                'f1_score': round(metrics.get('f1_score', 0) * 100, 2),
                'detection_rate': round(metrics.get('detection_rate', 0) * 100, 2),
                'false_positive_rate': round(metrics.get('false_positive_rate', 0) * 100, 2)
            }
        
        # Model information
        if model_loaded:
            model_info = detection_engine.get_model_info()
            summary['model'] = {
                'algorithm': model_info.get('algorithm', 'Unknown'),
                'is_trained': model_info.get('is_trained', False),
                'training_date': str(model_info.get('training_stats', {}).get('training_date', '2026-02-21'))[:10]
            }
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get dashboard summary',
            'message': str(e)
        }), 500


# Error handlers

# ══ TEST & SIMULATION ENDPOINTS ══════════════════════════════════════

import subprocess
import threading

network_monitor_process = None

@app.route('/api/test/simulate-attack', methods=['POST'])
def simulate_attack():
    """
    Simulate an attack for demonstration
    ---
    tags: [Tests]
    parameters:
      - in: body
        name: body
        schema:
          properties:
            attack_type:
              type: string
              enum: [sqli, portscan, bruteforce, ping_flood]
              example: sqli
    responses:
      200:
        description: Attack simulated successfully
        schema:
          properties:
            success:     {type: boolean}
            attack_type: {type: string}
            details:     {type: array, items: {type: string}}
            next_step:   {type: string, description: "Where to see results"}
    """
    """Simulate different attack types for demo purposes"""
    try:
        data     = request.get_json() or {}
        attack   = data.get('attack_type', 'sqli')
        results  = []

        if attack == 'sqli':
            # Simulate SQL injection attempts in Apache logs
            payloads = [
                "curl -s 'http://localhost/login?user=admin%27--&pass=anything' -o /dev/null",
                "curl -s 'http://localhost/search?q=1+UNION+SELECT+username,password+FROM+users' -o /dev/null",
                "curl -s 'http://localhost/search?q=1%27;+SLEEP(5)--' -o /dev/null",
                "curl -s 'http://localhost/search?q=1+UNION+SELECT+table_name+FROM+information_schema.tables' -o /dev/null",
            ]
            for cmd in payloads:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            results = ['Boolean bypass', 'UNION extraction', 'Time-based blind', 'Schema enumeration']

        elif attack == 'portscan':
            # Simulate port scan using nmap if available
            cmd = "nmap -sT -p 22,80,443,3306,5432,6379 127.0.0.1 -T4 2>/dev/null || echo 'nmap not available'"
            subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
            results = ['Port 22 (SSH)', 'Port 80 (HTTP)', 'Port 443 (HTTPS)', 'Port 3306 (MySQL)']

        elif attack == 'bruteforce':
            # Simulate SSH brute force attempts
            for i in range(6):
                cmd = f"ssh -o ConnectTimeout=1 -o StrictHostKeyChecking=no wronguser@127.0.0.1 2>/dev/null || true"
                subprocess.run(cmd, shell=True, capture_output=True, timeout=3)
            results = ['6 failed SSH attempts simulated']

        elif attack == 'ping_flood':
            cmd = "ping -c 25 -i 0.05 127.0.0.1 > /dev/null 2>&1"
            subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
            results = ['25 ICMP packets sent']

        tips = {
            'sqli':       'Go to Logs tab → click Run Log Scan to see SQLi alerts',
            'portscan':   'Check Network tab (monitor must be running)',
            'bruteforce': 'Go to Logs tab → click Run Log Scan to see brute force alerts',
            'ping_flood': 'Check Network tab for ICMP flood (monitor must be running)',
        }
        return jsonify({
            'success':     True,
            'attack_type': attack,
            'message':     f'{attack} attack simulated successfully',
            'details':     results,
            'next_step':   tips.get(attack, 'Check Logs and Network tabs'),
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test/network-monitor/start', methods=['POST'])
def start_network_monitor():
    """Start the network monitor as background process"""
    global network_monitor_process
    try:
        if network_monitor_process and network_monitor_process.poll() is None:
            return jsonify({'success': False, 'message': 'Network monitor already running'}), 200

        venv_python = os.path.join(BASE_DIR, '..', 'venv', 'bin', 'python')
        script_path = os.path.join(BASE_DIR, 'log_analysis', 'network_monitor.py')

        data      = request.get_json() or {}
        # Auto-detect interface if not provided
        def get_default_iface():
            try:
                import subprocess as sp2
                r = sp2.run(['ip','route','show','default'], capture_output=True, text=True)
                parts = r.stdout.strip().split()
                return parts[parts.index('dev')+1] if 'dev' in parts else 'wlp4s0'
            except: return 'wlp4s0'
        interface = data.get('interface') or get_default_iface()

        cmd = ['sudo', os.path.abspath(venv_python), script_path, '--interface', interface]
        network_monitor_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return jsonify({
            'success':   True,
            'message':   f'Network monitor started on {interface}',
            'pid':       network_monitor_process.pid,
            'interface': interface
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test/network-monitor/stop', methods=['POST'])
def stop_network_monitor():
    """Stop the network monitor"""
    global network_monitor_process
    try:
        if network_monitor_process and network_monitor_process.poll() is None:
            network_monitor_process.terminate()
            network_monitor_process = None
            return jsonify({'success': True, 'message': 'Network monitor stopped'}), 200
        return jsonify({'success': False, 'message': 'Network monitor is not running'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test/network-monitor/status', methods=['GET'])
def network_monitor_status():
    """Check if network monitor is running"""
    global network_monitor_process
    running = network_monitor_process is not None and network_monitor_process.poll() is None
    return jsonify({'running': running}), 200


@app.route('/api/test/clear-alerts', methods=['POST'])
def clear_alerts():
    """Clear all network alerts for a fresh demo"""
    try:
        cleared = []
        for filename in ['network_alerts.json', 'log_alerts.json']:
            path = os.path.join(BASE_DIR, 'results', filename)
            with open(path, 'w') as f:
                json.dump([], f)
            cleared.append(filename)
        return jsonify({'success': True, 'message': f'Cleared: {", ".join(cleared)}', 'cleared': cleared}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500




@app.route('/api/test/monitor-command', methods=['GET'])
def get_monitor_command():
    """Return dynamic monitor command for this specific machine"""
    venv_python = os.path.abspath(os.path.join(BASE_DIR, '..', 'venv', 'bin', 'python'))
    script_path = os.path.abspath(os.path.join(BASE_DIR, 'log_analysis', 'network_monitor.py'))
    try:
        import subprocess as sp2
        result = sp2.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True, timeout=3)
        parts = result.stdout.strip().split()
        iface = parts[parts.index('dev') + 1] if 'dev' in parts else 'wlp4s0'
    except Exception:
        iface = 'wlp4s0'
    return jsonify({'command': f"sudo {venv_python} {script_path} --interface {iface}", 'interface': iface}), 200


# ══ WEBSOCKET EVENTS ══════════════════════════════════════════════

@socketio.on('connect')
def handle_connect():
    """Client connected to WebSocket"""
    print(f"[WS] Client connected")
    emit('connected', {
        'status': 'connected',
        'message': 'Real-time stream active',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[WS] Client disconnected")

@socketio.on('ping_server')
def handle_ping():
    emit('pong_server', {'timestamp': datetime.now().isoformat()})

def emit_alert(event_name, data):
    """Helper to emit alert to all connected clients"""
    try:
        socketio.emit(event_name, {**data, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        print(f"[WS] Emit error: {e}")

def emit_system_status():
    """Emit current system status to all clients"""
    try:
        alerts_path = os.path.join(BASE_DIR, 'results', 'log_alerts.json')
        net_path    = os.path.join(BASE_DIR, 'results', 'network_alerts.json')
        log_count   = len(json.load(open(alerts_path))) if os.path.exists(alerts_path) else 0
        net_count   = len(json.load(open(net_path)))    if os.path.exists(net_path)    else 0
        socketio.emit('system_status', {
            'log_alerts':     log_count,
            'network_alerts': net_count,
            'monitor_running': network_monitor_process is not None and network_monitor_process.poll() is None,
            'timestamp':      datetime.now().isoformat()
        })
    except Exception as e:
        print(f"[WS] Status emit error: {e}")


@app.route('/api/database/stats', methods=['GET'])
def database_stats():
    """
    Get database statistics
    ---
    tags: [Dashboard]
    responses:
      200:
        description: Real-time database statistics
    """
    try:
        stats = get_stats()
        return jsonify({**stats, 'status': 'connected', 'db': 'SQLite'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


# Initialize and run


@app.route('/api/logs/alerts', methods=['GET'])
def get_log_alerts():
    """
    Get log analysis alerts
    ---
    tags: [Logs]
    responses:
      200:
        description: Alerts detected from auth.log, Apache2, and syslog
        schema:
          properties:
            total:  {type: integer}
            high:   {type: integer, description: "HIGH severity alerts"}
            medium: {type: integer}
            alerts:
              type: array
              items:
                properties:
                  event_type:    {type: string, example: failed_login}
                  threat_level:  {type: string, enum: [HIGH, MEDIUM, LOW]}
                  ip_address:    {type: string, example: "192.168.1.100"}
                  anomaly_score: {type: number}
                  live:          {type: boolean, description: "True if detected by real-time file watcher"}
    """
    """Get real-time log analysis alerts"""
    try:
        # Read from SQLite database (primary source)
        alerts = db_get_log_alerts(limit=200)

        # Fallback to JSON if database is empty
        if not alerts:
            alerts_path = os.path.join(BASE_DIR, 'results/log_alerts.json')
            if os.path.exists(alerts_path):
                with open(alerts_path, 'r') as f:
                    alerts = json.load(f)

        high   = sum(1 for a in alerts if a.get('threat_level') == 'HIGH')
        medium = sum(1 for a in alerts if a.get('threat_level') == 'MEDIUM')
        # Enrich with MITRE ATT&CK + risk score
        for a in alerts:
            etype = a.get('event_type', '')
            score = float(a.get('anomaly_score', 0.5))
            sev   = 3 if a.get('threat_level') == 'HIGH' else 1
            a['risk_score']      = round(sev * score, 2)
            # Dynamic MITRE lookup with intelligent fallback
            mitre_map = CONFIG.get('mitre', {})
            if etype in mitre_map:
                a['mitre'] = mitre_map[etype]
            elif 'login' in etype or 'auth' in etype or 'password' in etype:
                a['mitre'] = {'id': 'T1110', 'name': 'Brute Force', 'tactic': 'Credential Access'}
            elif 'scan' in etype or 'probe' in etype:
                a['mitre'] = {'id': 'T1046', 'name': 'Network Service Scan', 'tactic': 'Discovery'}
            elif 'sql' in etype or 'inject' in etype or 'web' in etype:
                a['mitre'] = {'id': 'T1190', 'name': 'Exploit Public App', 'tactic': 'Initial Access'}
            elif 'flood' in etype or 'dos' in etype or 'memory' in etype or 'kernel' in etype:
                a['mitre'] = {'id': 'T1499', 'name': 'Endpoint DoS', 'tactic': 'Impact'}
            elif 'root' in etype or 'sudo' in etype or 'priv' in etype:
                a['mitre'] = {'id': 'T1548', 'name': 'Abuse Elevation Control', 'tactic': 'Privilege Escalation'}
            else:
                a['mitre'] = {'id': 'T0000', 'name': etype.replace('_',' ').title(), 'tactic': 'Unknown'}
            a['threat_category'] = CONFIG.get('threat_intelligence', {}).get(etype, 'Unknown')

        return jsonify({
            'alerts':  alerts,
            'total':   len(alerts),
            'high':    high,
            'medium':  medium,
            'sources': {
                'auth_log': sum(1 for a in alerts if a.get('source') == 'auth.log'),
                'apache':   sum(1 for a in alerts if a.get('source') == 'apache2'),
                'syslog':   sum(1 for a in alerts if a.get('source') == 'syslog'),
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/logs/scan', methods=['POST'])
def trigger_log_scan():
    """
    Trigger manual log scan
    ---
    tags: [Logs]
    responses:
      200:
        description: Scan complete — returns count of threats found
        schema:
          properties:
            status:  {type: string, example: complete}
            total:   {type: integer}
            high:    {type: integer}
            medium:  {type: integer}
            message: {type: string}
    """
    """Trigger a log scan synchronously and return results immediately"""
    try:
        import sys
        sys.path.insert(0, BASE_DIR)
        from log_analysis.log_detector import LogAnomalyDetector

        detector = LogAnomalyDetector()
        detector.run_once()

        alerts = detector.alerts
        high   = sum(1 for a in alerts if a.get('threat_level') == 'HIGH')
        medium = sum(1 for a in alerts if a.get('threat_level') == 'MEDIUM')

        # Emit WebSocket event to all connected clients
        emit_alert('new_log_alerts', {
            'total':  len(alerts),
            'high':   high,
            'medium': medium,
            'alerts': alerts[:10],  # Send first 10 for instant display
        })

        # Save alerts to database
        for alert in alerts:
            save_log_alert(alert)

        # Push to all WebSocket clients instantly
        socketio.emit('new_log_alerts', {
            'total':   len(alerts),
            'high':    high,
            'medium':  medium,
            'alerts':  alerts[:10],
            'timestamp': datetime.now().isoformat(),
        })

        return jsonify({
            'message': f'Scan complete — {len(alerts)} alerts found',
            'status':  'complete',
            'total':   len(alerts),
            'high':    high,
            'medium':  medium,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 500



@app.route('/api/logs/sqli', methods=['GET'])
def get_sqli_alerts():
    """Scan Apache logs for SQL injection attacks"""
    try:
        import sys
        sys.path.append(BASE_DIR)
        from log_analysis.sqli_detector import SQLiDetector
        
        detector = SQLiDetector()
        alerts   = detector.scan_apache_log()

        high   = sum(1 for a in alerts if a.get('severity', 0) >= 4)
        medium = sum(1 for a in alerts if a.get('severity', 0) == 3)

        return jsonify({
            'alerts':        alerts,
            'total':         len(alerts),
            'high_severity': high,
            'medium_severity': medium,
            'message':       f"Found {len(alerts)} SQLi attempts"
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/network/alerts', methods=['GET'])
def get_network_alerts():
    """
    Get network monitoring alerts
    ---
    tags: [Network]
    responses:
      200:
        description: Alerts captured by Scapy packet sniffer
        schema:
          properties:
            total:       {type: integer}
            high:        {type: integer}
            unique_ips:  {type: integer}
            attack_types: {type: object}
            alerts:
              type: array
              items:
                properties:
                  src_ip:      {type: string}
                  dst_ip:      {type: string}
                  attack_type: {type: string, enum: [PORT_SCAN, ICMP_FLOOD, UDP_FLOOD, SYN_FLOOD]}
                  severity:    {type: integer}
    """
    """Get real-time network monitoring alerts"""
    try:
        path = os.path.join(BASE_DIR, 'results/network_alerts.json')
        if not os.path.exists(path):
            return jsonify({'alerts': [], 'total': 0,
                'message': 'Network monitor not running yet'}), 200

        with open(path, 'r') as f:
            alerts = json.load(f)

        high   = sum(1 for a in alerts if a.get('threat_level') == 'HIGH')
        medium = sum(1 for a in alerts if a.get('threat_level') == 'MEDIUM')

        attack_types = {}
        for a in alerts:
            t = a.get('attack_type', 'unknown')
            attack_types[t] = attack_types.get(t, 0) + 1

        return jsonify({
            'alerts':       alerts[-50:],
            'total':        len(alerts),
            'high':         high,
            'medium':       medium,
            'attack_types': attack_types,
            'unique_ips':   len(set(a.get('src_ip') for a in alerts)),
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI-IDS BACKEND API - ITERATION 3")
    print("="*60 + "\n")
    
    # Load models on startup
    load_models()
    
    # Run the Flask app
    print("\n[INFO] Starting Flask server...")
    print("[INFO] API will be available at: http://localhost:5000")
    print("[INFO] React frontend should connect to this address")
    print("\n" + "="*60 + "\n")
    
    # Initialize database
    init_db()

    # Start real-time file watcher
    try:
        from log_analysis.file_watcher import LogFileWatcher
        watcher = LogFileWatcher(socketio=socketio)
        watcher.start()
        print("[INFO] ✅ Real-time file watcher started!")
    except Exception as e:
        print(f"[WARN] File watcher failed to start: {e}")

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
