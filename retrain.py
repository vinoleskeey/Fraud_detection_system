import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

print("Loading dataset...")
df = pd.read_csv('dataset/creditcard.csv')
df = df.drop_duplicates()
print(f"Rows: {len(df)}, Fraud: {(df['Class']==1).sum()}, Rate: {df['Class'].mean():.4f}")

features = ['V1','V2','V3','V4','V5','V6','V7','V8','V9','V10',
            'V11','V12','V13','V14','V15','V16','V17','V18','V19','V20',
            'V21','V22','V23','V24','V25','V26','V27','V28']

print("Fitting scaler...")
scaler = StandardScaler()
df['Amount_scaled'] = scaler.fit_transform(df[['Amount']])

X = df[features + ['Amount_scaled']].values

print("Training Isolation Forest (contamination=0.0017)...")
model = IsolationForest(contamination=0.0017, random_state=42, n_estimators=200, n_jobs=-1)
model.fit(X)

scores_fraud = model.decision_function(df[df['Class']==1][features + ['Amount_scaled']].values)
scores_safe  = model.decision_function(df[df['Class']==0][features + ['Amount_scaled']].values)

print(f"\nFraud scores: min={scores_fraud.min():.4f}, max={scores_fraud.max():.4f}, mean={scores_fraud.mean():.4f}")
print(f"Safe  scores: min={scores_safe.min():.4f},  max={scores_safe.max():.4f},  mean={scores_safe.mean():.4f}")
print(f"Model offset_: {model.offset_:.4f}")

# Set custom threshold = 75th percentile of fraud scores
# catches most fraud while keeping false positives low
custom_threshold = float(np.percentile(scores_fraud, 75))
print(f"Custom threshold (75th pct of fraud scores): {custom_threshold:.4f}")

flagged = (scores_fraud < custom_threshold).sum()
print(f"Fraud caught with custom threshold: {flagged}/{len(scores_fraud)} ({flagged/len(scores_fraud)*100:.1f}%)")

fp = (scores_safe < custom_threshold).sum()
print(f"False positives: {fp}/{len(scores_safe)} ({fp/len(scores_safe)*100:.2f}%)")

print("\nSaving model, scaler, and threshold...")
joblib.dump(model,            'ML/model.pkl')
joblib.dump(scaler,           'ML/scaler.pkl')
joblib.dump(custom_threshold, 'ML/threshold.pkl')
print("Done.")
