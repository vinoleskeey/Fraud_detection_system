import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.preprocess import load_and_clean_data
from utils.config import Config

def train_model():
    """Train fraud detection model and save"""
    print("Loading and cleaning data...")
    df = load_and_clean_data(Config.DATASET_PATH)
    
    # Prepare features (V1-V28 + scaled Amount)
    print("Preparing features...")
    scaler = StandardScaler()
    df['Amount_scaled'] = scaler.fit_transform(df[['Amount']])
    
    features = ['V1','V2','V3','V4','V5','V6','V7','V8','V9','V10',
                'V11','V12','V13','V14','V15','V16','V17','V18','V19','V20',
                'V21','V22','V23','V24','V25','V26','V27','V28','Amount_scaled']
    
    X = df[features]
    
    print("Training Isolation Forest...")
    model = IsolationForest(contamination=0.0017, random_state=42)  # ~0.17% fraud rate
    model.fit(X)
    
    print("Saving model...")
    joblib.dump(model, Config.MODEL_PATH)
    print(f"Model saved to {Config.MODEL_PATH}")
    
    # Test prediction
    fraud_count = (df['Class'] == 1).sum()
    print(f"Dataset fraud rate: {fraud_count/len(df):.4f}")
    
    return model

if __name__ == "__main__":
    train_model()
