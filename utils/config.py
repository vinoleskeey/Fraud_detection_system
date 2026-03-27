import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fraud-detection-dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fraud_detection.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH     = os.path.join(BASE_DIR, 'ML', 'model.pkl')
    SCALER_PATH    = os.path.join(BASE_DIR, 'ML', 'scaler.pkl')
    THRESHOLD_PATH = os.path.join(BASE_DIR, 'ML', 'threshold.pkl')
    DATASET_PATH = os.environ.get('DATASET_PATH') or os.path.join(BASE_DIR, 'dataset', 'creditcard.csv')
