import joblib
import pandas as pd
from algorithms.compressed_if import train_compressed_if
from shap_explain import explain_model
from algorithms.lstm_autoencoder import (
    LSTMAutoencoder,
    create_sequences
)
from algorithms.xgboost_model import XGBoostModel
from algorithms.oneclass_svm import OneClassSVMModel
from algorithms.isolation_forest import IsolationForestModel
from algorithms.random_forest import train_random_forest
from evaluation import evaluate_model
from preprocess import (
    load_dataset,
    prepare_data,
    split_dataset,
    scale_data
)

print("=" * 60)
print("AI Predictive Maintenance")
print("=" * 60)

df = load_dataset("../data/final_dataset_complete_v3.csv")

import os

print("\nCurrent working directory:", os.getcwd())
print("Absolute dataset path:",
      os.path.abspath("../data/final_dataset_complete_v3.csv"))

X, y = prepare_data(df)

print("\nGround Truth Distribution")
print(y.value_counts())

print("\nGround Truth Percentage")
print((y.value_counts(normalize=True) * 100).round(2))

(
    X_train,
    X_val,
    X_test,
    y_train,
    y_val,
    y_test
) = split_dataset(X, y)

(
    X_train_sc,
    X_val_sc,
    X_test_sc,
    scaler
) = scale_data(
    X_train,
    X_val,
    X_test
)

# =====================================================
# Create LSTM Sequences
# =====================================================

X_train_seq, y_train_seq = create_sequences(
    X_train_sc,
    y_train,
    sequence_length=5
)

X_val_seq, y_val_seq = create_sequences(
    X_val_sc,
    y_val,
    sequence_length=5
)

X_test_seq, y_test_seq = create_sequences(
    X_test_sc,
    y_test,
    sequence_length=5
)

print("\nSequence Shapes")
print("Train :", X_train_seq.shape)
print("Validation :", X_val_seq.shape)
print("Test :", X_test_seq.shape)

joblib.dump(
    scaler,
    "../models/scaler.pkl"
)

print("\nScaler saved successfully.")

rf_model = train_random_forest(
    X_train_sc,
    y_train
)

iso = IsolationForestModel()

iso.fit(
    X_train_sc,
    y_train,
    X_val_sc,
    y_val
)

iso.save()

ocsvm = OneClassSVMModel()

ocsvm.fit(
    X_train_sc,
    y_train,
    X_val_sc,
    y_val
)

ocsvm.save()

xgb = XGBoostModel()

xgb.fit(
    X_train_sc,
    y_train
)

xgb.save()

# =====================================================
# LSTM Autoencoder
# =====================================================

lstm = LSTMAutoencoder()

# Train only on NORMAL sequences
X_train_normal = X_train_seq[y_train_seq == 0]

lstm.fit(X_train_normal)

lstm.save()

# =====================================================
# SHAP Explainability
# =====================================================

explain_model(
    rf_model,
    X_train_sc,
    X_test_sc,
    X.columns.tolist()
)

compressed_if = train_compressed_if(
    X_train_sc,
    y_train,
    X_val_sc,
    y_val,
    X.columns.tolist(),
    top_k=8
)

rf_results = evaluate_model(
    rf_model,
    X_test_sc,
    y_test,
    "Random Forest"
)

iso_results = evaluate_model(
    iso,
    X_test_sc,
    y_test,
    "Isolation Forest"
)

ocsvm_results = evaluate_model(
    ocsvm,
    X_test_sc,
    y_test,
    "One-Class SVM"
)
 
xgb_results = evaluate_model(
    xgb,
    X_test_sc,
    y_test,
    "XGBoost"
) 

lstm_results = evaluate_model(
    lstm,
    X_test_seq,
    y_test_seq,
    "LSTM Autoencoder"
)

compressed_results = evaluate_model(
    compressed_if,
    X_test_sc,
    y_test,
    "Compressed IF"
)

print(rf_results)
print(iso_results)
print(ocsvm_results)
print(xgb_results)
print(lstm_results)
print(compressed_results)

comparison = pd.DataFrame([
    rf_results,
    iso_results,
    ocsvm_results,
    xgb_results,
    lstm_results,
    compressed_results
])

comparison.to_csv(
    "../results/final_model_comparison.csv",
    index=False
)

print("\nFinal comparison saved.")

print(comparison)