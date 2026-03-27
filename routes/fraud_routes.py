from flask import Blueprint, request, jsonify
import json
import numpy as np
from models.transactions import Transaction
from utils.preprocess import preprocess_for_prediction
from utils.config import Config
import joblib
from utils.extensions import db

fraud_bp = Blueprint('fraud', __name__)

model     = None
threshold = None


def load_model():
    global model, threshold
    if model is None:
        model = joblib.load(Config.MODEL_PATH)
    if threshold is None:
        try:
            threshold = float(joblib.load(Config.THRESHOLD_PATH))
        except Exception:
            threshold = float(model.offset_)
    return model, threshold


@fraud_bp.route('/predict', methods=['POST'])
def predict_fraud():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        clf, thresh = load_model()

        feature_array = preprocess_for_prediction(data)
        X             = feature_array.reshape(1, -1)
        anomaly_score = float(clf.decision_function(X)[0])

        is_fraud = anomaly_score < thresh

        # Normalise score to 0-1 risk using the threshold as midpoint
        # scores well below threshold -> risk near 1.0
        # scores well above threshold -> risk near 0.0
        score_range = 0.15  # typical spread around threshold
        gap         = thresh - anomaly_score
        risk_score  = float(max(0.0, min(1.0, 0.5 + gap / score_range * 0.5)))
        confidence  = float(min(1.0, abs(gap) / score_range))

        transaction = Transaction(
            features=json.dumps(data),
            time=float(data.get('Time', 0.0)),
            amount=float(data.get('Amount', 0.0)),
            is_fraud=is_fraud,
            confidence=confidence,
            risk_score=risk_score,
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'is_fraud': is_fraud,
            'confidence': confidence,
            'risk_score': risk_score,
            'transaction_id': transaction.id,
            '_debug': {
                'anomaly_score': round(anomaly_score, 6),
                'threshold': round(thresh, 6),
            }
        }), 200

    except FileNotFoundError:
        return jsonify({'error': 'Model file not found. Please run retrain.py first.'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@fraud_bp.route('/history', methods=['GET'])
def get_history():
    try:
        limit = min(int(request.args.get('limit', 50)), 200)
        transactions = (
            Transaction.query
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .all()
        )
        history = []
        for tx in transactions:
            history.append({
                'id': tx.id,
                'features': json.loads(tx.features) if isinstance(tx.features, str) else tx.features,
                'Time': tx.time,
                'Amount': tx.amount,
                'is_fraud': tx.is_fraud,
                'confidence': float(tx.confidence),
                'risk_score': float(tx.risk_score),
                'created_at': tx.created_at.isoformat(),
            })
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@fraud_bp.route('/stats', methods=['GET'])
def get_stats():
    try:
        total       = Transaction.query.count()
        fraud_count = Transaction.query.filter_by(is_fraud=True).count()
        safe_count  = total - fraud_count
        avg_risk    = db.session.query(db.func.avg(Transaction.risk_score)).scalar() or 0.0
        return jsonify({
            'total': total,
            'fraud': fraud_count,
            'safe': safe_count,
            'fraud_rate': round(fraud_count / total * 100, 2) if total > 0 else 0,
            'avg_risk_score': round(float(avg_risk) * 100, 2),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@fraud_bp.route('/train', methods=['POST'])
def train_model_route():
    global model, threshold
    try:
        from ML.training_model import train_model
        model     = train_model()
        threshold = None
        return jsonify({'message': 'Model trained and loaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
