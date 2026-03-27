import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import pandas as pd
from utils.config import Config


def load_and_clean_data(path=None):
    path = path or Config.DATASET_PATH
    df = pd.read_csv(path)
    df = df.drop_duplicates()
    print(f"Loaded {len(df)} rows — fraud rate: {df['Class'].mean():.4f}")
    return df


def preprocess_for_prediction(data: dict) -> np.ndarray:
    try:
        scaler = joblib.load(Config.SCALER_PATH)
    except Exception:
        scaler = StandardScaler()

    v_features = [
        'V1',  'V2',  'V3',  'V4',  'V5',  'V6',  'V7',  'V8',  'V9',  'V10',
        'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
        'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28',
    ]

    amount        = float(data.get('Amount', 0))
    amount_scaled = float(scaler.transform(np.array([[amount]]))[0][0])
    v_values      = [float(data.get(f, 0)) for f in v_features]

    # 29 features: V1-V28 + Amount_scaled (matches retrained model)
    return np.array(v_values + [amount_scaled], dtype=np.float64)
