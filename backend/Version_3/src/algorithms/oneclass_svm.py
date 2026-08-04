"""
===========================================================
One-Class SVM
===========================================================
"""

import joblib
import numpy as np

from sklearn.svm import OneClassSVM
from sklearn.metrics import f1_score

try:
    from Version_3.src.config import OCSVM_PARAMS
except ImportError:
    from config import OCSVM_PARAMS


class OneClassSVMModel:

    def __init__(self):

        self.model = OneClassSVM(**OCSVM_PARAMS)

        self.threshold = 0.0

    # --------------------------------------------------
    # Train
    # --------------------------------------------------

    def fit(self, X_train, y_train, X_val=None, y_val=None):

        print("\n" + "=" * 60)
        print("Training One-Class SVM")
        print("=" * 60)

        X_normal = X_train[y_train == 0]

        print(f"Normal samples : {len(X_normal)}")

        self.model.fit(X_normal)

        if X_val is not None and y_val is not None:

            self.optimize_threshold(
                X_val,
                y_val
            )

        return self

    # --------------------------------------------------
    # Threshold Optimization
    # --------------------------------------------------

    def optimize_threshold(self, X_val, y_val):

        print("Optimizing threshold...")

        scores = self.model.decision_function(X_val)

        thresholds = np.linspace(
            scores.min(),
            scores.max(),
            100
        )

        best_f1 = -1

        best_threshold = 0

        for threshold in thresholds:

            prediction = (
                scores < threshold
            ).astype(int)

            current_f1 = f1_score(
                y_val,
                prediction,
                zero_division=0
            )

            if current_f1 > best_f1:

                best_f1 = current_f1

                best_threshold = threshold

        self.threshold = best_threshold

        print(f"Best Threshold : {best_threshold:.5f}")

        print(f"Validation F1  : {best_f1:.4f}")

    # --------------------------------------------------
    # Prediction
    # --------------------------------------------------

    def predict(self, X):

        scores = self.model.decision_function(X)

        return (
            scores < self.threshold
        ).astype(int)

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save(self, path="../models/oneclass_svm.pkl"):

        joblib.dump(

            {

                "model": self.model,

                "threshold": self.threshold

            },

            path

        )

        print(f"Model saved -> {path}")

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    @classmethod
    def load(cls, path="../models/oneclass_svm.pkl"):

        data = joblib.load(path)

        obj = cls()

        obj.model = data["model"]

        obj.threshold = data["threshold"]

        return obj