"""
AI Detection Engine for AI-IDS Project
Iteration 1: Core AI Intelligence

This module implements the autonomous AI-based intrusion detection system
using Isolation Forest algorithm for anomaly detection.

Author: Your Name
Date: February 2026
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    classification_report, 
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)
import pickle
import os
import json
from datetime import datetime

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load configuration
def _load_config():
    """Load configuration from config.json file."""
    config_path = os.path.join(BACKEND_DIR, 'config.json')
    if not os.path.exists(config_path):
        # Return default config if file doesn't exist
        return {
            'data_path': 'data/processed',
            'model_path': 'models/ai_detection_model.pkl',
            'contamination': 0.1,
            'max_results': None,
            'random_state': 42,
            'model_params': {
                'n_estimators': 100,
                'max_samples': 'auto',
                'verbose': 0
            },
            'results_dir': 'results',
            'logs_dir': 'logs'
        }
    with open(config_path, 'r') as f:
        return json.load(f)

CONFIG = _load_config()


class AIDetectionEngine:
    """
    Autonomous AI-based anomaly detection engine.
    Uses Isolation Forest algorithm to detect network intrusions.
    """
    
    def __init__(self, contamination=None, random_state=None):
        """
        Initialize the AI detection engine.
        
        Args:
            contamination (float): Expected proportion of anomalies in dataset.
                                 If None, uses value from config.json
            random_state (int): Random seed for reproducibility.
                               If None, uses value from config.json
        """
        # Use config values if parameters not provided
        contamination = contamination or CONFIG.get('contamination', 0.1)
        random_state = random_state or CONFIG.get('random_state', 42)
        model_params = CONFIG.get('model_params', {})
        
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=model_params.get('n_estimators', 100),
            max_samples=model_params.get('max_samples', 'auto'),
            verbose=model_params.get('verbose', 0)
        )
        self.is_trained = False
        self.training_stats = {}
        self.contamination = contamination
        
    def train(self, X_train, y_train=None):
        """
        Train the AI model on network traffic data.
        
        For Isolation Forest, training is unsupervised (doesn't need labels),
        but we keep y_train for evaluation purposes.
        
        Args:
            X_train (np.ndarray): Training features
            y_train (np.ndarray): Training labels (for evaluation only)
        """
        print("\n" + "="*60)
        print("TRAINING AI DETECTION ENGINE")
        print("="*60 + "\n")
        
        print(f"[INFO] Algorithm: Isolation Forest")
        print(f"[INFO] Contamination rate: {self.contamination}")
        print(f"[INFO] Training samples: {len(X_train)}")
        
        # Train the model (unsupervised)
        print("[INFO] Training in progress...")
        self.model.fit(X_train)
        self.is_trained = True
        
        print("[SUCCESS] Model training completed!")
        
        # Store training statistics
        self.training_stats = {
            'training_date': datetime.now().isoformat(),
            'n_samples': len(X_train),
            'n_features': X_train.shape[1],
            'contamination': self.contamination,
            'algorithm': 'Isolation Forest'
        }
        
        # Evaluate on training data if labels are provided
        if y_train is not None:
            print("\n[INFO] Evaluating on training data...")
            y_pred = self.predict(X_train)
            self._evaluate_model(y_train, y_pred, "Training")
    
    def predict(self, X):
        """
        Predict whether network traffic is normal or anomalous.
        
        Args:
            X (np.ndarray): Features to classify
            
        Returns:
            np.ndarray: Predictions (0 = normal, 1 = anomaly)
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Isolation Forest returns -1 for anomalies, 1 for normal
        # We convert to 0 (normal) and 1 (anomaly)
        predictions = self.model.predict(X)
        predictions = np.where(predictions == -1, 1, 0)
        
        return predictions
    
    def predict_with_scores(self, X):
        """
        Predict with anomaly scores.
        
        Args:
            X (np.ndarray): Features to classify
            
        Returns:
            tuple: (predictions, anomaly_scores)
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = self.predict(X)
        
        # Get anomaly scores (more negative = more anomalous)
        # We invert so higher score = more anomalous
        anomaly_scores = -self.model.score_samples(X)
        
        return predictions, anomaly_scores
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate the model on test data.
        
        Args:
            X_test (np.ndarray): Test features
            y_test (np.ndarray): True labels
            
        Returns:
            dict: Evaluation metrics
        """
        print("\n" + "="*60)
        print("MODEL EVALUATION")
        print("="*60 + "\n")
        
        # Make predictions
        y_pred, anomaly_scores = self.predict_with_scores(X_test)
        
        # Calculate metrics
        metrics = self._evaluate_model(y_test, y_pred, "Testing", anomaly_scores)
        
        return metrics
    
    def _evaluate_model(self, y_true, y_pred, dataset_name="", anomaly_scores=None):
        """
        Internal method to calculate and display evaluation metrics.
        
        Args:
            y_true (np.ndarray): True labels
            y_pred (np.ndarray): Predicted labels
            dataset_name (str): Name of dataset being evaluated
            anomaly_scores (np.ndarray): Anomaly scores (optional)
            
        Returns:
            dict: Evaluation metrics
        """
        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        # Detection rate and false positive rate
        detection_rate = tp / (tp + fn) if (tp + fn) > 0 else 0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        
        # Display results
        print(f"[{dataset_name} Set Evaluation]")
        print(f"  Accuracy:           {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"  Precision:          {precision:.4f}")
        print(f"  Recall:             {recall:.4f}")
        print(f"  F1-Score:           {f1:.4f}")
        print(f"  Detection Rate:     {detection_rate:.4f} ({detection_rate*100:.2f}%)")
        print(f"  False Positive Rate: {false_positive_rate:.4f} ({false_positive_rate*100:.2f}%)")
        
        print(f"\n  Confusion Matrix:")
        print(f"    True Negatives:   {tn}")
        print(f"    False Positives:  {fp}")
        print(f"    False Negatives:  {fn}")
        print(f"    True Positives:   {tp}")
        
        # Detailed classification report
        print(f"\n  Classification Report:")
        print(classification_report(y_true, y_pred, 
                                   target_names=['Normal', 'Anomaly'],
                                   zero_division=0))
        
        # Store metrics
        metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'detection_rate': float(detection_rate),
            'false_positive_rate': float(false_positive_rate),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
            'dataset': dataset_name
        }
        
        return metrics
    
    def detect_batch(self, X, return_scores=True):
        """
        Detect anomalies in a batch of network traffic.
        
        Args:
            X (np.ndarray): Network traffic features
            return_scores (bool): Whether to return anomaly scores
            
        Returns:
            list: Detection results with details
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions, scores = self.predict_with_scores(X)
        
        results = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            result = {
                'event_id': i,
                'timestamp': datetime.now().isoformat(),
                'prediction': 'anomaly' if pred == 1 else 'normal',
                'anomaly_score': float(score),
                'confidence': float(abs(score))  # Higher score = more confident
            }
            results.append(result)
        
        return results
    
    def detect_live(self, packet_features):
        """
        Real-time detection for live network packet features.
        Used for streaming data from network monitor.
        
        Args:
            packet_features (np.ndarray or list): Features from a single packet or batch
                                                  Shape: (n_features,) for single packet
                                                  Shape: (n_packets, n_features) for batch
        
        Returns:
            dict or list: Detection result(s) with score and prediction
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Cannot detect on live data.")
        
        # Handle single packet (1D array)
        if isinstance(packet_features, (list, np.ndarray)):
            packet_features = np.array(packet_features)
            if packet_features.ndim == 1:
                packet_features = packet_features.reshape(1, -1)
        
        # Use batch detection for consistency
        results = self.detect_batch(packet_features)
        
        # Return single result if input was single packet
        if len(results) == 1 and packet_features.shape[0] == 1:
            return results[0]
        
        return results
    
    def save_model(self, output_path=None):
        """
        Save the trained model to disk.
        
        Args:
            output_path (str): Path to save the model. If None, uses value from config.json
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Cannot save untrained model.")
        
        # Use config value if path not provided
        output_path = output_path or CONFIG.get('model_path', 'models/ai_detection_model.pkl')
        
        # Use absolute path to models directory
        full_path = os.path.join(BACKEND_DIR, output_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'is_trained': self.is_trained,
            'training_stats': self.training_stats,
            'contamination': self.contamination
        }
        
        with open(full_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"[SUCCESS] Model saved to: {full_path}")
    
    def load_model(self, input_path=None):
        """
        Load a previously trained model from disk.
        
        Args:
            input_path (str): Path to load the model from. If None, uses value from config.json
        """
        # Use config value if path not provided
        input_path = input_path or CONFIG.get('model_path', 'models/ai_detection_model.pkl')
        
        # Use absolute path to models directory
        full_path = os.path.join(BACKEND_DIR, input_path)
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Model file not found: {full_path}")
        
        with open(full_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.is_trained = model_data['is_trained']
        self.training_stats = model_data['training_stats']
        self.contamination = model_data['contamination']
        
        print(f"[SUCCESS] Model loaded from: {full_path}")
        print(f"[INFO] Model trained on: {self.training_stats.get('training_date', 'Unknown')}")
    
    def get_model_info(self):
        """
        Get information about the trained model.
        
        Returns:
            dict: Model information
        """
        return {
            'is_trained': self.is_trained,
            'training_stats': self.training_stats,
            'algorithm': 'Isolation Forest',
            'contamination': self.contamination
        }


def main():
    """
    Main function to demonstrate AI detection engine workflow.
    All paths and parameters are loaded from config.json
    """
    print("\n" + "="*60)
    print("AI-IDS PROJECT - ITERATION 1")
    print("AI Detection Engine")
    print("="*60 + "\n")
    
    # Load all paths from config
    data_path = CONFIG.get('data_path', 'data/processed')
    results_dir = CONFIG.get('results_dir', 'results')
    contamination = CONFIG.get('contamination', 0.1)
    model_path = CONFIG.get('model_path', 'models/ai_detection_model.pkl')
    max_results = CONFIG.get('max_results')  # None means save all results
    
    # Use absolute paths
    data_dir = os.path.join(BACKEND_DIR, data_path)
    results_dir = os.path.join(BACKEND_DIR, results_dir)
    
    if not os.path.exists(data_dir):
        print("[ERROR] Processed data not found. Run extractor.py first.")
        print(f"[ERROR] Expected path: {data_dir}")
        return
    
    print(f"[CONFIG] Data path: {data_path}")
    print(f"[CONFIG] Model path: {model_path}")
    print(f"[CONFIG] Contamination rate: {contamination}")
    print(f"[CONFIG] Max results: {max_results or 'All'}\n")
    
    X_train = np.load(os.path.join(data_dir, 'X_train.npy'))
    X_test = np.load(os.path.join(data_dir, 'X_test.npy'))
    y_train = np.load(os.path.join(data_dir, 'y_train.npy'))
    y_test = np.load(os.path.join(data_dir, 'y_test.npy'))
    
    print(f"[INFO] Loaded training data: {X_train.shape}")
    print(f"[INFO] Loaded testing data: {X_test.shape}")
    
    # Initialize AI engine with config values
    engine = AIDetectionEngine(contamination=contamination)
    
    # Train the model
    engine.train(X_train, y_train)
    
    # Evaluate the model
    metrics = engine.evaluate(X_test, y_test)
    
    # Save evaluation metrics
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, 'evaluation_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"\n[SUCCESS] Evaluation metrics saved to {results_dir}/evaluation_metrics.json")
    
    # Save the trained model using config
    engine.save_model()
    
    # Generate detection results for dashboard
    print("\n[INFO] Generating detection results for dashboard...")
    detection_results = engine.detect_batch(X_test)
    
    # Apply max_results limit if configured, otherwise save all
    if max_results is not None:
        detection_results = detection_results[:max_results]
        print(f"[INFO] Limiting results to {max_results} (from config)")
    else:
        print(f"[INFO] Saving all {len(detection_results)} results (max_results = null in config)")
    
    # Save detection results
    with open(os.path.join(results_dir, 'detection_results.json'), 'w') as f:
        json.dump(detection_results, f, indent=4)
    
    print(f"[SUCCESS] Detection results saved to {results_dir}/detection_results.json")
    
    # Summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    model_info = engine.get_model_info()
    print(f"  Algorithm: {model_info['algorithm']}")
    print(f"  Training completed: {model_info['is_trained']}")
    print(f"  Training samples: {model_info['training_stats']['n_samples']}")
    print(f"  Features used: {model_info['training_stats']['n_features']}")
    print(f"  Contamination rate: {model_info['contamination']}")
    print(f"  Model path: {model_path}")
    print("="*60)
    
    print("\n[SUCCESS] AI Detection Engine training completed!")
    print("[NEXT STEP] Build Flask backend API\n")


if __name__ == "__main__":
    main()