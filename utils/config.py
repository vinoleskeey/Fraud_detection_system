import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fraud-detection-dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fraud_detection.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = 'ML/model.pkl'
    DATASET_PATH = r'C:\Users\VICTOR SHITTU\Documents\Fraud detection system\dataset\creditcard.csv'
