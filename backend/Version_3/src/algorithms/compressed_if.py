"""
===========================================================
SHAP-Based Compressed Isolation Forest
===========================================================
"""

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score

try:
    from Version_3.src.config import IF_PARAMS
except ImportError:
    from config import IF_PARAMS

class CompressedIF:

        def __init__(self, model, threshold, indices, features):

            self.model = model
            self.threshold = threshold
            self.indices = indices
            self.features = features

        def predict(self, X):

            X_small = X[:, self.indices]

            scores = self.model.decision_function(X_small)

            return (scores < self.threshold).astype(int)

        def decision_function(self, X):

            X_small = X[:, self.indices]

            return self.model.decision_function(X_small)
        
        def predict_proba(self, X):

            scores = -self.decision_function(X)

            scores = (scores - scores.min()) / (
                scores.max() - scores.min() + 1e-8
            )

            return np.column_stack(
                [1 - scores, scores]
            )
        
def train_compressed_if(
        X_train,
        y_train,
        X_val,
        y_val,
        feature_names,
        top_k=8
):

    print("\n" + "=" * 60)
    print("Training SHAP-Based Compressed Isolation Forest")
    print("=" * 60)

    # -----------------------------------------------------
    # Load SHAP feature importance
    # -----------------------------------------------------

    importance = pd.read_csv("../results/feature_importance.csv")

    top_features = importance.head(top_k)["Feature"].tolist()

    print("\nSelected Features")

    for feature in top_features:
        print("•", feature)

    # -----------------------------------------------------
    # Get column indices
    # -----------------------------------------------------

    indices = [
        feature_names.index(feature)
        for feature in top_features
    ]

    # -----------------------------------------------------
    # Compress dataset
    # -----------------------------------------------------

    X_train_small = X_train[:, indices]

    X_val_small = X_val[:, indices]

    # -----------------------------------------------------
    # Train only on NORMAL samples
    # -----------------------------------------------------

    X_normal = X_train_small[y_train == 0]

    model = IsolationForest(**IF_PARAMS)

    model.fit(X_normal)

    # -----------------------------------------------------
    # Threshold optimization
    # -----------------------------------------------------

    scores = model.decision_function(X_val_small)

    thresholds = np.linspace(
        scores.min(),
        scores.max(),
        100
    )

    best_threshold = 0
    best_f1 = -1

    for threshold in thresholds:

        prediction = (
            scores < threshold
        ).astype(int)

        score = f1_score(
            y_val,
            prediction,
            zero_division=0
        )

        if score > best_f1:

            best_f1 = score
            best_threshold = threshold

    print(f"\nBest Threshold : {best_threshold:.5f}")
    print(f"Validation F1  : {best_f1:.4f}")

    # -----------------------------------------------------
    # Prediction Wrapper
    # -----------------------------------------------------

    compressed_model = CompressedIF(
        model,
        best_threshold,
        indices,
        top_features
    )

    joblib.dump(
        compressed_model,
        "../models/compressed_if.pkl"
    )

    print("\nModel saved -> ../models/compressed_if.pkl")

    return compressed_model