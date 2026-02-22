"""
Feature Extraction Module for AI-IDS Project
Iteration 1: Core AI Intelligence

This module extracts meaningful features from raw network traffic data
and prepares them for the AI detection engine.

Author: Your Name
Date: February 2026
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle
import os
import json

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FeatureExtractor:
    """
    Extracts and transforms features from network traffic data
    for AI-based anomaly detection.
    """
    
    def __init__(self):
        """Initialize the feature extractor with necessary encoders."""
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.protocol_encoder = LabelEncoder()
        self.feature_names = []
        self.is_fitted = False
        
    def extract_features(self, df):
        """
        Extract relevant features from raw network traffic data.
        
        This is where engineering intelligence is applied to select
        features that best represent network behavior.
        
        Args:
            df (pd.DataFrame): Raw network traffic data
            
        Returns:
            pd.DataFrame: Extracted features ready for AI processing
        """
        print("[INFO] Extracting features from network traffic...")
        
        # Create a copy to avoid modifying original data
        features_df = df.copy()
        
        # 1. Numerical features (already present)
        numerical_features = [
            'duration',
            'src_bytes',
            'dst_bytes',
            'src_packets',
            'dst_packets'
        ]
        
        # 2. Derived features (feature engineering)
        print("[INFO] Creating derived features...")
        
        # Bytes per second (traffic intensity)
        features_df['bytes_per_second'] = (
            (features_df['src_bytes'] + features_df['dst_bytes']) / 
            (features_df['duration'] + 0.001)  # Avoid division by zero
        )
        
        # Packet ratio (asymmetry indicator)
        features_df['packet_ratio'] = (
            features_df['src_packets'] / 
            (features_df['dst_packets'] + 1)  # Avoid division by zero
        )
        
        # Bytes ratio (data flow balance)
        features_df['bytes_ratio'] = (
            features_df['src_bytes'] / 
            (features_df['dst_bytes'] + 1)  # Avoid division by zero
        )
        
        # Average packet size
        features_df['avg_packet_size'] = (
            (features_df['src_bytes'] + features_df['dst_bytes']) /
            (features_df['src_packets'] + features_df['dst_packets'] + 1)
        )
        
        # 3. Categorical features (protocol encoding)
        print("[INFO] Encoding categorical features...")
        
        if 'protocol' in features_df.columns:
            if not self.is_fitted:
                features_df['protocol_encoded'] = self.protocol_encoder.fit_transform(
                    features_df['protocol']
                )
            else:
                features_df['protocol_encoded'] = self.protocol_encoder.transform(
                    features_df['protocol']
                )
        
        # Select final feature columns for AI model
        self.feature_names = numerical_features + [
            'bytes_per_second',
            'packet_ratio',
            'bytes_ratio',
            'avg_packet_size',
            'protocol_encoded'
        ]
        
        features_only = features_df[self.feature_names]
        
        print(f"[SUCCESS] Extracted {len(self.feature_names)} features")
        print(f"[INFO] Features: {self.feature_names}")
        
        return features_only, features_df['label'] if 'label' in features_df.columns else None
    
    def normalize_features(self, features, fit=True):
        """
        Normalize features using StandardScaler.
        This ensures all features have similar scale, improving AI performance.
        
        Args:
            features (pd.DataFrame): Extracted features
            fit (bool): Whether to fit the scaler (True for training, False for inference)
            
        Returns:
            np.ndarray: Normalized features
        """
        print("[INFO] Normalizing features...")
        
        if fit:
            normalized = self.scaler.fit_transform(features)
            self.is_fitted = True
            print("[SUCCESS] Features normalized and scaler fitted")
        else:
            if not self.is_fitted:
                raise ValueError("Scaler not fitted. Call with fit=True first.")
            normalized = self.scaler.transform(features)
            print("[SUCCESS] Features normalized using fitted scaler")
        
        return normalized
    
    def prepare_training_data(self, df, test_size=0.2):
        """
        Complete pipeline to prepare data for AI training.
        
        Args:
            df (pd.DataFrame): Raw network traffic dataset
            test_size (float): Proportion of data to use for testing
            
        Returns:
            tuple: (X_train, X_test, y_train, y_test, feature_names)
        """
        from sklearn.model_selection import train_test_split
        
        print("\n" + "="*60)
        print("PREPARING TRAINING DATA")
        print("="*60 + "\n")
        
        # Extract features
        features, labels = self.extract_features(df)
        
        # Normalize features
        features_normalized = self.normalize_features(features, fit=True)
        
        # Encode labels for evaluation (binary: normal vs attack)
        if labels is not None:
            labels_binary = (labels != 'BENIGN').astype(int)
        else:
            labels_binary = None
        
        # Split into training and testing sets
        if labels_binary is not None:
            X_train, X_test, y_train, y_test = train_test_split(
                features_normalized,
                labels_binary,
                test_size=test_size,
                random_state=42,
                stratify=labels_binary
            )
            
            print(f"[INFO] Training set size: {len(X_train)}")
            print(f"[INFO] Testing set size: {len(X_test)}")
            print(f"[INFO] Normal traffic in training: {(y_train == 0).sum()}")
            print(f"[INFO] Anomalous traffic in training: {(y_train == 1).sum()}")
            
            return X_train, X_test, y_train, y_test, self.feature_names
        else:
            # If no labels, return all data as training
            return features_normalized, None, None, None, self.feature_names
    
    def save_extractor(self, output_path='feature_extractor.pkl'):
        """
        Save the fitted feature extractor for later use.
        
        Args:
            output_path (str): Path to save the extractor
        """
        # Use absolute path to models directory
        full_path = os.path.join(BACKEND_DIR, 'models', output_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        extractor_data = {
            'scaler': self.scaler,
            'protocol_encoder': self.protocol_encoder,
            'feature_names': self.feature_names,
            'is_fitted': self.is_fitted
        }
        
        with open(full_path, 'wb') as f:
            pickle.dump(extractor_data, f)
        
        print(f"[SUCCESS] Feature extractor saved to: {full_path}")
    
    def load_extractor(self, input_path='feature_extractor.pkl'):
        """
        Load a previously saved feature extractor.
        
        Args:
            input_path (str): Path to load the extractor from
        """
        # Use absolute path to models directory
        full_path = os.path.join(BACKEND_DIR, 'models', input_path)
        
        with open(full_path, 'rb') as f:
            extractor_data = pickle.load(f)
        
        self.scaler = extractor_data['scaler']
        self.protocol_encoder = extractor_data['protocol_encoder']
        self.feature_names = extractor_data['feature_names']
        self.is_fitted = extractor_data['is_fitted']
        
        print(f"[SUCCESS] Feature extractor loaded from: {full_path}")
    
    def get_feature_importance_info(self):
        """
        Return information about features for documentation and explanation.
        
        Returns:
            dict: Feature descriptions
        """
        feature_info = {
            'duration': 'Connection duration in seconds',
            'src_bytes': 'Number of bytes sent from source',
            'dst_bytes': 'Number of bytes sent to destination',
            'src_packets': 'Number of packets sent from source',
            'dst_packets': 'Number of packets sent to destination',
            'bytes_per_second': 'Traffic intensity (derived)',
            'packet_ratio': 'Source to destination packet ratio (derived)',
            'bytes_ratio': 'Source to destination bytes ratio (derived)',
            'avg_packet_size': 'Average size of packets (derived)',
            'protocol_encoded': 'Network protocol (TCP/UDP/ICMP encoded)'
        }
        
        return feature_info


def main():
    """
    Main function to demonstrate feature extraction workflow.
    """
    print("\n" + "="*60)
    print("AI-IDS PROJECT - ITERATION 1")
    print("Feature Extraction Module")
    print("="*60 + "\n")
    
    # Load the cleaned dataset
    dataset_path = os.path.join(BACKEND_DIR, 'data', 'processed', 'cleaned_dataset.csv')
    
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        print(f"[SUCCESS] Loaded dataset: {len(df)} records")
    else:
        print("[ERROR] Dataset not found. Run prepare_dataset.py first.")
        return
    
    # Initialize feature extractor
    extractor = FeatureExtractor()
    
    # Prepare training data
    X_train, X_test, y_train, y_test, feature_names = extractor.prepare_training_data(df)
    
    # Display feature information
    print("\n" + "="*60)
    print("FEATURE INFORMATION")
    print("="*60)
    feature_info = extractor.get_feature_importance_info()
    for feature, description in feature_info.items():
        print(f"  • {feature}: {description}")
    
    # Save the feature extractor
    extractor.save_extractor('feature_extractor.pkl')
    
    # Save prepared data for AI training
    processed_dir = os.path.join(BACKEND_DIR, 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    np.save(os.path.join(processed_dir, 'X_train.npy'), X_train)
    np.save(os.path.join(processed_dir, 'X_test.npy'), X_test)
    np.save(os.path.join(processed_dir, 'y_train.npy'), y_train)
    np.save(os.path.join(processed_dir, 'y_test.npy'), y_test)
    
    print("\n[SUCCESS] Feature extraction completed!")
    print("[INFO] Processed data saved to data/processed/")
    print("[NEXT STEP] Run AI detection engine training\n")


if __name__ == "__main__":
    main()