"""
Standalone training script to fit an Isolation Forest on NSL-KDD data.

This script trains a model, prints evaluation, saves joblib artifacts,
and wraps the trained model into the project's `AIDetectionEngine` format
so the Flask backend can load it with the existing loader.

Usage:
    cd backend
    python train_model.py

"""
import os
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, accuracy_score
import joblib

from data_loader import load_nslkdd

try:
    from ai_engine.anomaly_detector import AIDetectionEngine
except Exception:
    AIDetectionEngine = None


def train_model():
    X_train, X_test, y_train, y_test, scaler = load_nslkdd()

    print("Training Isolation Forest model...")

    model = IsolationForest(
        n_estimators=100,
        contamination=0.4,
        random_state=42
    )

    model.fit(X_train)

    raw_predictions = model.predict(X_test)
    predictions = [1 if p == -1 else 0 for p in raw_predictions]

    print("\n📊 Model Performance:")
    print(f"Accuracy: {accuracy_score(y_test, predictions) * 100:.2f}%")
    print("\nDetailed Report:")
    print(classification_report(y_test, predictions, target_names=['Normal', 'Attack']))

    # Ensure models dir exists and save artifacts
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    os.makedirs(models_dir, exist_ok=True)

    joblib_path = os.path.join(models_dir, 'isolation_forest_model.pkl')
    scaler_path = os.path.join(models_dir, 'scaler.pkl')

    joblib.dump(model, joblib_path)
    joblib.dump(scaler, scaler_path)
    print(f"\n✅ Joblib model saved to: {joblib_path}")
    print(f"✅ Scaler saved to: {scaler_path}")

    # If project AIDetectionEngine is available, wrap and save in expected format
    if AIDetectionEngine is not None:
        engine = AIDetectionEngine(contamination=0.4)
        engine.model = model
        engine.is_trained = True
        engine.training_stats = {
            'training_date': __import__('datetime').datetime.now().strftime('%Y-%m-%d'),
            'n_samples': getattr(X_train, 'shape', (len(X_train),))[0],
            'n_features': getattr(X_train, 'shape', (None, None))[1] if hasattr(X_train, 'shape') else None,
            'contamination': 0.4,
            'algorithm': 'Isolation Forest (joblib-wrapped)'
        }

        # Save in the same format AIDetectionEngine.save_model uses
        try:
            engine.save_model('ai_detection_model.pkl')
            print("✅ Wrapped model saved for backend loader: backend/models/ai_detection_model.pkl")
        except Exception as e:
            print(f"⚠️  Could not save wrapped model: {e}")
    else:
        print("⚠️  AIDetectionEngine not importable; wrapped model not created.")

    return model, scaler


if __name__ == '__main__':
    train_model()
