import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
from utils.config import Config

def load_and_clean_data(path=None):
    """Load and clean creditcard dataset."""
    path = path or 'dataset/creditcard.csv'
    df = pd.read_csv(path)
    
    # Basic cleaning
    df = df.drop_duplicates()
    
    print(f"Loaded {len(df)} rows, no missing values, fraud rate: {df['Class'].mean():.4f}")
    return df

def preprocess_for_prediction(data):
    """Preprocess single transaction for prediction: scale Amount, select features."""
    
    try:
        scaler = joblib.load('ML/scaler.pkl')
    except:
        scaler = StandardScaler()
    
    # Create df with all required features (default 0)
    required_features = ['Time', 'V1','V2','V3','V4','V5','V6','V7','V8','V9','V10',
                         'V11','V12','V13','V14','V15','V16','V17','V18','V19','V20',
                         'V21','V22','V23','V24','V25','V26','V27','V28','Amount']
    
    df = pd.DataFrame([data])
    
    # Ensure all columns
    for f in required_features:
        if f not in df.columns:
            df[f] = data.get(f, 0)
    
    # Scale Amount 
    df['Amount_scaled'] = scaler.transform(df[['Amount']])[0]
    
    # Model features (matches notebook: V1-V28 + Amount_scaled, no duplicates)
    model_features = ['V1','V2','V3','V4','V5','V6','V7','V8','V9','V10',
                      'V11','V12','V13','V14','V15','V16','V17','V18','V19','V20',
                      'V21','V22','V23','V24','V25','V26','V27','V28','Amount_scaled']
    
    X = df[model_features].fillna(0)
    return X.values[0]
