from flask import Blueprint, request, jsonify
import json
import numpy as np
from models.transactions import Transaction
from utils.preprocess import preprocess_for_prediction
from utils.config import Config
import joblib
import pandas as pd
from datetime import datetime
from utils.extensions import db

fraud_bp = Blueprint('fraud', __name__)

model = None

@fraud_bp.route('/predict', methods=['POST'])
def predict_fraud():
    global model
    try:
        data = request.json
        
        # Load model
        if model is None:
            model = joblib.load('ML/model.pkl')
        
        # Preprocess
        feature_array = preprocess_for_prediction(data)
        
        # Skip feature names check (model expects exact 30 features from training)
        # Pad feature_array to 30 cols for model
        feature_array_padded = np.pad(feature_array, (0, 1), mode='constant')  
        features_df = pd.DataFrame([feature_array_padded], columns=list(model.feature_names_in_))
        
        # Predict
        prediction = model.predict(features_df)[0]
        anomaly_score = model.decision_function(features_df)[0]
        
        is_fraud = prediction == -1
        confidence = abs(anomaly_score)
        risk_score = confidence if is_fraud else 1 - confidence
        
        # Save to DB - features as JSON string
        transaction = Transaction(
            features=json.dumps(data),
            time=data.get('Time', 0.0),
            amount=data.get('Amount', 0.0),
            is_fraud=is_fraud,
            confidence=float(confidence),
            risk_score=float(risk_score)
        )
        db.session.add(transaction)
        db.session.commit()
        
        result = {
            'is_fraud': bool(is_fraud),
            'confidence': float(confidence),
            'risk_score': float(risk_score)
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fraud_bp.route('/history', methods=['GET'])
def get_history():
    try:
        transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(50).all()
        history = []
        for tx in transactions:
            history.append({
                'id': tx.id,
                'features': json.loads(tx.features),
                'Time': tx.time,
                'Amount': tx.amount,
                'is_fraud': tx.is_fraud,
                'confidence': float(tx.confidence),
                'risk_score': float(tx.risk_score),
                'created_at': tx.created_at.isoformat()
            })
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fraud_bp.route('/train', methods=['POST'])
def train_model():
    global model
    try:
        from ML.training_model import train_model
        model = train_model()
        return jsonify({'message': 'Model trained and loaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
