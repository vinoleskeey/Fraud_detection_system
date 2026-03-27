import joblib
m = joblib.load('ML/model.pkl')
print(list(m.feature_names_in_))
print('Count:', len(m.feature_names_in_))
