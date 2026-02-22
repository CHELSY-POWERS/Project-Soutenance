"""
Train Random Forest model on NSL-KDD dataset
"""
import os
import json
import numpy as np
from data_loader import load_nslkdd
from ai_engine.random_forest_detector import RandomForestDetector

def train():
    # Load data
    X_train, X_test, y_train, y_test, scaler = load_nslkdd()

    # Train Random Forest
    detector = RandomForestDetector(n_estimators=100)
    detector.train(X_train, y_train)

    # Evaluate
    metrics = detector.evaluate(X_test, y_test)

    # Save model
    detector.save_model('random_forest_model.pkl')

    # Save metrics
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(results_dir, exist_ok=True)

    with open(os.path.join(results_dir, 'rf_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)
    print("\n✅ Random Forest metrics saved!")

    # Compare both models
    print("\n" + "="*60)
    print("MODEL COMPARISON SUMMARY")
    print("="*60)
    print(f"  Random Forest Accuracy:  {metrics['accuracy']*100:.2f}%")
    print(f"  Random Forest F1-Score:  {metrics['f1_score']*100:.2f}%")
    print(f"  Random Forest Detection: {metrics['detection_rate']*100:.2f}%")
    print("="*60)
    print("\n✅ Done! Now run app.py to see results in dashboard.")

if __name__ == '__main__':
    train()
