"""
Tune Random Forest with better preprocessing
"""
import os
import json
import numpy as np
from data_loader import load_nslkdd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle

def train_tuned():
    X_train, X_test, y_train, y_test, scaler = load_nslkdd()

    print("Training tuned Random Forest...")
    
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    accuracy  = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall    = recall_score(y_test, y_pred, zero_division=0)
    f1        = f1_score(y_test, y_pred, zero_division=0)

    print("\n" + "="*60)
    print("TUNED RANDOM FOREST RESULTS")
    print("="*60)
    print(f"  Accuracy:   {accuracy*100:.2f}%")
    print(f"  Precision:  {precision*100:.2f}%")
    print(f"  Recall:     {recall*100:.2f}%")
    print(f"  F1-Score:   {f1*100:.2f}%")

    # Save tuned model
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    path = os.path.join(models_dir, 'random_forest_model.pkl')
    
    with open(path, 'wb') as f:
        pickle.dump({
            'model': model,
            'is_trained': True,
            'training_stats': {
                'algorithm': 'Random Forest (Tuned)',
                'n_samples': len(X_train),
                'n_features': X_train.shape[1],
                'training_date': 'tuned'
            }
        }, f)

    metrics = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'detection_rate': float(recall),
        'false_positive_rate': float(1 - precision),
        'algorithm': 'Random Forest (Tuned)'
    }

    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, 'rf_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)

    print("\n✅ Tuned model saved!")

if __name__ == '__main__':
    train_tuned()
