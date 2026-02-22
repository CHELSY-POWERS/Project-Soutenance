import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

def load_nslkdd(train_path='data/processed/KDDTrain+.txt', test_path='data/processed/KDDTest+.txt'):
    
    # Column names for the dataset (it has no header by default)
    columns = [
        'duration', 'protocol_type', 'service', 'flag', 'src_bytes',
        'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot',
        'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
        'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
        'num_access_files', 'num_outbound_cmds', 'is_host_login',
        'is_guest_login', 'count', 'srv_count', 'serror_rate',
        'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
        'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
        'dst_host_srv_count', 'dst_host_same_srv_rate',
        'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
        'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
        'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
        'dst_host_srv_rerror_rate', 'label', 'difficulty'
    ]
    
    # Load the files
    print("Loading training data...")
    train = pd.read_csv(train_path, header=None, names=columns)
    
    print("Loading test data...")
    test = pd.read_csv(test_path, header=None, names=columns)
    
    # Drop the 'difficulty' column (we don't need it)
    train = train.drop('difficulty', axis=1)
    test = test.drop('difficulty', axis=1)
    
    # Simplify labels: normal = 0, any attack = 1
    train['label'] = train['label'].apply(lambda x: 0 if x == 'normal' else 1)
    test['label'] = test['label'].apply(lambda x: 0 if x == 'normal' else 1)
    
    # Convert text columns to numbers (AI only understands numbers)
    encoder = LabelEncoder()
    for col in ['protocol_type', 'service', 'flag']:
        train[col] = encoder.fit_transform(train[col])
        test[col] = encoder.transform(test[col])
    
    # Separate features (X) and labels (y)
    X_train = train.drop('label', axis=1)
    y_train = train['label']
    X_test = test.drop('label', axis=1)
    y_test = test['label']
    
    # Scale the data (make all numbers on the same scale)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    print("✅ Data loaded successfully!")
    print(f"   Training samples: {len(X_train)}")
    print(f"   Test samples: {len(X_test)}")
    
    return X_train, X_test, y_train, y_test, scaler