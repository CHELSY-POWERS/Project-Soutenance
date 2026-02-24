"""
Flask Backend API for AI-IDS Project
Iteration 1: Core AI Intelligence

This module provides RESTful API endpoints for the React dashboard
to communicate with the AI detection engine.

Author: Your Name
Date: February 2026
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import json
import os
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
CORS(app)  # Enable CORS for React frontend

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
        detection_engine.load_model(os.path.join(base_dir, 'models/ai_detection_model.pkl'))
        
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
                'training_date': model_info.get('training_stats', {}).get('training_date', 'Unknown')
            }
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get dashboard summary',
            'message': str(e)
        }), 500


# Error handlers

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
    """Get real-time log analysis alerts"""
    try:
        alerts_path = os.path.join(BASE_DIR, 'results/log_alerts.json')
        if not os.path.exists(alerts_path):
            return jsonify({
                'alerts': [],
                'total': 0,
                'message': 'No log scan run yet'
            }), 200
        with open(alerts_path, 'r') as f:
            alerts = json.load(f)
        high   = sum(1 for a in alerts if a.get('threat_level') == 'HIGH')
        medium = sum(1 for a in alerts if a.get('threat_level') == 'MEDIUM')
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
    """Manually trigger a log scan"""
    try:
        import subprocess
        subprocess.Popen([
            '/home/chelsy/ai-ids-project/venv/bin/python',
            os.path.join(BASE_DIR, 'log_analysis/log_detector.py')
        ])
        return jsonify({
            'message': 'Log scan triggered successfully',
            'status': 'running'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



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


if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI-IDS BACKEND API - ITERATION 1")
    print("="*60 + "\n")
    
    # Load models on startup
    load_models()
    
    # Run the Flask app
    print("\n[INFO] Starting Flask server...")
    print("[INFO] API will be available at: http://localhost:5000")
    print("[INFO] React frontend should connect to this address")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)