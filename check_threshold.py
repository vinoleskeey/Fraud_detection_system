import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
import joblib

model  = joblib.load('ML/model.pkl')
scaler = joblib.load('ML/scaler.pkl')

df = pd.read_csv('dataset/creditcard.csv')
df = df.drop_duplicates()

fraud_df = df[df['Class'] == 1].head(10)

features = ['V1','V2','V3','V4','V5','V6','V7','V8','V9','V10',
            'V11','V12','V13','V14','V15','V16','V17','V18','V19','V20',
            'V21','V22','V23','V24','V25','V26','V27','V28']

print("=== Real fraud transaction scores ===")
for i, (_, row) in enumerate(fraud_df.iterrows()):
    amt_scaled = scaler.transform([[row['Amount']]])[0][0]
    X = np.array([[row[f] for f in features] + [amt_scaled, amt_scaled]])
    score = model.decision_function(X)[0]
    pred  = model.predict(X)[0]
    print(f"Fraud #{i+1}: score={score:.4f}, pred={pred}, Amount={row['Amount']:.2f}")

print()
print("=== Real safe transaction scores (sample) ===")
safe_df = df[df['Class'] == 0].sample(5, random_state=42)
for i, (_, row) in enumerate(safe_df.iterrows()):
    amt_scaled = scaler.transform([[row['Amount']]])[0][0]
    X = np.array([[row[f] for f in features] + [amt_scaled, amt_scaled]])
    score = model.decision_function(X)[0]
    pred  = model.predict(X)[0]
    print(f"Safe  #{i+1}: score={score:.4f}, pred={pred}, Amount={row['Amount']:.2f}")

print()
print("=== Score distribution across all fraud cases ===")
scores = []
for _, row in df[df['Class'] == 1].iterrows():
    amt_scaled = scaler.transform([[row['Amount']]])[0][0]
    X = np.array([[row[f] for f in features] + [amt_scaled, amt_scaled]])
    scores.append(model.decision_function(X)[0])
scores = np.array(scores)
print(f"Fraud scores: min={scores.min():.4f}, max={scores.max():.4f}, mean={scores.mean():.4f}, median={np.median(scores):.4f}")
print(f"Threshold:    {model.offset_:.4f}")
print(f"Fraud flagged by model: {(scores < model.offset_).sum()} / {len(scores)}")
print()

# Suggest a better threshold
pct5 = np.percentile(scores, 20)
print(f"Suggested threshold (20th pct of fraud scores): {pct5:.4f}")
print(f"First real fraud row V-values:")
row = df[df['Class'] == 1].iloc[0]
print({f: round(row[f], 4) for f in features[:10]})
print("Amount:", row['Amount'])
