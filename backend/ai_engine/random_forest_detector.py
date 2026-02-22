"""
Random Forest Detector
Supervised model that classifies specific attack types
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
import pickle
import os
import json
from datetime import datetime

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RandomForestDetector:

    def __init__(self, n_estimators=100, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1, class_weight='balanced'
        )
        self.is_trained = False
        self.training_stats = {}

    def train(self, X_train, y_train):
        print("\n" + "="*60)
        print("TRAINING RANDOM FOREST DETECTOR")
        print("="*60)
        print(f"[INFO] Training samples: {len(X_train)}")
        print(f"[INFO] Training in progress...")

        self.model.fit(X_train, y_train)
        self.is_trained = True

        self.training_stats = {
            'training_date': datetime.now().isoformat(),
            'n_samples': len(X_train),
            'n_features': X_train.shape[1],
            'algorithm': 'Random Forest'
        }
        print("[SUCCESS] Random Forest training completed!")

    def predict(self, X):
        if not self.is_trained:
            raise ValueError("Model not trained yet.")
        return self.model.predict(X)

    def predict_proba(self, X):
        if not self.is_trained:
            raise ValueError("Model not trained yet.")
        return self.model.predict_proba(X)

    def evaluate(self, X_test, y_test):
        print("\n" + "="*60)
        print("RANDOM FOREST EVALUATION")
        print("="*60)

        y_pred = self.predict(X_test)

        accuracy  = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall    = recall_score(y_test, y_pred, zero_division=0)
        f1        = f1_score(y_test, y_pred, zero_division=0)

        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()

        detection_rate     = tp / (tp + fn) if (tp + fn) > 0 else 0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0

        print(f"  Accuracy:            {accuracy*100:.2f}%")
        print(f"  Precision:           {precision*100:.2f}%")
        print(f"  Recall:              {recall*100:.2f}%")
        print(f"  F1-Score:            {f1*100:.2f}%")
        print(f"  Detection Rate:      {detection_rate*100:.2f}%")
        print(f"  False Positive Rate: {false_positive_rate*100:.2f}%")
        print(f"\n  Classification Report:")
        print(classification_report(y_test, y_pred,
              target_names=['Normal', 'Attack'], zero_division=0))

        metrics = {
            'accuracy':            float(accuracy),
            'precision':           float(precision),
            'recall':              float(recall),
            'f1_score':            float(f1),
            'detection_rate':      float(detection_rate),
            'false_positive_rate': float(false_positive_rate),
            'true_negatives':      int(tn),
            'false_positives':     int(fp),
            'false_negatives':     int(fn),
            'true_positives':      int(tp),
            'algorithm':           'Random Forest'
        }
        return metrics

    def save_model(self, filename='random_forest_model.pkl'):
        if not self.is_trained:
            raise ValueError("Cannot save untrained model.")
        path = os.path.join(BACKEND_DIR, 'models', filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'is_trained': self.is_trained,
                'training_stats': self.training_stats
            }, f)
        print(f"[SUCCESS] Random Forest model saved to: {path}")

    def load_model(self, filename='random_forest_model.pkl'):
        path = os.path.join(BACKEND_DIR, 'models', filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model not found: {path}")
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.model          = data['model']
        self.is_trained     = data['is_trained']
        self.training_stats = data['training_stats']
        print(f"[SUCCESS] Random Forest loaded from: {path}")

    def get_model_info(self):
        return {
            'algorithm':     'Random Forest',
            'is_trained':    self.is_trained,
            'training_stats': self.training_stats
        }
